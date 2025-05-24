# PDF to speech Converter

A Python application that converts text content from PDF files into audible speech using Microsoft Edge's online Text-to-Speech (TTS) services. It features a user-friendly graphical interface (GUI) built with Tkinter, allowing users to select languages and voices for the speech output.

## Features

- **PDF Text Extraction**: Accurately extracts textual content from PDF documents.
- **High-Quality Speech Synthesis**: Utilizes `edge-tts` for natural-sounding speech.
- **Language Selection**: Allows users to choose the desired language for the speech output.
- **Voice Selection**: Provides a list of available voices (male/female) based on the selected language.
- **Graphical User Interface**: Intuitive GUI for easy file selection, language/voice configuration, and conversion.
- **Asynchronous Operations**: Employs `asyncio` for non-blocking voice loading and speech synthesis, ensuring the GUI remains responsive.
- **MP3 Output**: Saves the generated speech as an `.mp3` audio file in the same directory as the input PDF.
- **Modular Design**: Code is organized into `core` (backend logic) and `gui` (frontend) packages for better maintainability and scalability.

## Project Structure

```
pdf-to-speech/
├── core/
│   ├── __init__.py
│   ├── pdf_extractor.py         # Module for extracting text from PDFs
│   ├── speech_synthesizer.py    # Module for converting text to speech (Edge TTS)
│   └── main_controller.py       # Module for orchestrating the conversion process
│
├── gui/
│   ├── __init__.py
│   └── app_gui.py               # Main application GUI (Tkinter)
│
├── .venv/                       # (Recommended) Python virtual environment
├── requirements.txt             # Project dependencies
└── README.md                    # This file
```

## Prerequisites

- Python 3.7+
- `pip` (Python package installer)
- An active internet connection (for `edge-tts` to access Microsoft's TTS services)

## Installation

### 1. Clone or Download the Project

```bash
# If you are using Git
git clone https://github.com/awakra/pdf-to-speech
cd pdf-to-speech
```

### 2. Navigate to Project Directory

```bash
cd path/to/your/pdf-to-speech
```

### 3. Create and Activate Virtual Environment

**For Windows:**

```bash
python -m venv .venv
.venv\Scripts\activate
```

**For macOS/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install Dependencies

First, create a `requirements.txt` file with the following content:

```
PyPDF2
edge-tts
```

Then install the dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Running the Application

1. Ensure your virtual environment is activated
2. Navigate to the project's root directory in your terminal
3. Run the application:

```bash
python gui/app_gui.py
```

### Using the GUI

1. Click the **"Browse..."** button to select a PDF file
2. Select your desired language from the **"Select Language"** dropdown menu (the voice list will update automatically)
3. Choose a voice from the **"Select Voice"** dropdown menu
4. Click the **"Convert to Speech"** button
5. The application will process the PDF and save an MP3 file (e.g., `yourfile_speech.mp3`) in the same directory as the original PDF
6. Status messages will guide you through the process and indicate success or any errors

## Modules Overview

### `gui/app_gui.py`

- Contains the `PdfToSpeechApp` class, which defines and manages all elements of the Tkinter-based graphical user interface
- Handles user interactions, file selection, language/voice selection, and triggers the conversion process
- Manages threading for background tasks to keep the UI responsive

### `core/pdf_extractor.py`

- Provides the `extract_text_from_pdf(pdf_path)` function
- Responsible for opening PDF files, reading their content, and extracting all text
- Includes error handling for file-related issues

### `core/speech_synthesizer.py`

- Contains the `synthesize_speech(text, voice, output_filename)` function
- Interfaces with the `edge-tts` library to convert the provided text into speech using the specified voice
- Handles the asynchronous nature of `edge-tts` and saves the audio output
- `DEFAULT_VOICE` is defined here as a fallback

### `core/main_controller.py`

- Features the `convert_pdf_to_speech(pdf_path, output_audio_path, voice)` function
- Acts as the central coordinator, linking the PDF extraction and speech synthesis processes
- Manages the overall workflow from receiving a PDF path to producing an audio file

## Troubleshooting

### Common Issues

- **Internet Connection**: Ensure you have an active internet connection as `edge-tts` requires access to Microsoft's online TTS services
- **PDF Format**: Some PDFs may not extract text properly if they contain only images or are password-protected
- **Audio Output**: The generated MP3 file will be saved in the same directory as the input PDF file

### Dependencies Issues

If you encounter issues with dependencies, try:

```bash
pip install --upgrade PyPDF2 edge-tts
```

## Acknowledgments

- Microsoft Edge TTS service for providing high-quality text-to-speech functionality
- PyPDF2 library for PDF text extraction capabilities
- Python Tkinter for the GUI framework
