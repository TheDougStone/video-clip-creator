#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import sys
import traceback
from video_clip_creator import create_clips, parse_timecode
import pandas as pd

class VideoClipCreatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Clip Creator")
        self.root.geometry("600x400")
        
        # Make window resizable
        self.root.resizable(True, True)
        
        # Configure style
        style = ttk.Style()
        style.configure('TButton', padding=5)
        style.configure('TLabel', padding=5)
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Video file selection
        ttk.Label(main_frame, text="Video File:").grid(row=0, column=0, sticky=tk.W)
        self.video_path = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.video_path, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_video).grid(row=0, column=2)
        
        # CSV file selection
        ttk.Label(main_frame, text="CSV File:").grid(row=1, column=0, sticky=tk.W)
        self.csv_path = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.csv_path, width=50).grid(row=1, column=1, padx=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_csv).grid(row=1, column=2)
        
        # Output directory selection
        ttk.Label(main_frame, text="Output Directory:").grid(row=2, column=0, sticky=tk.W)
        self.output_path = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.output_path, width=50).grid(row=2, column=1, padx=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_output).grid(row=2, column=2)
        
        # Preview frame
        preview_frame = ttk.LabelFrame(main_frame, text="CSV Preview", padding="5")
        preview_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Create Treeview for CSV preview
        self.tree = ttk.Treeview(preview_frame, columns=("Start", "End", "OutputName"), show="headings", height=5)
        self.tree.heading("Start", text="Start")
        self.tree.heading("End", text="End")
        self.tree.heading("OutputName", text="Output Name")
        
        # Set column widths
        self.tree.column("Start", width=100)
        self.tree.column("End", width=100)
        self.tree.column("OutputName", width=200)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add scrollbar to Treeview
        scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Status label
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        ttk.Label(main_frame, textvariable=self.status_var).grid(row=5, column=0, columnspan=3)
        
        # Process button
        self.process_button = ttk.Button(main_frame, text="Create Clips", command=self.process_video)
        self.process_button.grid(row=6, column=0, columnspan=3, pady=10)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        
        # Bind CSV path changes to update preview
        self.csv_path.trace_add("write", self.update_preview)
        
        # Set initial focus
        self.root.focus_force()
    
    def browse_video(self):
        try:
            filename = filedialog.askopenfilename(
                title="Select Video File",
                filetypes=[
                    ("Video files", "*.mp4 *.avi *.mov *.mkv"),
                    ("All files", "*.*")
                ]
            )
            if filename:
                self.video_path.set(filename)
        except Exception as e:
            self.show_error("Error selecting video file", str(e))
    
    def browse_csv(self):
        try:
            filename = filedialog.askopenfilename(
                title="Select CSV File",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            if filename:
                self.csv_path.set(filename)
        except Exception as e:
            self.show_error("Error selecting CSV file", str(e))
    
    def browse_output(self):
        try:
            dirname = filedialog.askdirectory(title="Select Output Directory")
            if dirname:
                self.output_path.set(dirname)
        except Exception as e:
            self.show_error("Error selecting output directory", str(e))
    
    def update_preview(self, *args):
        try:
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Try to load and preview CSV
            csv_path = self.csv_path.get()
            if csv_path and os.path.exists(csv_path):
                try:
                    df = pd.read_csv(csv_path)
                    # Normalize column names to title case
                    df.columns = [col.title() for col in df.columns]
                    required_columns = ['Start', 'End']
                    if not all(col in df.columns for col in required_columns):
                        raise ValueError(f"CSV must contain columns: {', '.join(required_columns)}")
                    
                    for _, row in df.iterrows():
                        self.tree.insert("", tk.END, values=(
                            row.get('Start', ''),
                            row.get('End', ''),
                            row.get('Outputname', '')
                        ))
                except Exception as e:
                    self.show_error("Error loading CSV", str(e))
        except Exception as e:
            self.show_error("Error updating preview", str(e))
    
    def process_video(self):
        try:
            # Validate inputs
            if not self.video_path.get():
                self.show_error("Error", "Please select a video file")
                return
            if not self.csv_path.get():
                self.show_error("Error", "Please select a CSV file")
                return
            if not self.output_path.get():
                self.show_error("Error", "Please select an output directory")
                return
            
            # Validate file existence
            if not os.path.exists(self.video_path.get()):
                self.show_error("Error", "Video file does not exist")
                return
            if not os.path.exists(self.csv_path.get()):
                self.show_error("Error", "CSV file does not exist")
                return
            
            # Disable process button
            self.process_button.configure(state="disabled")
            self.status_var.set("Processing...")
            
            # Start processing in a separate thread
            thread = threading.Thread(target=self._process_video_thread)
            thread.daemon = True
            thread.start()
        except Exception as e:
            self.show_error("Error starting process", str(e))
    
    def _process_video_thread(self):
        try:
            create_clips(
                self.video_path.get(),
                self.csv_path.get(),
                self.output_path.get()
            )
            self.root.after(0, lambda: messagebox.showinfo("Success", "Video clips created successfully!"))
        except Exception as e:
            error_msg = f"Error processing video:\n{str(e)}\n\n{traceback.format_exc()}"
            self.root.after(0, lambda: self.show_error("Processing Error", error_msg))
        finally:
            self.root.after(0, lambda: self.process_button.configure(state="normal"))
            self.root.after(0, lambda: self.status_var.set("Ready"))
    
    def show_error(self, title, message):
        """Show error message in a dialog box"""
        messagebox.showerror(title, message)

def main():
    try:
        root = tk.Tk()
        app = VideoClipCreatorGUI(root)
        root.mainloop()
    except Exception as e:
        error_msg = f"Application Error:\n{str(e)}\n\n{traceback.format_exc()}"
        messagebox.showerror("Fatal Error", error_msg)
        sys.exit(1)

if __name__ == "__main__":
    main() 