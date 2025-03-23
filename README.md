# Dual Screen Presentation Application

This application controls what is being displayed on two screens:

1. **PDF Reader**: Opens a PDF file, reads it aloud, and displays what is currently being read.
2. **Image Slideshow**: Showcases a slideshow of images that go along with the PDF.

## Features

### PDF Reader
- Open and display PDF files
- Navigate between pages
- Text-to-speech functionality to read PDF content aloud

### Image Slideshow
- Open and display images from a folder
- Navigate between images
- Automatic slideshow with adjustable timing

## Installation

1. Ensure you have Python 3.6+ installed
2. Install the required dependencies:

```
pip install -r requirements.txt
```

## Usage

Run the application with:

```
python main.py
```

### Getting Started

1. Use the "Open PDF" button to select a PDF file
2. Use the "Open Images" button to select a folder containing images
3. Navigate through PDF pages using the "Previous" and "Next" buttons
4. Start/stop reading the PDF aloud using the "Read Aloud" button
5. Navigate through images using the "Previous" and "Next" buttons
6. Start/stop the image slideshow using the "Play Slideshow" button
7. Adjust slideshow speed in the Settings menu

## Dependencies

- PyMuPDF: PDF processing
- pyttsx3: Text-to-speech functionality
- Pillow: Image processing
- Pygame: Additional multimedia support
- Tkinter: GUI framework (included with Python)
