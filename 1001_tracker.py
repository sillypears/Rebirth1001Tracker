# Imports
import os
import re
import sys
import json
import tkinter
import math
from tkinter import filedialog
import time
import struct

# Configuration
bad_ids = [43, 59, 61, 235, 263] #ids not used, need offset

# The Item1001Tracker class
class Item1001Tracker(tkinter.Frame):
    def __init__(self, parent):
        # Class variables
        self.file_array_position = 0
        self.items_remaining_list = []
        self.items_found_from_file = {}
        self.version = ""
        self.item_total = 0
        self.offset_start = 0
        self.offset_end = 0
        self.game_data_file = game_data_file
        self.all_item_ids = []
        self.items_from_file = []
        # Welcome message
        print('Starting 1001% item tracker...')

        # Get a sorted list of all item IDs
        with open('items.json', 'r') as items_file:
            items_json = json.load(items_file)
        for item_id, item_details in items_json.items():
            self.all_item_ids.append(item_id)
        self.all_item_ids.sort()
        
        
        # Initialize the photo dictionary
        self.photos = {}
        for item_id in self.all_item_ids:
            image_path = 'collectibles/collectibles_' + item_id + '.png'
            self.photos[item_id] = tkinter.PhotoImage(file=image_path)
        
        # Initialize a new GUI window
        self.parent = parent
        self.window = tkinter.Toplevel(self.parent)
        self.window.title('1001% Tracker')  # Set the GUI title
        self.icon = tkinter.PhotoImage(file='collectibles/collectibles_076.png')
        self.window.tk.call('wm', 'iconphoto', self.window._w, self.icon)  # Set the GUI icon
        self.window.protocol('WM_DELETE_WINDOW', sys.exit)  # Close the main GUI when the window is closed

        # Initialize the label and the canvas
        self.left_label = tkinter.Label(self.window, font='font 20 bold')
        self.left_label.pack(fill=tkinter.X, expand=tkinter.NO)
        self.canvas = tkinter.Canvas(self.window, width=646)  # Just enough width to make 10 columns
        self.canvas.pack(fill=tkinter.BOTH, expand=tkinter.YES)
        self.canvas.bind('<Configure>', lambda event: self.drawUI())

        # Define keyboard bindings
        self.window.bind('<MouseWheel>', self.on_mousewheel)
        self.window.bind('<Home>', lambda event: self.canvas.yview_moveto(0))
        self.window.bind('<End>', lambda event: self.canvas.yview_moveto(1))
        self.window.bind('<Prior>', lambda event: self.canvas.yview_scroll(-1, 'pages'))  # PgUp
        self.window.bind('<Next>', lambda event: self.canvas.yview_scroll(1, 'pages'))  # PgDn

        # Initialization
        self.drawUI()
        self.parse_save()

        
        #while True:
        #    self.parse_save()
        #    print("sleeping")
        #    time.sleep(5)


    # on_mousewheel - Code taken from: http://stackoverflow.com/questions/17355902/python-tkinter-binding-mousewheel-to-scrollbar
    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')

    def drawUI(self):
        items_remaining = "{} items remaining in {}".format(self.item_total-(len(self.items_found_from_file)+len(bad_ids)), self.version) 
        self.left_label.configure(text=items_remaining)

        self.canvas.delete("all")

        x = 34  # We start an extra 2 pixels to the right so that the left border will show
        y = 34  # We start an extra 2 pixels lower so that the top border will show
        draw_x = x
        draw_y = y
        draw_w = 64
        window_width = self.window.winfo_width()
        columns = int(math.floor(window_width / (draw_w + 1)))
        
        #print out the items left to touch not found in the file and are valid item IDs
        for item_id in range(1,len(self.items_from_file)+1):
            if item_id not in sorted(self.items_found_from_file.keys()) and item_id not in bad_ids:
                self.canvas.create_image((draw_x, draw_y), image=self.photos["{0:03d}".format(item_id)])
                self.canvas.create_rectangle(draw_x - 32, draw_y - 32, draw_x + 32, draw_y + 32)

                draw_x += draw_w
                if draw_x == x + (draw_w * columns):
                    draw_x = x
                    draw_y += draw_w

    def parse_save(self):
        with open(game_data_file, 'rb') as file:
            content = file.read()

        v = struct.unpack('<b', content[12:13])[0] #get version number from file
        
        #assign values based on version number
        if str(v) == '54':
            self.version = "Rebirth"
            self.item_total= 346
            self.offset_start = 676 #0x2A4-0x3FD
            self.offset_end = self.offset_start + self.item_total
        elif str(v) == '56':
            self.version = "Afterbirth"
            self.item_total= 441
            self.offset_start = 1042 #0x412-0x
            self.offset_end = self.offset_start + self.item_total
        elif str(v) == '57':
            self.version = "Afterbirth+"
            self.item_total= 510 
            self.offset_start = 1233 #0x4D1-0x6CE
            self.offset_end = self.offset_start + self.item_total
        else:
            print("what are you?")
            sys.exit(0)
        
        #pull all items from the save file
        self.items_from_file = struct.unpack('b'*self.item_total, content[self.offset_start:self.offset_end])
        
        for i in range(0,self.item_total):
            try:
                if self.items_from_file[i] and i+1 not in bad_ids:
                    self.items_found_from_file[i+1] = self.all_item_ids[i]
            except Exception as e:
                print(e, i)

        # Redraw the UI
        self.drawUI()

        # Schedule another log parse in 1 second
        self.parent.after(1000, self.parse_save)

# The main program
if __name__ == '__main__':
    # Initialize the root GUI
    root = tkinter.Tk()
    root.withdraw()  # Hide the GUI
    game_data_file = filedialog.askopenfilename() #Ask for the game file
    
    # Show the GUI
    Item1001Tracker(root)
    root.mainloop()
    

