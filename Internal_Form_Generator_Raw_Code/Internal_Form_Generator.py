import tkinter as tk
from tkinter import messagebox, Text
import csv
import os
import sys
from datetime import datetime
import re
import requests
from PIL import Image, ImageTk
import pygame  # For audio playback
import subprocess  # For video playback
import platform  # For detecting OS
import tempfile  # Might be needed for temporary files
from PyInstaller.utils.hooks import collect_all

class FormApplication:
    def __init__(self, root, questions_file, csv_file, description_file="Description.txt", window_width=800, window_height=600):
        self.root = root
        self.root.title("Internal Form Organizer")
        self.root.geometry(f"{window_width}x{window_height}")
        
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        
        # Create path for Change_Form folder
        self.data_folder = os.path.join(script_dir, "Change_Form")
        
        # Create path for Media_Data folder
        self.media_folder = os.path.join(script_dir, "Media_Data")
        
        # Create path for VLC Portable folder
        self.vlc_folder = os.path.join(script_dir, "VLCPortable")
        
        # Create the folders if they don't exist
        os.makedirs(self.data_folder, exist_ok=True)
        os.makedirs(self.media_folder, exist_ok=True)
        
        # Create full paths for all files within the Change_Form folder
        self.questions_file = os.path.join(self.data_folder, questions_file)
        self.csv_file = os.path.join(self.data_folder, csv_file)
        self.description_file = os.path.join(self.data_folder, description_file)
        self.remote_link_file = os.path.join(self.data_folder, "Remote_Link.txt")
        
        # Print file locations to console
        print("\nFile locations:")
        print(f"Questions file: {self.questions_file}")
        print(f"Responses CSV: {self.csv_file}")
        print(f"Description file: {self.description_file}")
        print(f"Remote link file: {self.remote_link_file}")
        print(f"VLC folder: {self.vlc_folder}\n")
        
        self.questions = []
        self.question_modifiers = []
        self.description = ""
        self.entries = []
        self.checkboxes = []
        self.checkbox_vars = []
        
        # Create default files if they don't exist
        self.create_default_files()
        
        # Load questions and description from files
        if not self.load_questions():
            return  # Stop initialization if questions couldn't be loaded
        self.load_description()
        
        # Create the form (this should be after all initializations)
        self.create_form()
        
        # Bind the resize event
        self.root.bind('<Configure>', self.on_window_resize)
        
        # Initialize pygame mixer for audio
        pygame.mixer.init()
        
        # Store currently playing media
        self.currently_playing = None
        self.media_window = None
    
    def create_default_files(self):
        # Create default Questions.txt if it doesn't exist
        if not os.path.exists(self.questions_file):
            default_questions = """What is your name?<text>
            
What is your email address?

What is your age?<number>
            
Please describe your experience.<Long>

Do you agree to the terms?<checkmark>"""
            with open(self.questions_file, 'w') as f:
                f.write(default_questions)
            messagebox.showinfo(
                "Info", 
                f"Created default questions file at:\n{self.questions_file}\n\n"
                "You can edit this file to change the form questions."
            )
        
        # Create default Description.txt if it doesn't exist
        if not os.path.exists(self.description_file):
            default_description = "Please fill out this form with your information."
            with open(self.description_file, 'w') as f:
                f.write(default_description)
            messagebox.showinfo(
                "Info", 
                f"Created default description file at:\n{self.description_file}\n\n"
                "You can edit this file to change the form description."
            )
        
        # Create default Remote_Link.txt if it doesn't exist
        if not os.path.exists(self.remote_link_file):
            with open(self.remote_link_file, 'w') as f:
                pass  # Create empty file
    
    def load_remote_link(self):
        """Load the remote link from file if it exists and is valid"""
        try:
            if os.path.exists(self.remote_link_file):
                with open(self.remote_link_file, 'r') as file:
                    link = file.read().strip()
                    if link:  # Only return if there's actually a link
                        return link
            return None
        except Exception as e:
            messagebox.showwarning("Warning", f"Could not load remote link: {str(e)}")
            return None
    
    def is_web_url(self, link):
        """Check if the link is a web URL (http/https)"""
        return link.lower().startswith(('http://', 'https://'))

    def save_to_remote(self, data, remote_link):
        """Attempt to save data to a remote location (either web URL or local path)"""
        try:
            if self.is_web_url(remote_link):
                # Handle web URL
                response = requests.post(remote_link, json=data)
                if response.status_code == 200:
                    return True, "Data saved remotely successfully!"
                else:
                    return False, f"Remote server returned status code {response.status_code}"
            else:
                # Handle local path
                try:
                    # Ensure directory exists
                    os.makedirs(os.path.dirname(remote_link), exist_ok=True)
                    
                    # Prepare CSV data
                    file_exists = os.path.isfile(remote_link)
                    with open(remote_link, 'a', newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        
                        if not file_exists:
                            header_questions = data['questions'].copy()
                            header_questions.append("Timestamp")
                            writer.writerow(header_questions)
                        
                        row = data['responses'].copy()
                        row.append(data['timestamp'])
                        writer.writerow(row)
                    
                    return True, f"Data saved to local path: {remote_link}"
                except Exception as e:
                    return False, f"Failed to save to local path: {str(e)}"
        except Exception as e:
            return False, f"Failed to save: {str(e)}"
    
    def load_questions(self):
        try:
            with open(self.questions_file, 'r') as file:
                content = file.read()
                # Split by lines and remove empty lines
                lines = [line.strip() for line in content.split('\n') if line.strip()]
                
                self.form_items = []  # Combined list of questions and media items with their order preserved
                
                current_question = ""
                for line in lines:
                    # If the line starts with whitespace, it's part of the previous question
                    if not line.startswith((' ', '\t')) and current_question:
                        # Process the accumulated question
                        self._process_question_or_media(current_question)
                        current_question = line
                    else:
                        if current_question:
                            current_question += " " + line
                        else:
                            current_question = line
                
                # Process the last question
                if current_question:
                    self._process_question_or_media(current_question)
                    
            if not self.form_items:
                messagebox.showerror("Error", "No items found in the questions file.")
                self.root.destroy()
                return False
                
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load questions: {str(e)}")
            self.root.destroy()
            return False

    def _process_question_or_media(self, text):
        """Process a line as either a question or media item"""
        modifiers = []
        item_text = text
        
        # Extract modifiers at the end
        mod_match = re.search(r'\s*<([^>]+)>\s*$', item_text)
        if mod_match:
            modifiers = [m.strip().lower() for m in mod_match.group(1).split(',')]
            item_text = re.sub(r'\s*<[^>]+>\s*$', '', item_text).strip()
        
        # Store item with its type (media or question)
        if 'media' in modifiers:
            self.form_items.append(('media', item_text, modifiers))
        else:
            self.form_items.append(('question', item_text, modifiers))
        
    def load_description(self):
        try:
            if os.path.exists(self.description_file):
                with open(self.description_file, 'r') as file:
                    self.description = file.read().strip()
        except Exception as e:
            messagebox.showwarning("Warning", f"Could not load description: {str(e)}")
            self.description = ""
    
    def create_form(self):
        # Create main frame with padding
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Add title
        title_label = tk.Label(self.main_frame, 
                            text="Please Answer the Following Questions",
                            font=("Times New Roman", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Add description if available
        if self.description:
            description_label = tk.Label(self.main_frame, 
                                    text=self.description,
                                    wraplength=600, 
                                    justify="left", 
                                    anchor="w")
            description_label.pack(pady=(0, 20), fill="x")
        
        # Create canvas with scrollbar
        self.canvas = tk.Canvas(self.main_frame, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.main_frame, 
                                    orient="vertical", 
                                    command=self.canvas.yview)
        
        # Pack scrollbar first (important for proper sizing)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Create scrollable frame with minimum width
        self.scrollable_frame = tk.Frame(self.canvas, width=600)
        self.canvas_frame = self.canvas.create_window((0, 0), 
                                                    window=self.scrollable_frame, 
                                                    anchor="nw")
        
        # Configure scrolling behavior
        def _configure_scrollregion(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            self.canvas.itemconfig(self.canvas_frame, width=max(event.width, 600))
        
        self.scrollable_frame.bind("<Configure>", _configure_scrollregion)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Configure grid weights
        self.scrollable_frame.columnconfigure(0, weight=1)
        
        # Reset form element lists
        self.entries = []
        self.checkboxes = []
        self.checkbox_vars = []
        self.questions = []
        self.question_modifiers = []
        
        row_counter = 0
        
        # Create form elements with wider fields
        for item_type, item_text, modifiers in self.form_items:
            if item_type == 'media':
                self._add_media_item(item_text, modifiers, row_counter)
                row_counter += 1
            else:
                self.questions.append(item_text)
                self.question_modifiers.append(modifiers)
                
                # Question label
                question_label = tk.Label(self.scrollable_frame, 
                                        text=item_text, 
                                        anchor="w", 
                                        justify="left")
                question_label.grid(row=row_counter, 
                                column=0, 
                                sticky="ew", 
                                pady=(10, 0))
                row_counter += 1
                
                # Input field container
                entry_frame = tk.Frame(self.scrollable_frame)
                entry_frame.grid(row=row_counter, 
                                column=0, 
                                sticky="ew", 
                                pady=(5, 10))
                entry_frame.columnconfigure(0, weight=1)
                row_counter += 1
                
                if 'checkmark' in modifiers:
                    var = tk.BooleanVar(value=False)
                    checkbox = tk.Checkbutton(entry_frame, variable=var)
                    checkbox.grid(row=0, column=0, sticky="w")
                    self.checkboxes.append(checkbox)
                    self.checkbox_vars.append(var)
                    self.entries.append(None)
                elif 'long' in modifiers:
                    # Wider text area (60 characters wide, 5 lines tall)
                    entry = Text(entry_frame, 
                            height=5, 
                            width=60,
                            wrap=tk.WORD, 
                            padx=5, 
                            pady=5)
                    entry.grid(row=0, 
                            column=0, 
                            sticky="nsew", 
                            padx=(0, 20))
                    self.entries.append(entry)
                else:
                    # Wider entry field (60 characters wide)
                    entry = tk.Entry(entry_frame, 
                                width=60)
                    entry.grid(row=0, 
                            column=0, 
                            sticky="ew", 
                            ipady=2, 
                            padx=(0, 20))
                    self.entries.append(entry)
        
        # Submit button
        self.submit_button = tk.Button(self.scrollable_frame, 
                                    text="Submit", 
                                    command=self.submit_form)
        self.submit_button.grid(row=row_counter, 
                            column=0, 
                            sticky="w", 
                            pady=20)
        
        # Configure final row weight
        self.scrollable_frame.rowconfigure(row_counter, weight=1)
        
        # Initial configuration
        self.root.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def _add_media_item(self, media_file, modifiers, row_counter):
        """Add a media item to the form"""
        media_path = os.path.join(self.media_folder, media_file)
        
        if os.path.exists(media_path):
            try:
                if media_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    # Display image
                    img = Image.open(media_path)
                    # Maintain aspect ratio while limiting size
                    max_size = (400, 400)
                    img.thumbnail(max_size, Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    
                    media_label = tk.Label(self.scrollable_frame, image=photo)
                    media_label.image = photo  # Keep reference
                    media_label.grid(row=row_counter, column=0, pady=10)
                    
                elif media_file.lower().endswith('.mp4'):
                    # Video placeholder
                    media_label = tk.Label(self.scrollable_frame, 
                                        text=f"Video: {media_file} (double-click to play)",
                                        fg="blue", cursor="hand2")
                    media_label.bind("<Double-Button-1>", lambda e, f=media_path: self.play_video(f))
                    media_label.grid(row=row_counter, column=0, pady=10)
                    
                elif media_file.lower().endswith('.mp3'):
                    # Audio placeholder
                    media_label = tk.Label(self.scrollable_frame, 
                                        text=f"Audio: {media_file} (click to play)",
                                        fg="blue", cursor="hand2")
                    media_label.bind("<Button-1>", lambda e, f=media_path: self.play_audio(f))
                    media_label.grid(row=row_counter, column=0, pady=10)
            except Exception as e:
                error_label = tk.Label(self.scrollable_frame, 
                                    text=f"Error loading media: {media_file}\n{str(e)}",
                                    fg="red")
                error_label.grid(row=row_counter, column=0, pady=10)
        else:
            error_label = tk.Label(self.scrollable_frame, 
                                text=f"Media file not found: {media_file}",
                                fg="red")
            error_label.grid(row=row_counter, column=0, pady=10)
    
    def play_video(self, video_path):
        """Play video using portable VLC player"""
        try:
            # Stop any currently playing media
            self.stop_media()
            
            # Determine VLC executable path based on OS
            if platform.system() == 'Windows':
                vlc_path = os.path.join(self.vlc_folder, 'VLCPortable.exe')
            elif platform.system() == 'Darwin':  # macOS
                vlc_path = os.path.join(self.vlc_folder, 'VLC.app', 'Contents', 'MacOS', 'VLC')
            else:  # Linux
                vlc_path = os.path.join(self.vlc_folder, 'vlc')
            
            if not os.path.exists(vlc_path):
                messagebox.showerror("Error", "VLC player not found in the VLCPortable folder")
                return
            
            # Launch VLC with the video file
            subprocess.Popen([vlc_path, video_path])
            
        except Exception as e:
            messagebox.showerror("Playback Error", f"Could not play video: {str(e)}")

    def play_audio(self, audio_path):
        """Play audio using portable VLC player"""
        try:
            # Stop any currently playing audio
            self.stop_media()
            
            # Determine VLC executable path based on OS
            if platform.system() == 'Windows':
                vlc_path = os.path.join(self.vlc_folder, 'VLCPortable.exe')
            elif platform.system() == 'Darwin':  # macOS
                vlc_path = os.path.join(self.vlc_folder, 'VLC.app', 'Contents', 'MacOS', 'VLC')
            else:  # Linux
                vlc_path = os.path.join(self.vlc_folder, 'vlc')
            
            if not os.path.exists(vlc_path):
                messagebox.showerror("Error", "VLC player not found in the VLCPortable folder")
                return
            
            # Launch VLC with the audio file
            subprocess.Popen([vlc_path, audio_path])
            
        except Exception as e:
            messagebox.showerror("Playback Error", f"Could not play audio: {str(e)}")
            
    def stop_media(self):
        """Stop any currently playing media (just cleanup references)"""
        self.currently_playing = None
        if hasattr(self, 'media_window') and self.media_window and tk.Toplevel.winfo_exists(self.media_window):
            self.media_window.destroy()    

    def on_window_resize(self, event):
        if event.widget == self.root:
            # Simply update the scrollregion
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def update_scrollregion(self):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def validate_response(self, response, modifiers, question):
        """Validate the response based on modifiers"""
        if not response.strip() and 'required' in modifiers:
            return False, "This field is required"
            
        if not response.strip():  # Skip validation for empty non-required fields
            return True, ""
            
        if 'integer' in modifiers:
            if not response.strip().isdigit():
                return False, "Please enter a valid integer"
                
        if 'number' in modifiers:
            try:
                float(response.strip())
            except ValueError:
                return False, "Please enter a valid number"
                
        if 'text' in modifiers:
            if any(char.isdigit() for char in response.strip()):
                return False, "This field should contain only text"
                
        return True, ""
    
    def submit_form(self):
        # Collect responses
        responses = []
        empty_fields = []
        
        # Initialize indices for checkboxes and entries
        checkbox_index = 0
        entry_index = 0
        
        for i, (question, modifiers) in enumerate(zip(self.questions, self.question_modifiers)):
            if 'checkmark' in modifiers:
                # Handle checkbox
                response = str(self.checkbox_vars[checkbox_index].get())
                checkbox_index += 1
            else:
                # Handle text entry
                if entry_index < len(self.entries):
                    entry = self.entries[entry_index]
                    if isinstance(entry, Text):
                        response = entry.get("1.0", "end-1c")
                    elif entry is not None:  # Regular entry
                        response = entry.get()
                    else:
                        response = ""
                    entry_index += 1
                else:
                    response = ""
            
            # Check for empty fields (for warning)
            if not response.strip() and 'required' not in modifiers:
                empty_fields.append(question)
            
            # Validate response
            is_valid, error_msg = self.validate_response(response, modifiers, question)
            if not is_valid:
                messagebox.showerror("Validation Error", f"Question: {question}\nError: {error_msg}")
                return
            
            responses.append(response)
    
        # Check if any required fields are empty
        for i, (response, modifiers, question) in enumerate(zip(responses, self.question_modifiers, self.questions)):
            if 'required' in modifiers and not response.strip():
                if not messagebox.askyesno("Warning", f"Required field '{question}' is empty. Submit anyway?"):
                    return
        
        # Warn about empty non-required fields
        if empty_fields:
            warning_msg = "The following non-required fields are empty:\n\n" + "\n".join(f"- {q}" for q in empty_fields)
            warning_msg += "\n\nDo you want to submit anyway?"
            if not messagebox.askyesno("Empty Fields Warning", warning_msg):
                return
        
        # Add timestamp to responses
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        responses.append(timestamp)
        
        # Prepare data for saving
        data = {
            "questions": self.questions,
            "responses": responses[:-1],  # Exclude timestamp
            "timestamp": timestamp
        }
        
        # Check for remote link
        remote_link = self.load_remote_link()
        if remote_link:
            # Try to save to remote location or local path
            success, message = self.save_to_remote(data, remote_link)
            if success:
                messagebox.showinfo("Success", message)
            else:
                # Fall back to local saving if remote fails
                if messagebox.askyesno("Save Failed", 
                                    f"{message}\n\nWould you like to save to default location instead?"):
                    self.save_to_local(responses)
        else:
            # Save locally if no remote link
            self.save_to_local(responses)
            
    def save_to_local(self, responses):
        """Save responses to local CSV file"""
        try:
            file_exists = os.path.isfile(self.csv_file)
            with open(self.csv_file, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                
                if not file_exists:
                    header_questions = self.questions.copy()
                    header_questions.append("Timestamp")
                    writer.writerow(header_questions)
                
                writer.writerow(responses)
                
            messagebox.showinfo("Success", "Your responses have been saved locally!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save responses locally: {str(e)}")
    
    def save_to_remote(self, data, remote_link):
        """Attempt to save data to a remote location (either web URL or local path)"""
        try:
            if self.is_web_url(remote_link):
                # Handle web URL
                response = requests.post(remote_link, json=data)
                if response.status_code == 200:
                    return True, "Data saved remotely successfully!"
                else:
                    return False, f"Remote server returned status code {response.status_code}"
            else:
                # Handle local path
                try:
                    # Check if the path is a directory
                    if os.path.isdir(remote_link):
                        # Use a consistent filename in the directory
                        filename = "Responses.csv"
                        full_path = os.path.join(remote_link, filename)
                    else:
                        # Use the path as is (assuming it includes a filename)
                        full_path = remote_link
                        # Ensure directory exists
                        os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    
                    # Prepare CSV data
                    file_exists = os.path.isfile(full_path)
                    with open(full_path, 'a', newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        
                        if not file_exists:
                            header_questions = data['questions'].copy()
                            header_questions.append("Timestamp")
                            writer.writerow(header_questions)
                        
                        row = data['responses'].copy()
                        row.append(data['timestamp'])
                        writer.writerow(row)
                    
                    return True, f"Data saved to local path: {full_path}"
                except Exception as e:
                    return False, f"Failed to save to local path: {str(e)}"
        except Exception as e:
            return False, f"Failed to save: {str(e)}"
        
    def clear_form(self):
        """Clear all form entries"""
        checkbox_index = 0
        for i, entry in enumerate(self.entries):
            if 'checkmark' in self.question_modifiers[i]:
                self.checkbox_vars[checkbox_index].set(False)
                checkbox_index += 1
            elif entry is not None:
                if isinstance(entry, Text):
                    entry.delete("1.0", tk.END)
                else:
                    entry.delete(0, tk.END)

def main():
    # Configuration - just filenames without paths
    questions_file = "Questions.txt"
    csv_file = "Responses.csv"
    description_file = "Description.txt"
    window_width = 800
    window_height = 600
    
    # Create Tkinter window
    root = tk.Tk()
    app = FormApplication(root, questions_file, csv_file, description_file, window_width, window_height)
    root.mainloop()

if __name__ == "__main__":
    main()