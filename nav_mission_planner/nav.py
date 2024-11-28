from dronekit import connect, VehicleMode, LocationGlobalRelative
import time
import cv2

# Connect to the vehicle
vehicle = connect('127.0.0.1:14550', wait_ready=True)

def arm_and_takeoff(altitude):
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    while not vehicle.armed:
        time.sleep(1)
    vehicle.simple_takeoff(altitude)

def goto_waypoint(lat, lon, alt):
    waypoint = LocationGlobalRelative(lat, lon, alt)
    vehicle.simple_goto(waypoint)

def capture_photo(image_path, geolocation):
    # Camera setup and photo capture
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    if ret:
        # Save photo with geolocation metadata in JSON or CSV
        cv2.imwrite(image_path, frame)
        with open("geolocation_data.csv", "a") as f:
            f.write(f"{image_path},{geolocation}\n")
    cap.release()

# Main mission sequence
arm_and_takeoff(10)  # Altitude in meters

waypoints = [(lat1, lon1, alt), (lat2, lon2, alt)]
for waypoint in waypoints:
    goto_waypoint(*waypoint)
    time.sleep(5)  # Wait to reach the waypoint
    capture_photo("photo_at_waypoint.jpg", waypoint)

