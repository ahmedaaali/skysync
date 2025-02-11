import os
import sys
import time
import logging
import requests
import json
import getpass
import curses
from curses import wrapper
from dotenv import load_dotenv

from dronekit import connect
from pymavlink import mavutil

load_dotenv()

SERVER_URL = os.getenv("SERVER_URL", "https://example.com")
DRONE_CONNECTION = os.getenv("DRONE_UDP_CONNECTION", "udp:192.168.1.10:14550")
CERT_PATH = os.getenv("CERT_PATH", "/home/user/cert.pem")  # if needed

logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

# MAV_CMD constants
MAV_CMD_NAV_LOITER_UNLIM = 17
MAV_CMD_DO_JUMP = 177
MAV_CMD_DO_SET_MODE = 176
MAV_CMD_COMPONENT_ARM_DISARM = 400
MAV_CMD_DO_SET_PARAMETER = 180
MAV_CMD_DO_REPOSITION = 192

# Custom parameters for commands
RTL_MODE_PARAM2 = 5
EMERGENCY_LAND_PARAM2 = 21196
CAMERA_INTERVAL_PARAM1 = 999

class TerminalInterface:
    def __init__(self):
        self.token = None
        self.vehicle = None

    def login(self):
        # Prompt user for credentials
        print("=== SkySync Terminal Interface ===")
        print("Please login to the backend server:")
        username = input("Username: ")
        password = getpass.getpass("Password: ")

        # Attempt login
        data = {'username': username, 'password': password}
        try:
            resp = requests.post(f"{SERVER_URL}/login", json=data, verify=CERT_PATH, timeout=10)
            if resp.status_code == 200:
                result = resp.json()
                self.token = result.get('token')
                if self.token:
                    print("Login successful!")
                    return True
                else:
                    print("Login failed: No token received.")
                    return False
            else:
                print(f"Login failed: {resp.status_code} {resp.text}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to server: {e}")
            return False

    def connect_drone(self):
        print("Connecting to the drone...")
        self.vehicle = connect(DRONE_CONNECTION, wait_ready=True)
        print("Connected to drone.")

    def send_command_long(self, command, param1=0, param2=0, param3=0, param4=0, param5=0, param6=0, param7=0):
        # Construct the COMMAND_LONG message
        msg = self.vehicle.message_factory.command_long_encode(
            0, 0,    # target system, target component
            command,  # command
            0,        # confirmation
            param1,
            param2,
            param3,
            param4,
            param5,
            param6,
            param7
        )
        self.vehicle.send_mavlink(msg)
        self.vehicle.flush()
        print(f"Sent MAV_CMD: {command} with params {[param1, param2, param3, param4, param5, param6, param7]}")

    def menu(self):
        while True:
            print("\n=== Main Menu ===")
            print("1. Start Mission (assumes mission already loaded on drone's side)")
            print("2. Pause Mission")
            print("3. Resume Mission")
            print("4. Skip Next Waypoint")
            print("5. Return to Launch (RTL)")
            print("6. Land Now (Emergency)")
            print("7. Change Camera Interval")
            print("8. Manual Control (Keyboard)")
            print("9. Exit")
            choice = input("Select an option: ")

            if choice == '1':
                self.start_mission()
            elif choice == '2':
                self.pause_mission()
            elif choice == '3':
                self.resume_mission()
            elif choice == '4':
                self.skip_waypoint()
            elif choice == '5':
                self.return_to_launch()
            elif choice == '6':
                self.land_now()
            elif choice == '7':
                self.change_camera_interval()
            elif choice == '8':
                self.manual_control_mode()
            elif choice == '9':
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please try again.")

    def start_mission(self):
        # Starting mission might mean switching the drone to GUIDED mode and let it follow waypoints
        # If your logic requires a specific command, send it. 
        # If the drone code reads from command_handler that "MISSION" is default, maybe no command needed
        # But let's say we do MAV_CMD_DO_SET_MODE to guided or no command if mission is default state
        print("Starting mission... (In current design, mission starts by default if no overrides)")
        # Optionally send a command to "resume_mission" logic if needed
        self.send_command_long(MAV_CMD_DO_SET_MODE, param1=1, param2=4) # param2=4 might represent GUIDED mode in some logic
        print("Mission start requested.")

    def pause_mission(self):
        # MAV_CMD_NAV_LOITER_UNLIM to pause mission
        self.send_command_long(MAV_CMD_NAV_LOITER_UNLIM)
        print("Mission paused.")

    def resume_mission(self):
        # Resuming mission might mean sending mode back to GUIDED or removing pause flag.
        # Possibly send MAV_CMD_DO_SET_MODE with param2=4 for GUIDED
        self.send_command_long(MAV_CMD_DO_SET_MODE, param1=1, param2=4)
        print("Mission resumed.")

    def skip_waypoint(self):
        self.send_command_long(MAV_CMD_DO_JUMP, param1=1, param2=1) # param1=1 jump to next Wp or skip next?
        print("Skip waypoint requested.")

    def return_to_launch(self):
        self.send_command_long(MAV_CMD_DO_SET_MODE, param2=RTL_MODE_PARAM2)
        print("RTL requested.")

    def land_now(self):
        self.send_command_long(MAV_CMD_COMPONENT_ARM_DISARM, param2=EMERGENCY_LAND_PARAM2)
        print("Emergency land requested.")

    def change_camera_interval(self):
        new_interval = input("Enter new camera interval in seconds: ")
        try:
            interval = int(new_interval)
            if interval > 0:
                self.send_command_long(MAV_CMD_DO_SET_PARAMETER, param1=CAMERA_INTERVAL_PARAM1, param2=interval)
                print(f"Camera interval change requested to {interval} sec.")
            else:
                print("Invalid interval. Must be > 0.")
        except ValueError:
            print("Invalid input. Must be an integer.")

    def manual_control_mode(self):
        print("Entering manual control mode. Use arrow keys to move drone, 'q' to quit.")
        print("This sends MAV_CMD_DO_REPOSITION commands to shift drone's position slightly.")
        # We switch drone to GUIDED mode for reposition commands
        self.send_command_long(MAV_CMD_DO_SET_MODE, param1=1, param2=4)
        time.sleep(1)

        def curses_main(stdscr):
            stdscr.nodelay(True)
            stdscr.keypad(True)
            stdscr.clear()
            stdscr.addstr(0, 0, "Manual Control Mode:\nUse arrow keys to move drone.\n'q' to quit.\n")

            # Assume each arrow key press repositions the drone by a small offset
            # param5, param6 = Lat, Long offset? Actually DO_REPOSITION sets LAT/LON/ALT if we had them.
            # For simplicity, let's just do small offsets. In reality, you'd get current lat/lon and offset them slightly.
            
            offset = 0.00001 # small lat/lon offset
            current_lat = self.vehicle.location.global_relative_frame.lat or 0.0
            current_lon = self.vehicle.location.global_relative_frame.lon or 0.0
            current_alt = self.vehicle.location.global_relative_frame.alt or 10.0

            while True:
                try:
                    key = stdscr.getch()
                    if key == -1:
                        # no input
                        time.sleep(0.1)
                        continue
                    elif key == ord('q'):
                        stdscr.addstr(5, 0, "Exiting manual control mode...")
                        stdscr.refresh()
                        time.sleep(1)
                        break
                    elif key == curses.KEY_UP:
                        current_lat += offset
                    elif key == curses.KEY_DOWN:
                        current_lat -= offset
                    elif key == curses.KEY_LEFT:
                        current_lon -= offset
                    elif key == curses.KEY_RIGHT:
                        current_lon += offset
                    
                    # Send DO_REPOSITION command
                    # MAV_CMD_DO_REPOSITION param5=lat, param6=lon, param7=alt
                    msg = self.vehicle.message_factory.command_long_encode(
                        0, 0,
                        MAV_CMD_DO_REPOSITION,
                        0,
                        0,0,0,0,
                        current_lat,
                        current_lon,
                        current_alt
                    )
                    self.vehicle.send_mavlink(msg)
                    self.vehicle.flush()
                    stdscr.addstr(6, 0, f"Set pos: lat={current_lat}, lon={current_lon}, alt={current_alt}")
                    stdscr.clrtoeol()
                    stdscr.refresh()

                except Exception as e:
                    stdscr.addstr(7, 0, f"Error: {e}")
                    stdscr.refresh()
                    time.sleep(1)

        wrapper(curses_main)
        print("Manual control mode exited. Returning to main menu...")

def main():
    app = TerminalInterface()
    if not app.login():
        sys.exit("Login failed, cannot proceed.")

    app.connect_drone()
    app.menu()

    if app.vehicle is not None:
        app.vehicle.close()

if __name__ == "__main__":
    main()

