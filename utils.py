import math
from adafruit_servokit import ServoKit
import time
kit = ServoKit(channels=16)

def map_points_to_angles(strokes, canvas_width, canvas_height, physical_width, physical_height, distance_to_wall):
    
    angles = []
    for stroke in strokes:
        for (x, y) in stroke:
            
            # convert absolute x, y to offset from center
            center_offset_x = x - canvas_width / 2
            center_offset_y = y - canvas_height / 2
            
            # convert pixel offset from the center to physical offset in mm
            physical_offset_x = center_offset_x * physical_width / canvas_width
            physical_offset_y = center_offset_y * physical_height / canvas_height
            
            # convert physical offset to angle
            angle_x = math.atan(physical_offset_x / distance_to_wall)
            angle_y = math.atan(physical_offset_y / distance_to_wall)
            
            # convert angle to servo angle
            servo_angle_x = angle_x * 180 / math.pi
            servo_angle_y = angle_y * 180 / math.pi
            
            angles.append((servo_angle_x, servo_angle_y))

    return angles
            
def write_angles_to_servo(angles, wait_duration=0.01):
    for stroke in angles:
        for (thx, thy) in stroke:
            kit.servo[0].angle = thx
            kit.servo[1].angle = thy
            time.sleep(wait_duration)
            
            