import logging

MAV_CMD_NAV_LOITER_UNLIM = 17
MAV_CMD_DO_JUMP = 177
MAV_CMD_DO_SET_MODE = 176
MAV_CMD_COMPONENT_ARM_DISARM = 400
MAV_CMD_DO_SET_PARAMETER = 180

class CommandHandler:
    def __init__(self, vehicle):
        self.vehicle = vehicle
        self.rc_override_active = False
        self.gcs_override_active = False
        self.current_command = "MISSION"

        self.pause_mission = False
        self.skip_waypoint = False
        self.return_to_launch = False
        self.land_now = False
        self.change_camera_interval = None

        self.vehicle.add_message_listener('COMMAND_LONG', self.command_long_callback)

    def command_long_callback(self, name, message):
        cmd = message.command
        param1 = message.param1
        param2 = message.param2

        if cmd == MAV_CMD_NAV_LOITER_UNLIM:
            logging.info("GCS Command: NAV_LOITER_UNLIM (pause mission).")
            self.pause_mission = True
        elif cmd == MAV_CMD_DO_JUMP:
            logging.info("GCS Command: DO_JUMP (skip next waypoint).")
            self.skip_waypoint = True
        elif cmd == MAV_CMD_DO_SET_MODE:
            if param2 == 5:
                logging.info("GCS Command: DO_SET_MODE => RTL.")
                self.return_to_launch = True
        elif cmd == MAV_CMD_COMPONENT_ARM_DISARM:
            if int(param2) == 21196:
                logging.info("GCS Command: emergency land.")
                self.land_now = True
        elif cmd == MAV_CMD_DO_SET_PARAMETER:
            if int(param1) == 999:
                new_interval = int(param2)
                if new_interval > 0:
                    logging.info(f"Camera interval changed to {new_interval}s by GCS.")
                    self.change_camera_interval = new_interval

    def update_rc_status(self):
        ch7 = self.vehicle.channels.get('7', 1500)
        if ch7 > 1800:
            self.rc_override_active = True
            self.current_command = "RC_OVERRIDE"
        else:
            self.rc_override_active = False

    def process_gcs_commands(self):
        pass

    def get_active_command(self):
        self.update_rc_status()
        self.process_gcs_commands()

        if self.rc_override_active:
            return "RC_OVERRIDE"
        if self.return_to_launch:
            return "RTL"
        if self.land_now:
            return "LAND"
        if self.pause_mission:
            return "PAUSE"
        return "MISSION"

    def clear_gcs_flags(self):
        self.skip_waypoint = False
