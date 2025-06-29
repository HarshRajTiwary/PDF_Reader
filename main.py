import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pyttsx3
import fitz
from threading import Thread
from PIL import Image, ImageTk
import time

class PDF_Reader_App:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Voice Reader Pro")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)
        self.root.configure(bg='#f0f2f5')
        
        # Initialize TTS engine
        self.engine = None
        self.is_playing = False
        self.is_paused = False
        self.current_text = ""
        self.playback_thread = None
        self.current_position = 0
        self.total_chars = 0
        
        # Load icons (placeholder paths - replace with actual icon files)
        self.icons = {
            'play': self.create_icon("▶", "#4CAF50"),
            'pause': self.create_icon("⏸", "#FFC107"),
            'stop': self.create_icon("⏹", "#F44336"),
            'forward': self.create_icon("⏩", "#2196F3"),
            'backward': self.create_icon("⏪", "#2196F3"),
            'open': self.create_icon("📂", "#607D8B"),
            'clear': self.create_icon("🗑", "#607D8B")
        }
        
        # Styling
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure styles
        self.style.configure('TFrame', background='#f0f2f5')
        self.style.configure('TButton', font=('Segoe UI', 10), padding=8)
        self.style.configure('TLabel', background='#f0f2f5', foreground='#333333')
        self.style.configure('Header.TLabel', font=('Segoe UI', 14, 'bold'), foreground='#2c3e50')
        self.style.configure('Control.TFrame', background='#ffffff', relief=tk.RAISED, borderwidth=1)
        self.style.configure('Status.TLabel', font=('Segoe UI', 9), foreground='#666666')
        
        # Custom button styles
        self.style.map('Primary.TButton',
                      foreground=[('active', 'white'), ('!disabled', 'white')],
                      background=[('active', '#45a049'), ('!disabled', '#4CAF50')])
        
        self.style.map('Secondary.TButton',
                      foreground=[('active', 'white'), ('!disabled', 'white')],
                      background=[('active', '#0288D1'), ('!disabled', '#03A9F4')])
        
        self.style.map('Warning.TButton',
                      foreground=[('active', 'white'), ('!disabled', 'white')],
                      background=[('active', '#d32f2f'), ('!disabled', '#F44336')])
        
        # Main container
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        self.header_frame = ttk.Frame(self.main_frame, style='Control.TFrame')
        self.header_frame.pack(fill=tk.X, pady=(0, 10), ipady=10)
        
        ttk.Label(self.header_frame, text="PDF VOICE READER PRO", style='Header.TLabel').pack(side=tk.LEFT, padx=10)
        ttk.Label(self.header_frame, text="Premium Edition", style='TLabel').pack(side=tk.LEFT, padx=5)
        ttk.Label(self.header_frame, text="Created by Harsh Raj", style='TLabel').pack(side=tk.RIGHT, padx=10)
        
        # Content area
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # PDF text display
        self.text_frame = ttk.Frame(self.content_frame, style='Control.TFrame')
        self.text_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=(0, 10))
        
        self.text_scroll = ttk.Scrollbar(self.text_frame)
        self.text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_display = tk.Text(
            self.text_frame, 
            wrap=tk.WORD, 
            yscrollcommand=self.text_scroll.set,
            bg='#ffffff', 
            fg='#333333', 
            insertbackground='#333333',
            selectbackground='#BBDEFB',
            font=('Segoe UI', 10),
            padx=10,
            pady=10,
            relief=tk.FLAT
        )
        self.text_display.pack(fill=tk.BOTH, expand=True)
        self.text_scroll.config(command=self.text_display.yview)
        
        # Controls frame
        self.controls_frame = ttk.Frame(self.content_frame, width=200, style='Control.TFrame')
        self.controls_frame.pack(fill=tk.Y, side=tk.RIGHT)
        
        # File controls
        file_controls = ttk.LabelFrame(self.controls_frame, text="File", style='TFrame')
        file_controls.pack(fill=tk.X, pady=(0, 10), padx=5, ipadx=5, ipady=5)
        
        ttk.Button(
            file_controls, 
            text=" Open PDF", 
            image=self.icons['open'],
            compound=tk.LEFT,
            style='Secondary.TButton',
            command=self.open_pdf
        ).pack(fill=tk.X, pady=2)
        
        ttk.Button(
            file_controls, 
            text=" Clear Text", 
            image=self.icons['clear'],
            compound=tk.LEFT,
            style='Secondary.TButton',
            command=self.clear_text
        ).pack(fill=tk.X, pady=2)
        
        # Playback controls
        playback_controls = ttk.LabelFrame(self.controls_frame, text="Playback", style='TFrame')
        playback_controls.pack(fill=tk.X, pady=(0, 10), padx=5, ipadx=5, ipady=5)
        
        control_buttons = ttk.Frame(playback_controls)
        control_buttons.pack(fill=tk.X)
        
        self.backward_btn = ttk.Button(
            control_buttons, 
            text=" Back", 
            image=self.icons['backward'],
            compound=tk.LEFT,
            style='Secondary.TButton',
            command=self.skip_backward,
            state=tk.DISABLED
        )
        self.backward_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        self.play_btn = ttk.Button(
            control_buttons, 
            text=" Play", 
            image=self.icons['play'],
            compound=tk.LEFT,
            style='Primary.TButton',
            command=self.play_audio
        )
        self.play_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        self.pause_btn = ttk.Button(
            control_buttons, 
            text=" Pause", 
            image=self.icons['pause'],
            compound=tk.LEFT,
            style='Warning.TButton',
            command=self.pause_audio,
            state=tk.DISABLED
        )
        self.pause_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        self.stop_btn = ttk.Button(
            control_buttons, 
            text=" Stop", 
            image=self.icons['stop'],
            compound=tk.LEFT,
            style='Warning.TButton',
            command=self.stop_audio,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        self.forward_btn = ttk.Button(
            control_buttons, 
            text=" Forward", 
            image=self.icons['forward'],
            compound=tk.LEFT,
            style='Secondary.TButton',
            command=self.skip_forward,
            state=tk.DISABLED
        )
        self.forward_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        # Progress bar
        self.progress_frame = ttk.Frame(playback_controls)
        self.progress_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.progress_label = ttk.Label(self.progress_frame, text="Progress:", style='TLabel')
        self.progress_label.pack(anchor=tk.W)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.progress_frame, 
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.pack(fill=tk.X)
        
        # Voice settings
        settings_frame = ttk.LabelFrame(self.controls_frame, text="Voice Settings", style='TFrame')
        settings_frame.pack(fill=tk.X, padx=5, ipadx=5, ipady=5)
        
        # Voice selection
        ttk.Label(settings_frame, text="Voice:").pack(anchor=tk.W)
        self.voice_var = tk.StringVar()
        self.voice_combobox = ttk.Combobox(settings_frame, textvariable=self.voice_var, state='readonly')
        self.voice_combobox.pack(fill=tk.X, pady=(0, 5))
        
        # Speed control
        ttk.Label(settings_frame, text="Speed:").pack(anchor=tk.W)
        self.speed_frame = ttk.Frame(settings_frame)
        self.speed_frame.pack(fill=tk.X)
        
        ttk.Label(self.speed_frame, text="Slow").pack(side=tk.LEFT)
        self.speed_slider = ttk.Scale(
            settings_frame, 
            from_=50, 
            to=300, 
            value=200,
            command=self.update_speed
        )
        self.speed_slider.pack(fill=tk.X)
        ttk.Label(self.speed_frame, text="Fast").pack(side=tk.RIGHT)
        
        # Volume control
        ttk.Label(settings_frame, text="Volume:").pack(anchor=tk.W, pady=(5, 0))
        self.volume_frame = ttk.Frame(settings_frame)
        self.volume_frame.pack(fill=tk.X)
        
        ttk.Label(self.volume_frame, text="Low").pack(side=tk.LEFT)
        self.volume_slider = ttk.Scale(
            settings_frame, 
            from_=0, 
            to=100, 
            value=70,
            command=self.update_volume
        )
        self.volume_slider.pack(fill=tk.X)
        ttk.Label(self.volume_frame, text="High").pack(side=tk.RIGHT)
        
        # Status bar
        self.status_frame = ttk.Frame(self.main_frame, style='Control.TFrame')
        self.status_frame.pack(fill=tk.X, pady=(10, 0), ipady=5)
        
        self.status_text = tk.StringVar()
        self.status_text.set("Ready to open a PDF file")
        self.status_label = ttk.Label(
            self.status_frame, 
            textvariable=self.status_text, 
            style='Status.TLabel'
        )
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # Initialize engine
        self.init_engine()
    
    def create_icon(self, symbol, color):
        """Create a simple text-based icon"""
        img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
        return ImageTk.PhotoImage(img)  # Placeholder - in real app use actual icons
    
    def init_engine(self):
        try:
            self.engine = pyttsx3.init()
            voices = self.engine.getProperty('voices')
            
            # Populate voice combobox
            voice_names = [voice.name for voice in voices]
            self.voice_combobox['values'] = voice_names
            if len(voice_names) > 1:
                self.voice_combobox.current(1)  # Default to female voice if available
            else:
                self.voice_combobox.current(0)
            
            self.voice_var.trace('w', self.update_voice)
            
            # Set default properties
            self.engine.setProperty('rate', 200)
            self.engine.setProperty('volume', 0.7)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize TTS engine: {str(e)}")
            self.status_text.set("TTS engine initialization failed")
    
    def update_voice(self, *args):
        if self.engine:
            voices = self.engine.getProperty('voices')
            selected = self.voice_combobox.current()
            if 0 <= selected < len(voices):
                self.engine.setProperty('voice', voices[selected].id)
                self.status_text.set(f"Voice set to {voices[selected].name}")
    
    def open_pdf(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            title="Select PDF File"
        )
        if file_path:
            try:
                self.status_text.set(f"Loading: {os.path.basename(file_path)}...")
                self.root.update()
                
                pdf_document = fitz.open(file_path)
                text = ""
                for page_num in range(len(pdf_document)):
                    page = pdf_document[page_num]
                    text += page.get_text()
                
                self.current_text = text
                self.total_chars = len(text)
                self.current_position = 0
                self.text_display.delete(1.0, tk.END)
                self.text_display.insert(tk.END, text)
                self.progress_var.set(0)
                
                self.status_text.set(f"Loaded: {os.path.basename(file_path)}")
                self.backward_btn.config(state=tk.NORMAL)
                self.forward_btn.config(state=tk.NORMAL)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load PDF: {str(e)}")
                self.status_text.set("Error loading PDF")
    
    def clear_text(self):
        self.text_display.delete(1.0, tk.END)
        self.current_text = ""
        self.current_position = 0
        self.total_chars = 0
        self.progress_var.set(0)
        self.status_text.set("Text cleared")
        self.backward_btn.config(state=tk.DISABLED)
        self.forward_btn.config(state=tk.DISABLED)
        self.stop_audio()  # Stop any ongoing playback
    
    def play_audio(self):
        if not self.current_text:
            self.status_text.set("No text to read")
            return
            
        if self.is_playing and not self.is_paused:
            return
            
        self.is_playing = True
        self.is_paused = False
        self.play_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.NORMAL)
        self.backward_btn.config(state=tk.NORMAL)
        self.forward_btn.config(state=tk.NORMAL)
        
        text_to_read = self.current_text[self.current_position:]
        self.playback_thread = Thread(target=self._play_audio_thread, args=(text_to_read,), daemon=True)
        self.playback_thread.start()
    
    def _play_audio_thread(self, text):
        try:
            self.engine.say(text)
            self.engine.runAndWait()
            
            # Update position when playback completes
            if not self.is_paused:
                self.current_position = self.total_chars
                self.progress_var.set(100)
                
        except Exception as e:
            self.status_text.set(f"Playback error: {str(e)}")
        finally:
            if not self.is_paused:
                self.is_playing = False
                self.root.after(0, self._reset_playback_buttons)
    
    def _reset_playback_buttons(self):
        self.play_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_text.set("Playback completed" if self.current_text else "Ready")
    
    def pause_audio(self):
        if self.is_playing and not self.is_paused:
            self.engine.stop()
            self.is_paused = True
            self.pause_btn.config(state=tk.DISABLED)
            self.play_btn.config(state=tk.NORMAL)
            
            # Calculate current position
            # Note: pyttsx3 doesn't provide exact position, this is an approximation
            elapsed = self.engine.getProperty('rate') / 100  # Words per second approximation
            self.current_position = min(self.total_chars, self.current_position + int(elapsed * 10))
            progress = (self.current_position / self.total_chars) * 100 if self.total_chars > 0 else 0
            self.progress_var.set(progress)
            
            self.status_text.set(f"Playback paused at {int(progress)}%")
    
    def stop_audio(self):
        if self.is_playing:
            self.engine.stop()
            self.is_playing = False
            self.is_paused = False
            self.current_position = 0
            self.progress_var.set(0)
            self._reset_playback_buttons()
            self.status_text.set("Playback stopped")
    
    def skip_forward(self):
        if self.total_chars > 0:
            skip_amount = int(self.total_chars * 0.1)  # Skip 10% forward
            self.current_position = min(self.total_chars, self.current_position + skip_amount)
            progress = (self.current_position / self.total_chars) * 100
            self.progress_var.set(progress)
            
            if self.is_playing:
                self.pause_audio()
                self.play_audio()
            
            self.status_text.set(f"Skipped to {int(progress)}%")
    
    def skip_backward(self):
        if self.total_chars > 0:
            skip_amount = int(self.total_chars * 0.1)  # Skip 10% backward
            self.current_position = max(0, self.current_position - skip_amount)
            progress = (self.current_position / self.total_chars) * 100
            self.progress_var.set(progress)
            
            if self.is_playing:
                self.pause_audio()
                self.play_audio()
            
            self.status_text.set(f"Skipped to {int(progress)}%")
    
    def update_speed(self, value):
        if self.engine:
            speed = int(float(value))
            self.engine.setProperty('rate', speed)
            self.status_text.set(f"Speed set to {speed} (words per minute)")
    
    def update_volume(self, value):
        if self.engine:
            volume = float(value) / 100
            self.engine.setProperty('volume', volume)
            self.status_text.set(f"Volume set to {int(float(value))}%")

if __name__ == "__main__":
    root = tk.Tk()
    
    # Set window icon (replace with actual icon file)
    try:
        root.iconbitmap('icon.ico')
    except:
        pass
    
    app = PDF_Reader_App(root)
    root.mainloop()