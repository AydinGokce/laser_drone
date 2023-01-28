import math
from adafruit_servokit import ServoKit
import time
import board
import busio
import adafruit_pca9685


class ServoWriter:
    def __init__(self):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.pca = adafruit_pca9685.PCA9685(self.i2c)
        self.kit = ServoKit(channels=16)
        self.pca.frequency = 60
        
        self.uptime = 0
        self.max_uptime = 10
        self.cooldown_period = 25
        
    def map_points_to_angles(self, strokes, canvas_width, canvas_height, physical_width, physical_height, distance_to_wall, angle_offset=90):
        
        angles = []
        for stroke in strokes:
            angle_stroke = []
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
                servo_angle_x = angle_offset + (angle_x * 180 / math.pi)
                servo_angle_y = angle_offset - (angle_y * 180 / math.pi)
                
                angle_stroke.append((servo_angle_x, servo_angle_y))
            angles.append(angle_stroke)

        return angles
        
    def reset_position(self):
        self.kit.servo[0].angle = 90
        self.kit.servo[1].angle = 90
    
    def visualize_bounds(self, canvas_width, canvas_height, physical_width, physical_height, distance_to_wall):
        pts = self.map_points_to_angles([
            [
              (0, 0),
                (canvas_width, 0),
                (canvas_width, canvas_height),
                (0, canvas_height),
                (0, 0)
            ]
        ], canvas_width, canvas_height, physical_width, physical_height, distance_to_wall)
        
        self.write_angles_to_servo(pts, point_interval=0.3)
    
    def write_angles_to_servo(self, angles, point_interval=0.6):
        self.reset_position()
        
        for stroke in angles:
            self.turn_laser_on()
            for i, (thx, thy) in enumerate(stroke):
                print(f"writing angle ({thx}, {thy})")
                self.kit.servo[0].angle = thx
                self.kit.servo[1].angle = thy
                time.sleep(point_interval)
                self.uptime += point_interval
                if self.uptime > self.max_uptime:
                    self.turn_laser_off()
                    time.sleep(self.cooldown_period)
                    self.uptime =0
                    self.turn_laser_on()
                    
            self.turn_laser_off()

    def turn_laser_on(self, laser_channel = 2):
        self.pca.channels[laser_channel].duty_cycle = 0xffff
        
    def turn_laser_off(self, laser_channel = 2):
        self.pca.channels[laser_channel].duty_cycle = 0x0
                