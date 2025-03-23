"""
For this project I'd like to build a program that will control what is being displayed 
on two screens.

One screen will be a PDF Reader, it simply opens a PDF file, reads it aloud, and displays what is currently being read.

The other screen will showcase a slideshow of images that go along with the PDF.
"""

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import fitz  # PyMuPDF
import pygame
from PIL import Image, ImageTk
import pyttsx3
import threading
import time
from pathlib import Path


class PDFReader:
    def __init__(self, root, width, height):
        self.root = root
        self.width = width
        self.height = height
        self.current_page = 0
        self.pdf_document = None
        self.text_to_read = ""
        self.is_reading = False
        self.tts_engine = pyttsx3.init()
        
        # Configure the frame
        self.frame = tk.Frame(root, width=width, height=height)
        self.frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Text display area
        self.text_display = tk.Text(self.frame, wrap=tk.WORD, font=("Arial", 12))
        self.text_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control buttons
        self.controls_frame = tk.Frame(self.frame)
        self.controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.prev_button = tk.Button(self.controls_frame, text="Previous", command=self.prev_page)
        self.prev_button.pack(side=tk.LEFT, padx=5)
        
        self.next_button = tk.Button(self.controls_frame, text="Next", command=self.next_page)
        self.next_button.pack(side=tk.LEFT, padx=5)
        
        self.read_button = tk.Button(self.controls_frame, text="Read Aloud", command=self.toggle_reading)
        self.read_button.pack(side=tk.LEFT, padx=5)
        
        self.open_button = tk.Button(self.controls_frame, text="Open PDF", command=self.open_pdf)
        self.open_button.pack(side=tk.LEFT, padx=5)
    
    def open_pdf(self):
        # Stop any ongoing reading
        self.stop_reading()
        
        # Open file dialog
        file_path = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if file_path:
            try:
                self.pdf_document = fitz.open(file_path)
                self.current_page = 0
                self.display_page()
                return file_path
            except Exception as e:
                messagebox.showerror("Error", f"Could not open PDF: {str(e)}")
                return None
        return None
    
    def display_page(self):
        if not self.pdf_document:
            return
        
        # Clear the text display
        self.text_display.delete(1.0, tk.END)
        
        # Get page and extract text
        page = self.pdf_document[self.current_page]
        self.text_to_read = page.get_text()
        
        # Display the text
        self.text_display.insert(tk.END, self.text_to_read)
        
        # Update page info
        page_info = f"Page {self.current_page + 1} of {len(self.pdf_document)}"
        self.text_display.insert(tk.END, f"\n\n{page_info}")
    
    def next_page(self):
        if self.pdf_document and self.current_page < len(self.pdf_document) - 1:
            self.stop_reading()
            self.current_page += 1
            self.display_page()
    
    def prev_page(self):
        if self.pdf_document and self.current_page > 0:
            self.stop_reading()
            self.current_page -= 1
            self.display_page()
    
    def toggle_reading(self):
        if self.is_reading:
            self.stop_reading()
        else:
            self.start_reading()
    
    def start_reading(self):
        if not self.pdf_document:
            messagebox.showinfo("Info", "Please open a PDF file first.")
            return
        
        self.is_reading = True
        self.read_button.config(text="Stop Reading")
        
        # Start reading in a separate thread
        self.read_thread = threading.Thread(target=self.read_aloud)
        self.read_thread.daemon = True
        self.read_thread.start()
    
    def stop_reading(self):
        if self.is_reading:
            self.is_reading = False
            self.read_button.config(text="Read Aloud")
            self.tts_engine.stop()
    
    def read_aloud(self):
        self.tts_engine.say(self.text_to_read)
        self.tts_engine.runAndWait()
        self.is_reading = False
        self.root.after(0, lambda: self.read_button.config(text="Read Aloud"))


class ImageSlideshow:
    def __init__(self, root, width, height):
        self.root = root
        self.width = width
        self.height = height
        self.images = []
        self.current_image = 0
        self.slideshow_running = False
        self.slideshow_delay = 5000  # 5 seconds
        
        # Configure the frame
        self.frame = tk.Frame(root, width=width, height=height)
        self.frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Image display area
        self.image_label = tk.Label(self.frame)
        self.image_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control buttons
        self.controls_frame = tk.Frame(self.frame)
        self.controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.prev_button = tk.Button(self.controls_frame, text="Previous", command=self.prev_image)
        self.prev_button.pack(side=tk.LEFT, padx=5)
        
        self.next_button = tk.Button(self.controls_frame, text="Next", command=self.next_image)
        self.next_button.pack(side=tk.LEFT, padx=5)
        
        self.play_button = tk.Button(self.controls_frame, text="Play Slideshow", command=self.toggle_slideshow)
        self.play_button.pack(side=tk.LEFT, padx=5)
        
        self.open_button = tk.Button(self.controls_frame, text="Open Images", command=self.open_images)
        self.open_button.pack(side=tk.LEFT, padx=5)
    
    def open_images(self):
        # Stop any ongoing slideshow
        self.stop_slideshow()
        
        # Open file dialog
        folder_path = filedialog.askdirectory(title="Select Image Folder")
        
        if folder_path:
            self.images = []
            valid_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp"]
            
            # Get all image files in the folder
            for file in os.listdir(folder_path):
                ext = os.path.splitext(file)[1].lower()
                if ext in valid_extensions:
                    self.images.append(os.path.join(folder_path, file))
            
            if self.images:
                self.current_image = 0
                self.display_image()
                return folder_path
            else:
                messagebox.showinfo("Info", "No image files found in the selected folder.")
                return None
        return None
    
    def display_image(self):
        if not self.images:
            return
        
        try:
            # Open and resize the image
            img = Image.open(self.images[self.current_image])
            img = self.resize_image(img)
            
            # Convert to PhotoImage and display
            photo = ImageTk.PhotoImage(img)
            self.image_label.config(image=photo)
            self.image_label.image = photo  # Keep a reference
            
            # Display image info
            image_info = f"Image {self.current_image + 1} of {len(self.images)}"
            self.image_label.config(text=image_info, compound=tk.BOTTOM)
        except Exception as e:
            messagebox.showerror("Error", f"Could not display image: {str(e)}")
    
    def resize_image(self, img):
        # Calculate the new size while maintaining aspect ratio
        width, height = img.size
        max_width = self.width - 40  # Account for padding
        max_height = self.height - 80  # Account for padding and controls
        
        if width > max_width or height > max_height:
            ratio = min(max_width / width, max_height / height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            return img.resize((new_width, new_height), Image.LANCZOS)
        return img
    
    def next_image(self):
        if self.images and self.current_image < len(self.images) - 1:
            self.current_image += 1
            self.display_image()
    
    def prev_image(self):
        if self.images and self.current_image > 0:
            self.current_image -= 1
            self.display_image()
    
    def toggle_slideshow(self):
        if self.slideshow_running:
            self.stop_slideshow()
        else:
            self.start_slideshow()
    
    def start_slideshow(self):
        if not self.images:
            messagebox.showinfo("Info", "Please open image files first.")
            return
        
        self.slideshow_running = True
        self.play_button.config(text="Stop Slideshow")
        self.advance_slideshow()
    
    def stop_slideshow(self):
        self.slideshow_running = False
        self.play_button.config(text="Play Slideshow")
        # Cancel any pending slideshow advances
        if hasattr(self, 'slideshow_id'):
            self.root.after_cancel(self.slideshow_id)
    
    def advance_slideshow(self):
        if self.slideshow_running:
            self.next_image()
            # Loop back to the beginning if we're at the end
            if self.current_image >= len(self.images) - 1:
                self.current_image = -1  # Will be incremented to 0 in next_image
            
            # Schedule the next advance
            self.slideshow_id = self.root.after(self.slideshow_delay, self.advance_slideshow)


class DualScreenApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dual Screen Presentation")
        
        # Get screen width and height
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        # Set window size to full screen
        root.geometry(f"{screen_width}x{screen_height}")
        
        # Calculate dimensions for each panel
        panel_width = screen_width // 2
        panel_height = screen_height
        
        # Create the PDF reader
        self.pdf_reader = PDFReader(root, panel_width, panel_height)
        
        # Create the image slideshow
        self.slideshow = ImageSlideshow(root, panel_width, panel_height)
        
        # Menu bar
        self.create_menu()
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open PDF", command=self.pdf_reader.open_pdf)
        file_menu.add_command(label="Open Images", command=self.slideshow.open_images)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Slideshow Speed", command=self.set_slideshow_speed)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        
        self.root.config(menu=menubar)
    
    def set_slideshow_speed(self):
        # Simple dialog to set slideshow speed
        speed = tk.simpledialog.askinteger(
            "Slideshow Speed",
            "Enter slideshow delay in seconds:",
            minvalue=1,
            maxvalue=60,
            initialvalue=self.slideshow.slideshow_delay // 1000
        )
        
        if speed:
            self.slideshow.slideshow_delay = speed * 1000


def main():
    root = tk.Tk()
    app = DualScreenApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()