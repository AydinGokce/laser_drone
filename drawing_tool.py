from tkinter import Tk, Canvas, Button
from tkinter.colorchooser import askcolor
from utils import map_points_to_angles

class DroneCanvas(object):
    DEFAULT_PEN_SIZE = 0.5
    DEFAULT_COLOR = 'black'
    CANVAS_WIDTH = 1000
    CANVAS_HEIGHT = 300
    PHYSICAL_WIDTH = 300 #mm
    PHYSICAL_HEIGHT = 100 #mm
    
    def __init__(self):
        self.root = Tk()
        
        self.strokes = []
        self.points = []
        
        self.burn_button = Button(self.root, text='burn', command=self.burn)
        self.burn_button.grid(row=0, column=0)
        self.clear_button = Button(self.root, text='clear', command=self.clear)
        self.clear_button.grid(row=0, column=1)
        
        self.c = Canvas(self.root, bg='white', width=self.CANVAS_WIDTH, height=self.CANVAS_HEIGHT)
        self.c.grid(row=1, columnspan=2)
        self.setup()
        self.root.mainloop()
        
    def setup(self):
        self.old_x = None
        self.old_y = None
        self.line_width = self.DEFAULT_PEN_SIZE
        self.color = self.DEFAULT_COLOR
        self.c.bind('<B1-Motion>', self.paint)
        self.c.bind('<ButtonRelease-1>', self.reset)
        
    def paint(self, event):
        self.line_width = self.DEFAULT_PEN_SIZE
        paint_color = 'black'
        if self.old_x and self.old_y:
            self.c.create_line(self.old_x, self.old_y, event.x, event.y,
                               width=self.line_width, fill=paint_color,
                               capstyle='round', smooth=True)
            
        self.points.append((event.x, event.y))
        self.old_x = event.x
        self.old_y = event.y
        
    def reset(self, event):
        self.old_x, self.old_y = None, None
        self.strokes.append(self.points)
        self.points = []
        
    def burn(self):
        print(f"strokes: {len(self.strokes)}")
        angles = map_points_to_angles(self.strokes, self.CANVAS_WIDTH, self.CANVAS_HEIGHT, self.PHYSICAL_WIDTH, self.PHYSICAL_HEIGHT, 100)
        print(angles)
        
    def clear(self):
        self.c.delete('all')
        self.strokes = []
        self.points = []
        
if __name__ == '__main__':
    DroneCanvas()