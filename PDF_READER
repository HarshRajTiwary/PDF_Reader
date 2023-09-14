import os
import tkinter as tk
from tkinter import filedialog
import pyttsx3
import fitz

class PDF_Reader_App:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Reader")
        
        self.status_text = tk.StringVar()
        # self.status_label = tk.Label(root, textvariable=self.status_text)
        # self.status_label.pack(pady=10)

        open_button = tk.Button(root, text="Open PDF", background="red", foreground="yellow", command=self.open_pdf)
        open_button.pack()
        tk.Label(root, text="Created by Harsh Raj...", background="black", foreground="yellow").pack()

    def open_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            self.status_text.set("Selected file: " + os.path.basename(file_path))
            pdf_document = fitz.open(file_path)
            text = ""
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                text += page.get_text()
            
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            engine.setProperty('voice', voices[1].id)
            engine.say(text)
            engine.runAndWait()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("250x50")
    root.maxsize(250,50)
    root.minsize(250,50)
    root.config(background="black")
    app = PDF_Reader_App(root)
    root.mainloop()
