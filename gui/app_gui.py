import tkinter as tk
from tkinter import filedialog, messagebox
import asyncio
import threading
import os 

import sys
# Get the absolute path of the project's root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.main_controller import convert_pdf_to_speech
import edge_tts 
from core.speech_synthesizer import DEFAULT_VOICE 

class PdfToSpeechApp:
    """
    A Tkinter-based GUI application for converting PDF files to speech.
    """
    def __init__(self, root_window):
        """
        Initializes the PdfToSpeechApp.

        Args:
            root_window (tk.Tk): The main window for the application.
        """
        self.root = root_window
        self.root.title("PDF to Speech Converter")
        self.root.geometry("600x500") # Slightly increase height for the new dropdown

        self.selected_pdf_path = tk.StringVar()
        self.selected_language_display = tk.StringVar() # For the user-friendly language name
        self.selected_voice = tk.StringVar()
        self.status_message = tk.StringVar()

        # Mapping of language display names to their codes (e.g., "en", "pt-BR")
        # You can expand this list. Use locale codes that edge-tts understands.
        self.available_languages_map = {
            "English (US)": "en-US",
            "English (UK)": "en-GB",
            "Portuguese (Brazil)": "pt-BR",
            "Portuguese (Portugal)": "pt-PT",
            "Spanish (Spain)": "es-ES",
            "Spanish (Mexico)": "es-MX",
            "French (France)": "fr-FR",
            "German (Germany)": "de-DE",
        }
        # Map for loaded voices (display name -> short voice name)
        self.loaded_voices_map = {}

        self._setup_ui()
        # Load voices for the initially selected language
        if self.available_languages_map:
            initial_lang_display = list(self.available_languages_map.keys())[0]
            self.selected_language_display.set(initial_lang_display)
            self._on_language_selected(initial_lang_display) # Triggers voice loading

    def _setup_ui(self):
        """
        Sets up the user interface elements of the application.
        """
        # --- PDF File Selection ---
        frame_pdf = tk.LabelFrame(self.root, text="PDF File", padx=10, pady=10)
        frame_pdf.pack(padx=10, pady=10, fill="x")

        lbl_pdf_path = tk.Label(frame_pdf, text="Selected PDF:")
        lbl_pdf_path.pack(side=tk.LEFT, padx=(0, 5))

        ent_pdf_path = tk.Entry(frame_pdf, textvariable=self.selected_pdf_path, width=50, state='readonly')
        ent_pdf_path.pack(side=tk.LEFT, expand=True, fill="x", padx=(0, 5))

        btn_browse_pdf = tk.Button(frame_pdf, text="Browse...", command=self._browse_pdf_file)
        btn_browse_pdf.pack(side=tk.LEFT)

        # --- Language Selection ---
        frame_language = tk.LabelFrame(self.root, text="Language Selection", padx=10, pady=10)
        frame_language.pack(padx=10, pady=10, fill="x")

        lbl_language = tk.Label(frame_language, text="Select Language:")
        lbl_language.pack(side=tk.LEFT, padx=(0, 5))

        language_names = list(self.available_languages_map.keys())
        if not language_names: # Fallback if the map is empty for some reason
            language_names = ["N/A"]

        self.language_options_menu = tk.OptionMenu(
            frame_language,
            self.selected_language_display,
            *language_names, # Unpack names for OptionMenu
            command=self._on_language_selected # Command to execute on selection
        )
        self.language_options_menu.config(width=40)
        self.language_options_menu.pack(side=tk.LEFT, expand=True, fill="x")


        # --- Voice Selection ---
        frame_voice = tk.LabelFrame(self.root, text="Voice Selection", padx=10, pady=10)
        frame_voice.pack(padx=10, pady=10, fill="x")

        lbl_voice = tk.Label(frame_voice, text="Select Voice:")
        lbl_voice.pack(side=tk.LEFT, padx=(0, 5))

        self.voice_options_menu = tk.OptionMenu(frame_voice, self.selected_voice, "Select a language first...")
        self.voice_options_menu.config(width=40)
        self.voice_options_menu.pack(side=tk.LEFT, expand=True, fill="x")
        self.voice_options_menu.config(state=tk.DISABLED) # Starts disabled


        # --- Conversion Control ---
        frame_convert = tk.Frame(self.root, padx=10, pady=10)
        frame_convert.pack(fill="x")

        self.btn_convert = tk.Button(frame_convert, text="Convert to Speech", command=self._start_conversion_thread, font=("Arial", 12, "bold"), bg="lightblue")
        self.btn_convert.pack(pady=10)
        self.btn_convert.config(state=tk.DISABLED) # Disabled until a PDF and voice are selected

        # --- Status Display ---
        frame_status = tk.LabelFrame(self.root, text="Status", padx=10, pady=10)
        frame_status.pack(padx=10, pady=10, fill="both", expand=True)

        lbl_status = tk.Label(frame_status, textvariable=self.status_message, wraplength=550, justify=tk.LEFT)
        lbl_status.pack(anchor="nw")
        self.status_message.set("Please select a PDF file and language to begin.")

    def _on_language_selected(self, selected_lang_display_name: str):
        """
        Called when a language is selected. Triggers loading of voices for that language.
        """
        language_code = self.available_languages_map.get(selected_lang_display_name)
        if language_code:
            self.status_message.set(f"Loading voices for {selected_lang_display_name}...")
            # Clear and disable the voice menu while loading
            self.selected_voice.set("Loading...")
            voice_menu = self.voice_options_menu["menu"]
            voice_menu.delete(0, "end")
            self.voice_options_menu.config(state=tk.DISABLED)
            self.btn_convert.config(state=tk.DISABLED) # Disable conversion button as well

            self._load_voices_for_language(language_code)
        else:
            self.status_message.set(f"Error: Language code not found for {selected_lang_display_name}")
            self.voice_options_menu.config(state=tk.DISABLED)


    def _load_voices_for_language(self, language_code: str):
        """
        Loads available voices for the specified language code asynchronously.
        """
        def fetch_and_update_voices_thread():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                # Use edge_tts.list_voices() directly
                all_voices = loop.run_until_complete(edge_tts.list_voices())
                loop.close()

                # Filter voices by the main language part of the locale code
                # e.g., "en" for "en-US", "en-GB", etc.
                lang_prefix = language_code.split('-')[0].lower()
                language_specific_voices = [v for v in all_voices if v['Locale'].lower().startswith(lang_prefix)]


                if language_specific_voices:
                    self.loaded_voices_map = {
                        f"{v['Name']} ({v['Gender']})": v['ShortName']
                        for v in language_specific_voices
                    }
                    voice_display_names = list(self.loaded_voices_map.keys())
                    self.root.after(0, self._update_voice_menu, voice_display_names)
                    self.root.after(0, lambda: self.status_message.set(f"Voices loaded for {language_code}. Select a voice."))
                else:
                    self.root.after(0, self._update_voice_menu, []) # Empty list
                    self.root.after(0, lambda: self.status_message.set(f"No voices found for language: {language_code}."))

            except Exception as e:
                error_msg = f"Error loading voices: {e}"
                print(error_msg)
                self.root.after(0, lambda: self.status_message.set(error_msg))
                self.root.after(0, self._update_voice_menu, []) # Update menu to error state
            finally:
                # Enable conversion button if a PDF is already selected and voices are loaded
                if self.selected_pdf_path.get() and self.loaded_voices_map:
                     self.root.after(0, lambda: self.btn_convert.config(state=tk.NORMAL))


        threading.Thread(target=fetch_and_update_voices_thread, daemon=True).start()


    def _update_voice_menu(self, voice_display_names: list):
        """
        Updates the voice OptionMenu with the given list of voice names.
        This method must be called from the main Tkinter thread.
        """
        menu = self.voice_options_menu["menu"]
        menu.delete(0, "end") # Clear old options

        if voice_display_names:
            for name in voice_display_names:
                menu.add_command(label=name, command=lambda value=name: self.selected_voice.set(value))
            self.selected_voice.set(voice_display_names[0]) # Select the first voice by default
            self.voice_options_menu.config(state=tk.NORMAL)
            if self.selected_pdf_path.get(): # Enable convert button if PDF is selected
                self.btn_convert.config(state=tk.NORMAL)
        else:
            self.selected_voice.set("No voices available")
            self.voice_options_menu.config(state=tk.DISABLED)
            self.btn_convert.config(state=tk.DISABLED)


    def _browse_pdf_file(self):
        """
        Opens a file dialog to select a PDF file and updates the UI.
        """
        file_path = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=(("PDF Files", "*.pdf"), ("All Files", "*.*"))
        )
        if file_path:
            self.selected_pdf_path.set(file_path)
            base_name = os.path.basename(file_path)
            self.status_message.set(f"Selected: {base_name}. Ready if voice is selected.")
            # Enable convert button only if voices are loaded and a language is selected
            if self.loaded_voices_map and self.voice_options_menu["state"] == tk.NORMAL:
                self.btn_convert.config(state=tk.NORMAL)
        else:
            if not self.selected_pdf_path.get(): # If no file was previously selected
                self.status_message.set("No PDF file selected.")
                self.btn_convert.config(state=tk.DISABLED)


    def _start_conversion_thread(self):
        """
        Starts the PDF to speech conversion process in a new thread
        to prevent the GUI from freezing.
        """
        pdf_path = self.selected_pdf_path.get()
        if not pdf_path:
            messagebox.showerror("Error", "No PDF file selected.")
            return

        selected_voice_display = self.selected_voice.get()
        voice_short_name = self.loaded_voices_map.get(selected_voice_display)

        if not voice_short_name:
            messagebox.showerror("Error", "No voice selected or voice map is incorrect.")
            return

        output_dir = os.path.dirname(pdf_path)
        base_name_pdf = os.path.splitext(os.path.basename(pdf_path))[0]
        output_audio_path = os.path.join(output_dir, f"{base_name_pdf}_speech.mp3")

        self.status_message.set(f"Starting conversion for '{os.path.basename(pdf_path)}'...")
        self.btn_convert.config(state=tk.DISABLED)
        self.language_options_menu.config(state=tk.DISABLED)
        self.voice_options_menu.config(state=tk.DISABLED)


        thread = threading.Thread(
            target=self._run_conversion,
            args=(pdf_path, output_audio_path, voice_short_name),
            daemon=True
        )
        thread.start()

    def _run_conversion(self, pdf_path: str, output_audio_path: str, voice: str):
        """
        The actual conversion logic that runs in a separate thread.
        """
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.root.after(0, lambda: self.status_message.set(f"Extracting text from PDF '{os.path.basename(pdf_path)}'..."))
            success, message = loop.run_until_complete(
                convert_pdf_to_speech(pdf_path, output_audio_path, voice)
            )
            loop.close()

            if success:
                final_message = f"Success! Audio saved to: {output_audio_path}"
                self.root.after(0, lambda: messagebox.showinfo("Success", final_message))
            else:
                final_message = f"Conversion Failed: {message}"
                self.root.after(0, lambda: messagebox.showerror("Error", final_message))
            self.root.after(0, lambda: self.status_message.set(final_message))

        except Exception as e:
            error_msg = f"An unexpected error occurred in conversion thread: {e}"
            print(error_msg) # Log to console as well
            self.root.after(0, lambda: self.status_message.set(error_msg))
            self.root.after(0, lambda: messagebox.showerror("Critical Error", error_msg))
        finally:
            self.root.after(0, lambda: self.language_options_menu.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.voice_options_menu.config(state=tk.NORMAL if self.loaded_voices_map else tk.DISABLED))
            # Enable conversion button if a PDF is selected and voices are available
            if self.selected_pdf_path.get() and self.loaded_voices_map:
                 self.root.after(0, lambda: self.btn_convert.config(state=tk.NORMAL))
            else:
                self.root.after(0, lambda: self.btn_convert.config(state=tk.DISABLED))


def main_gui():
    """
    Main function to create and run the Tkinter application.
    """
    root = tk.Tk()
    app = PdfToSpeechApp(root)
    root.mainloop()

if __name__ == '__main__':
    main_gui()