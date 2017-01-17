# Imports
import os
import re
import sys
import json
import tkinter
import math
from tkinter import filedialog
import struct

# Configuration

# The Item1001Tracker class
class Item1001Tracker(tkinter.Frame):
    def __init__(self, parent):
        # Class variables
        self.file_array_position = 0
        self.items_remaining_list = []
        self.items_found_from_file = []
        self.version = ""
        self.items_total = 0
        self.offset_start = 0
        self.offset_end = 0
        self.game_data_file = ""
        self.all_item_ids = []

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
        for item_id in all_item_ids:
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

    # on_mousewheel - Code taken from: http://stackoverflow.com/questions/17355902/python-tkinter-binding-mousewheel-to-scrollbar
    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')

    def drawUI(self):
        items_remaining = "{} items remaining in {}".format(str(len(self.items_remaining_list)), self.version) 
        self.left_label.configure(text=items_remaining)

        self.canvas.delete("all")

        x = 34  # We start an extra 2 pixels to the right so that the left border will show
        y = 34  # We start an extra 2 pixels lower so that the top border will show
        draw_x = x
        draw_y = y
        draw_w = 64
        window_width = self.window.winfo_width()
        columns = int(math.floor(window_width / (draw_w + 1)))

        for item_id in self.items_remaining_list:
            self.canvas.create_image((draw_x, draw_y), image=self.photos[item_id])
            self.canvas.create_rectangle(draw_x - 32, draw_y - 32, draw_x + 32, draw_y + 32)

            draw_x += draw_w
            if draw_x == x + (draw_w * columns):
                draw_x = x
                draw_y += draw_w

    def parse_save(self):
        with open(self.game_data_file, 'rb') as file:
            content = file.read()
        self.version = struct.unpack('<b', content[12:13])[0]
        # Find version from save file and assign values accordingly
        if str(self.version) == '54':
            self.item_total= 341
            self.offset_start = 661
            self.offset_end = self.offset_start + self.item_total
        elif str(self.version) == '56':
            self.version = "Afterbirth"
            self.item_total= 441
            self.offset_start = 1041
            self.offset_end = self.offset_start + self.item_total
        elif str(self.version) == '57':
            self.version = "Afterbirth+"
            self.item_total= 510
            self.offset_start = 1041
            self.offset_end = self.offset_start + self.item_total
        else:
            print("what are you?")
            sys.exit(0)
        #pull all items from the save file
        self.items_from_file = struct.unpack('b'*self.item_total, content[self.offset_start:self.offset_end])

        #figure out if we've touched the item -- some items may need to be skipped because the IDs aren't valid IE: itemID 43 doesn't exist
        

        # Redraw the UI
        self.drawUI()

        # Schedule another log parse in 0.25 seconds
        self.parent.after(250, self.parseLog)


# The main program
if __name__ == '__main__':
    # Initialize the root GUI
    root = tkinter.Tk()
    root.withdraw()  # Hide the GUI
    self.game_data_file = filedialog.askopenfilename() #Ask for the game file
    
    # Show the GUI
    Item1001Tracker(root)
    root.mainloop()
