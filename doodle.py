import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, messagebox, PhotoImage
from PIL import Image, ImageTk, ImageDraw, ImageColor
import os
import copy
import sys


class DoodleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Doodle")

        # Change the icon path from .png to .ico
        icon_path = "doodle_icon.ico"  # Default for script execution
        if getattr(sys, 'frozen', False):  # Running as an .exe
            icon_path = os.path.join(sys._MEIPASS, "doodle_icon.ico")

        try:
            self.root.iconbitmap(icon_path)  # Use iconbitmap instead of iconphoto for .ico files
        except Exception as e:
            print("Icon loading failed:", e)

        self.root.configure(bg="#333333")
        
        # Set initial window size and position
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_width = 1000
        window_height = 900
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
            
        # Configure app theme
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TButton', background='#444444', foreground='#DDDDDD', 
                            font=('Courier', 10, 'bold'), relief='flat')
        self.style.map('TButton', background=[('active', '#555555')])
        self.style.configure('TRadiobutton', background='#333333', foreground='#DDDDDD', 
                            font=('Courier', 10))
        self.style.configure('TLabel', background='#333333', foreground='#DDDDDD', 
                            font=('Courier', 10, 'bold'))
        self.style.configure('TFrame', background='#333333')
            
        # Canvas dimensions
        self.canvas_width = 800
        self.canvas_height = 800
            
        # Variables
        self.current_color = "#000000"  # Default: Black
        self.brush_size = 5  # Default: Medium
        self.mode = "brush"  # Default: Brush mode
        self.old_x = None
        self.old_y = None
        self.selected_color_button = None  # Track the currently selected color button
            
        # Initialize the PIL image with transparency
        self.pil_image = Image.new("RGBA", (self.canvas_width, self.canvas_height), (255, 255, 255, 0))
        self.pil_draw = ImageDraw.Draw(self.pil_image)
            
        # Undo/Redo stacks
        self.history_stack = []
        self.redo_stack = []
            
        # Create the interface
        self.create_widgets()
            
        # Save initial empty state - MOVED TO AFTER create_widgets
        self.save_state()
            
        # Bind keyboard shortcuts
        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<Control-y>", lambda e: self.redo())
            
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
        # Left panel for tools
        tools_frame = ttk.Frame(main_frame)
        tools_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)
            
        # Tools label
        ttk.Label(tools_frame, text="TOOLS").pack(pady=(0, 10))
            
        # Tool selection
        self.brush_button = ttk.Button(tools_frame, text="BRUSH", command=lambda: self.set_mode("brush"))
        self.brush_button.pack(fill=tk.X, pady=2)
            
        self.eraser_button = ttk.Button(tools_frame, text="ERASER", command=lambda: self.set_mode("eraser"))
        self.eraser_button.pack(fill=tk.X, pady=2)
        
        # Add Fill Shape tool
        self.fill_shape_button = ttk.Button(tools_frame, text="FILL SHAPE", command=lambda: self.set_mode("fill_shape"))
        self.fill_shape_button.pack(fill=tk.X, pady=2)
        
        # Add Background Fill tool
        self.bg_fill_button = ttk.Button(tools_frame, text="FILL BACKGROUND", command=lambda: self.set_mode("bg_fill"))
        self.bg_fill_button.pack(fill=tk.X, pady=2)
            
        # Undo/Redo buttons
        undo_redo_frame = ttk.Frame(tools_frame)
        undo_redo_frame.pack(fill=tk.X, pady=(10, 2))
            
        self.undo_button = ttk.Button(undo_redo_frame, text="UNDO", command=self.undo)
        self.undo_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))
            
        self.redo_button = ttk.Button(undo_redo_frame, text="REDO", command=self.redo)
        self.redo_button.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(2, 0))
            
        # Size label
        ttk.Label(tools_frame, text="BRUSH SIZE").pack(pady=(20, 10))
            
        # Size selection
        self.size_var = tk.StringVar(value="medium")
            
        size_frame = ttk.Frame(tools_frame)
        size_frame.pack(fill=tk.X, pady=5)
            
        small_rb = ttk.Radiobutton(size_frame, text="Small", variable=self.size_var, 
                                    value="small", command=self.update_brush_size)
        small_rb.pack(anchor=tk.W)
            
        medium_rb = ttk.Radiobutton(size_frame, text="Medium", variable=self.size_var, 
                                value="medium", command=self.update_brush_size)
        medium_rb.pack(anchor=tk.W)
        
        large_rb = ttk.Radiobutton(size_frame, text="Large", variable=self.size_var, 
                                value="large", command=self.update_brush_size)
        large_rb.pack(anchor=tk.W)
        
        extra_large_rb = ttk.Radiobutton(size_frame, text="Extra Large", variable=self.size_var,
                                    value="extra_large", command=self.update_brush_size)
        extra_large_rb.pack(anchor=tk.W)
        
        # File operations
        ttk.Label(tools_frame, text="FILE").pack(pady=(20, 10))
        
        save_png_button = ttk.Button(tools_frame, text="SAVE PNG", command=lambda: self.save_image("png"))
        save_png_button.pack(fill=tk.X, pady=2)
        
        save_jpg_button = ttk.Button(tools_frame, text="SAVE JPEG", command=lambda: self.save_image("jpeg"))
        save_jpg_button.pack(fill=tk.X, pady=2)

        save_ico_button = ttk.Button(tools_frame, text="SAVE ICO", command=lambda: self.save_image("ico"))
        save_ico_button.pack(fill=tk.X, pady=2)
        
        clear_button = ttk.Button(tools_frame, text="CLEAR ALL", command=self.clear_canvas)
        clear_button.pack(fill=tk.X, pady=(20, 2))
        
        # Right area for canvas and colors
        canvas_color_frame = ttk.Frame(main_frame)
        canvas_color_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Color palette
        color_frame = ttk.Frame(canvas_color_frame)
        color_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        ttk.Label(color_frame, text="COLOR PALETTE").pack(pady=(0, 10))
        
        # Define retro colors
        self.retro_colors = [
            ("#FF5555", "Red"), ("#FF9955", "Orange"), ("#FFFF55", "Yellow"), 
            ("#55FF55", "Green"), ("#5555FF", "Blue"), ("#AA55FF", "Purple"),
            ("#FF55AA", "Pink"), ("#AAAAAA", "Grey"), ("#000000", "Black"), 
            ("#FFFFFF", "White")
        ]
        
        # Create color palette buttons - without labels and with fixed size
        palette_frame = ttk.Frame(color_frame)
        palette_frame.pack()
        
        self.color_buttons = {}  # Store color button references
        
        for i, (color_hex, _) in enumerate(self.retro_colors):
            if i % 5 == 0:
                row_frame = ttk.Frame(palette_frame)
                row_frame.pack(fill=tk.X, pady=2)
            
            # Create a frame for each color button for better styling
            button_frame = ttk.Frame(row_frame, padding=1)
            button_frame.pack(side=tk.LEFT, padx=5)
            
            # Create the actual button with fixed size
            color_button = tk.Button(button_frame, bg=color_hex, width=6, height=2,
                                    command=lambda c=color_hex, b=None: self.set_color(c, b))
            color_button.pack(fill=tk.NONE, expand=False)  # Don't allow growing
            
            # Bind the command to the button instance after it's created
            color_button.config(command=lambda c=color_hex, b=color_button: self.set_color(c, b))
            
            # Store the button reference
            self.color_buttons[color_hex] = color_button
        
        # Canvas
        canvas_frame = ttk.Frame(canvas_color_frame)
        canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Create the canvas with checker pattern background to show transparency
        self.canvas = tk.Canvas(canvas_frame, width=self.canvas_width, height=self.canvas_height,
                            bg="white", highlightthickness=1, highlightbackground="#555555")
        self.canvas.pack(padx=10, pady=10)
        
        # Bind mouse events
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.end_draw)
        
        # Create the initial drawable image
        self.update_canvas()
        
        # Status frame
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.status_text = tk.StringVar(value="Ready to Doodle!")
        status_label = ttk.Label(status_frame, textvariable=self.status_text, 
                            anchor=tk.W, font=('Courier', 9))
        status_label.pack(side=tk.LEFT)
        
        # Keyboard shortcuts info
        shortcuts_label = ttk.Label(status_frame, text="Shortcuts: Ctrl+Z (Undo) | Ctrl+Y (Redo)",
                                anchor=tk.E, font=('Courier', 9))
        shortcuts_label.pack(side=tk.RIGHT)
        
        # Set initial color selection visual cue
        self.set_color("#000000", self.color_buttons["#000000"])
    
    def set_mode(self, mode):
        self.mode = mode
        
        # Reset all buttons
        self.brush_button.state(['!pressed'])
        self.eraser_button.state(['!pressed'])
        self.fill_shape_button.state(['!pressed'])
        self.bg_fill_button.state(['!pressed'])
        
        # Set the appropriate button state
        if mode == "brush":
            self.status_text.set(f"Brush mode - {self.size_var.get()} size")
            self.brush_button.state(['pressed'])
        elif mode == "eraser":
            self.status_text.set(f"Eraser mode - {self.size_var.get()} size")
            self.eraser_button.state(['pressed'])
        elif mode == "fill_shape":
            self.status_text.set("Fill Shape mode - Click inside a closed shape to fill it")
            self.fill_shape_button.state(['pressed'])
        elif mode == "bg_fill":
            self.status_text.set("Background Fill mode - Click to fill the background")
            self.bg_fill_button.state(['pressed'])
    
    def update_brush_size(self):
        size_value = self.size_var.get()
        if size_value == "small":
            self.brush_size = 2
        elif size_value == "medium":
            self.brush_size = 5
        elif size_value == "large":
            self.brush_size = 10
        else:  # extra_large
            self.brush_size = 20
        
        self.status_text.set(f"{self.mode.capitalize().replace('_', ' ')} mode - {size_value.replace('_', ' ')} size")
    
    def set_color(self, color, button=None):
        self.current_color = color
        self.status_text.set(f"Selected color: {color}")
        
        # Reset border of previously selected button
        if self.selected_color_button:
            self.selected_color_button.config(highlightbackground="#333333", highlightthickness=0)
        
        # Set the button parameter if not provided (for initialization)
        if button is None and color in self.color_buttons:
            button = self.color_buttons[color]
        
        # Highlight the selected button with a white glow border
        if button:
            button.config(highlightbackground="white", highlightthickness=3)
            self.selected_color_button = button
        
        # Switch to brush mode when selecting a color
        if self.mode not in ["fill_shape", "bg_fill"]:
            self.set_mode("brush")
    
    def start_draw(self, event):
        x, y = event.x, event.y
        
        if self.mode == "fill_shape":
            self.flood_fill_shape(x, y)
            return
        elif self.mode == "bg_fill":
            self.fill_background()
            return
        
        self.old_x = x
        self.old_y = y
        # Draw a dot at the starting point
        self.draw_point(x, y)
    
    def draw(self, event):
        if self.old_x and self.old_y and self.mode in ["brush", "eraser"]:
            if self.mode == "brush":
                self.pil_draw.line([self.old_x, self.old_y, event.x, event.y],
                                fill=self.current_color, width=self.brush_size)
            else:  # eraser
                # For the eraser, we use (0, 0, 0, 0) which is fully transparent
                self.pil_draw.line([self.old_x, self.old_y, event.x, event.y],
                                fill=(0, 0, 0, 0), width=self.brush_size)
            
            self.old_x = event.x
            self.old_y = event.y
            self.update_canvas()
    
    def end_draw(self, event):
        if self.mode in ["brush", "eraser"]:
            self.reset_coordinates(event)
            # Save state for undo/redo after drawing
            self.save_state()
    
    def draw_point(self, x, y):
        if self.mode == "brush":
            self.pil_draw.ellipse([x-self.brush_size//2, y-self.brush_size//2,
                                x+self.brush_size//2, y+self.brush_size//2],
                                fill=self.current_color, outline=self.current_color)
        else:  # eraser
            self.pil_draw.ellipse([x-self.brush_size//2, y-self.brush_size//2,
                                x+self.brush_size//2, y+self.brush_size//2],
                                fill=(0, 0, 0, 0), outline=(0, 0, 0, 0))
        self.update_canvas()
    
    def reset_coordinates(self, event):
        self.old_x = None
        self.old_y = None
    
    def fill_background(self):
        """Fill the entire background with the selected color"""
        # Create a new layer with the selected color
        bg_layer = Image.new("RGBA", self.pil_image.size, self.current_color)
        
        # Paste the current image on top of the background
        # Use the alpha channel of the current image as a mask
        result = Image.alpha_composite(bg_layer, self.pil_image)
        
        # Update the drawing area
        self.pil_image = result
        self.pil_draw = ImageDraw.Draw(self.pil_image)
        
        # Update display
        self.update_canvas()
        self.save_state()
        self.status_text.set(f"Background filled with color: {self.current_color}")
    
    def flood_fill_shape(self, x, y):
        """Fill a shape containing the point (x,y) with the selected color"""
        try:
            # Get RGBA values for the fill color
            rgba = ImageColor.getrgb(self.current_color)
            if len(rgba) == 3:  # Convert RGB to RGBA
                rgba = rgba + (255,)  # Add full alpha
            
            # Create a copy of the image for fill operation
            img_copy = self.pil_image.copy()
            ImageDraw.floodfill(img_copy, (x, y), rgba, thresh=50)
            
            # Update the image
            self.pil_image = img_copy
            self.pil_draw = ImageDraw.Draw(self.pil_image)
            
            # Update display
            self.update_canvas()
            self.save_state()
            self.status_text.set(f"Shape filled with color: {self.current_color}")
        except Exception as e:
            self.status_text.set(f"Fill failed: {str(e)}")
            print("Fill error:", e)
    
    def update_canvas(self):
        # Convert PIL image for display
        self.tk_image = ImageTk.PhotoImage(self.pil_image)
        
        # Clear the canvas and display the new image
        self.canvas.delete("all")
        
        # Create a checkerboard pattern to indicate transparency
        for i in range(0, self.canvas_width, 20):
            for j in range(0, self.canvas_height, 20):
                if (i // 20 + j // 20) % 2 == 0:
                    self.canvas.create_rectangle(i, j, i+20, j+20, fill="#EEEEEE", outline="")
                else:
                    self.canvas.create_rectangle(i, j, i+20, j+20, fill="#DDDDDD", outline="")
        
        # Display the image on top of the checkerboard
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
    
    def save_state(self):
        """Save current state to history stack for undo functionality"""
        # Create a deep copy of the current image
        state_copy = self.pil_image.copy()
        self.history_stack.append(state_copy)
        
        # Clear redo stack when new action is performed
        self.redo_stack.clear()
        
        # Limit history size to prevent excessive memory usage
        if len(self.history_stack) > 20:
            self.history_stack.pop(0)
        
        self.update_undo_redo_status()
    
    def undo(self):
        """Undo the last drawing action"""
        if len(self.history_stack) > 1:  # Need at least 2 states to undo (current and previous)
            # Move current state to redo stack
            current_state = self.history_stack.pop()
            self.redo_stack.append(current_state)
            
            # Restore previous state
            previous_state = self.history_stack[-1]
            self.pil_image = previous_state.copy()
            self.pil_draw = ImageDraw.Draw(self.pil_image)
            
            self.update_canvas()
            self.status_text.set("Undo successful")
            self.update_undo_redo_status()
        else:
            self.status_text.set("Nothing to undo")
    
    def redo(self):
        """Redo the previously undone action"""
        if self.redo_stack:
            # Get the next state from redo stack
            next_state = self.redo_stack.pop()
            
            # Add it back to the history stack
            self.history_stack.append(next_state)
            
            # Restore that state
            self.pil_image = next_state.copy()
            self.pil_draw = ImageDraw.Draw(self.pil_image)
            
            self.update_canvas()
            self.status_text.set("Redo successful")
            self.update_undo_redo_status()
        else:
            self.status_text.set("Nothing to redo")
    
    def update_undo_redo_status(self):
        """Update the enabled/disabled state of undo/redo buttons"""
        # Check undo button
        if len(self.history_stack) > 1:
            self.undo_button.state(['!disabled'])
        else:
            self.undo_button.state(['disabled'])
        
        # Check redo button
        if self.redo_stack:
            self.redo_button.state(['!disabled'])
        else:
            self.redo_button.state(['disabled'])
    
    def clear_canvas(self):
        if messagebox.askyesno("Clear Canvas", "Are you sure you want to clear the canvas?"):
            self.pil_image = Image.new("RGBA", (self.canvas_width, self.canvas_height), (255, 255, 255, 0))
            self.pil_draw = ImageDraw.Draw(self.pil_image)
            self.update_canvas()
            self.save_state()  # Save the cleared state for undo
            self.status_text.set("Canvas cleared")
    
    def save_image(self, format_type):
        file_types = []
        if format_type == "png":
            file_types = [('PNG files', '*.png')]
            default_extension = ".png"
        elif format_type == "jpeg":
            file_types = [('JPEG files', '*.jpg')]
            default_extension = ".jpg"
        elif format_type == "ico":
            file_types = [('Icon files', '*.ico')]
            default_extension = ".ico"
        
        file_path = filedialog.asksaveasfilename(defaultextension=default_extension,
                                            filetypes=file_types, 
                                            title="Save As")
        
        if file_path:
            try:
                if format_type == "jpeg":
                    # For JPEG, convert to RGB and fill transparency with white
                    rgb_image = Image.new("RGB", self.pil_image.size, (255, 255, 255))
                    rgb_image.paste(self.pil_image, mask=self.pil_image.split()[3])
                    rgb_image.save(file_path, "JPEG", quality=95)
                elif format_type == "ico":
                    # For ICO, resize if needed and save
                    ico_image = self.pil_image.copy()
                    
                    # Icon files typically use small sizes like 16x16, 32x32, 48x48
                    # Get the maximum dimension and scale it to 48px if larger
                    max_dim = max(ico_image.width, ico_image.height)
                    if max_dim > 48:
                        scale_factor = 48 / max_dim
                        new_width = int(ico_image.width * scale_factor)
                        new_height = int(ico_image.height * scale_factor)
                        ico_image = ico_image.resize((new_width, new_height), Image.LANCZOS)
                        
                    # Save as ICO
                    ico_image.save(file_path, format="ICO")
                else:  # PNG
                    self.pil_image.save(file_path, "PNG")
                
                self.status_text.set(f"Saved as {os.path.basename(file_path)}")
                messagebox.showinfo("Save Successful", f"File saved successfully to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Error saving file: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DoodleApp(root)
    root.mainloop()