import time
import math
import logging
from dronekit import VehicleMode, LocationGlobalRelative
from config import Config

class DroneController:
    def __init__(self, vehicle, command_handler):
        self.vehicle = vehicle
        self.command_handler = command_handler
        self.mission_paused = False

    def arm_and_takeoff(self, target_alt):
        while not self.vehicle.is_armable:
            logging.info("Waiting for vehicle to become armable...")
            time.sleep(2)

        self.vehicle.mode = VehicleMode("GUIDED")
        self.vehicle.armed = True
        while not self.vehicle.armed:
            logging.info("Waiting for arm...")
            time.sleep(1)

        logging.info(f"Taking off to {target_alt}m...")
        self.vehicle.simple_takeoff(target_alt)
        while True:
            current_alt = self.get_altitude()
            if current_alt >= target_alt * 0.95:
                logging.info("Reached target altitude")
                break
            # Check override commands even during takeoff
            if self.command_handler.get_active_command() != "MISSION":
                self.handle_override()
                break
            time.sleep(2)

    def follow_waypoints(self, waypoints):
        waypoint_index = 0
        total_wps = len(waypoints)

        while waypoint_index < total_wps:
            active_cmd = self.command_handler.get_active_command()

            if active_cmd == "RC_OVERRIDE":
                self.handle_override()
                return
            if active_cmd == "PAUSE":
                self.pause_mission()
                continue
            if active_cmd == "RTL":
                self.set_mode("RTL")
                return
            if active_cmd == "LAND":
                self.set_mode("LAND")
                return

            lat, lon, alt = waypoints[waypoint_index]
            target_wp = LocationGlobalRelative(lat, lon, alt)
            logging.info(f"Going to waypoint {waypoint_index + 1}/{total_wps}")
            self.vehicle.simple_goto(target_wp, groundspeed=3)

            reached = self.wait_for_reach(target_wp)
            if not reached:
                logging.warning("Failed to reach waypoint due to override or battery issue.")
                return

            # Check if GCS asked to skip next waypoint
            if self.command_handler.skip_waypoint:
                logging.info("Skipping next waypoint as per GCS request.")
                waypoint_index += 2  # skip the next one
                self.command_handler.skip_waypoint = False
            else:
                waypoint_index += 1

            # Battery check
            if (self.vehicle.battery.voltage
                and self.vehicle.battery.voltage < Config.BATTERY_LOW_THRESHOLD):
                logging.warning("Battery low! Returning to launch.")
                self.set_mode("RTL")
                return

        # After all waypoints done
        logging.info("All waypoints completed. Returning to launch.")
        self.set_mode("RTL")

    def pause_mission(self):
        self.mission_paused = True
        logging.info("Mission paused. Holding position in LOITER mode.")
        self.set_mode("LOITER")
        # Wait until mission resumes or another command
        while True:
            cmd = self.command_handler.get_active_command()
            if cmd == "MISSION":
                self.mission_paused = False
                logging.info("Mission resumed.")
                self.set_mode("GUIDED")
                break
            elif cmd in ["RC_OVERRIDE", "RTL", "LAND"]:
                self.handle_override()
                break
            time.sleep(2)

    def handle_override(self):
        cmd = self.command_handler.get_active_command()
        if cmd == "RC_OVERRIDE":
            logging.info("RC override active: Following RC pilot commands.")
            # Could switch to LOITER mode for safety
            self.set_mode("LOITER")
            while self.command_handler.get_active_command() == "RC_OVERRIDE":
                time.sleep(2)
        elif cmd == "RTL":
            self.set_mode("RTL")
        elif cmd == "LAND":
            self.set_mode("LAND")

    def wait_for_reach(self, target_wp):
        while True:
            cmd = self.command_handler.get_active_command()
            if cmd != "MISSION":
                return False
            dist = self.get_distance_to_waypoint(target_wp)
            if dist < Config.WAYPOINT_REACH_THRESHOLD:
                logging.info("Waypoint reached.")
                return True
            # Battery check mid-flight
            if (self.vehicle.battery.voltage
                and self.vehicle.battery.voltage < Config.BATTERY_LOW_THRESHOLD):
                return False
            time.sleep(2)

    def get_distance_to_waypoint(self, target_wp):
        lat = self.vehicle.location.global_relative_frame.lat
        lon = self.vehicle.location.global_relative_frame.lon
        dlat = lat - target_wp.lat
        dlon = lon - target_wp.lon
        return math.sqrt((dlat*111139)**2 + (dlon*111139)**2)

    def get_altitude(self):
        return self.vehicle.location.global_relative_frame.alt or 0.0

    def set_mode(self, mode_name):
        self.vehicle.mode = VehicleMode(mode_name)
        for _ in range(10):
            if self.vehicle.mode.name == mode_name:
                break
            time.sleep(0.5)
