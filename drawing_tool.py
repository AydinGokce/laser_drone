from tkinter import Tk, Canvas, Button
from tkinter.colorchooser import askcolor
from servo_writer import ServoWriter
import numpy as np
class DroneCanvas(object):
    DEFAULT_PEN_SIZE = 0.5
    DEFAULT_COLOR = 'black'
    CANVAS_WIDTH = 1000
    CANVAS_HEIGHT = 300
    PHYSICAL_WIDTH = 225 #mm
    PHYSICAL_HEIGHT = 140 #mm
    
    def __init__(self):
        self.root = Tk()
        self.writer = ServoWriter()
        
        self.strokes = []
        self.points = []
        
        self.burn_button = Button(self.root, text='burn', command=self.burn)
        self.burn_button.grid(row=0, column=0)
        self.clear_button = Button(self.root, text='clear', command=self.clear)
        self.clear_button.grid(row=0, column=1)
        self.toggle_mode_button = Button(self.root, text='toggle mode', command=self.toggle_mode)
        self.toggle_mode_button.grid(row=0, column=2)
        
        self.c = Canvas(self.root, bg='white', width=self.CANVAS_WIDTH, height=self.CANVAS_HEIGHT)
        self.c.grid(row=1, columnspan=3, sticky='nsew') 
        
        self.setup()
        self.root.mainloop()
        
    def setup(self):
        self.old_x = None
        self.old_y = None
        self.curr_line_x = None
        self.curr_line_y = None
        self.curr_line_obj = None
        self.draw_mode = "scribble" #line
        
        self.line_width = self.DEFAULT_PEN_SIZE
        self.color = self.DEFAULT_COLOR
        self.c.bind('<Button 1>', self.paint)
        self.c.bind('<B1-Motion>', self.visualize)
        self.c.bind('<ButtonRelease-1>', self.reset)
        
    def toggle_mode(self):
        if self.draw_mode == 'scribble':
            self.draw_mode = 'line'
        else:
            self.draw_mode = 'scribble'
    
    def paint(self, event):
        self.old_x = event.x
        self.old_y = event.y
    
    def visualize(self, event):
        if self.draw_mode == 'line':
            if self.curr_line_obj is not None:
                self.c.delete(self.curr_line_obj)
            
            if self.old_x and self.old_y:
                self.curr_line_obj = self.c.create_line(self.old_x, self.old_y, event.x, event.y,
                                width=self.line_width, fill='black',
                                capstyle='round', smooth=True)
                self.curr_line_x = event.x
                self.curr_line_y = event.y
        else:
            if self.old_x and self.old_y:
                self.c.create_line(self.old_x, self.old_y, event.x, event.y, 
                                   width=self.DEFAULT_PEN_SIZE, fill='black',
                                   capstyle='round', smooth=True)
            self.points.append((event.x, event.y))
            self.old_x = event.x
            self.old_y = event.y
        print("moving")
    
    def reset(self, event):
        if self.draw_mode == 'line':
            distance = np.sqrt((self.curr_line_x - self.old_x)**2 + (self.curr_line_y - self.old_y)**2)
            pixels_per_step = 2
            line_x = np.linspace(self.old_x, self.curr_line_x, num=int(distance) // pixels_per_step)
            line_y = np.linspace(self.old_y, self.curr_line_y, num=int(distance) // pixels_per_step)
            self.points = np.c_[line_x, line_y]
            self.curr_line_obj, self.curr_line_x, self.curr_line_y = None, None, None
        
        self.old_x, self.old_y = None, None
        self.strokes.append(self.points)
        self.points = []
        
    def burn(self):
        print(f"strokes: {len(self.strokes)}")
        
        angles = self.writer.map_points_to_angles(self.strokes, self.CANVAS_WIDTH, self.CANVAS_HEIGHT, self.PHYSICAL_WIDTH, self.PHYSICAL_HEIGHT, 300)
        try:
            self.writer.write_angles_to_servo(angles)
        except Exception as e:
            self.writer.turn_laser_off()
            raise e
        print("##### DONE #####")
        
    def clear(self):
        self.c.delete('all')
        self.strokes = []
        self.points = []
        
if __name__ == '__main__':
    DroneCanvas()