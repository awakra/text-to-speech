import asyncio
from .pdf_extractor import extract_text_from_pdf  # Adicione o '.' aqui
from .speech_synthesizer import synthesize_speech, DEFAULT_VOICE, DEFAULT_OUTPUT_FILE

async def convert_pdf_to_speech(
    pdf_file_path: str,
    output_audio_path: str = DEFAULT_OUTPUT_FILE,
    voice: str = DEFAULT_VOICE
) -> tuple[bool, str]:
    """
    Orchestrates the conversion of a PDF file to a speech audio file.

    It first extracts text from the PDF and then synthesizes speech from the extracted text.

    Args:
        pdf_file_path (str): The path to the input PDF file.
        output_audio_path (str, optional): The path where the output audio file (e.g., MP3)
                                           will be saved. Defaults to the DEFAULT_OUTPUT_FILE
                                           defined in speech_synthesizer.
        voice (str, optional): The voice to be used for speech synthesis. Defaults to the
                               DEFAULT_VOICE defined in speech_synthesizer.

    Returns:
        tuple[bool, str]: A tuple containing:
                          - bool: True if the conversion was successful, False otherwise.
                          - str: A message indicating the result or error.
    """
    print(f"Starting PDF to speech conversion for: {pdf_file_path}")

    # Step 1: Extract text from PDF
    try:
        print("Extracting text from PDF...")
        extracted_text = extract_text_from_pdf(pdf_file_path)
        if not extracted_text:
            message = f"No text could be extracted from '{pdf_file_path}' or the PDF is empty."
            print(message)
            return False, message
        print(f"Text extracted successfully. Length: {len(extracted_text)} characters.")
        # For brevity in logs, let's print only a snippet
        print(f"Extracted text snippet: '{extracted_text[:100]}...'")
    except FileNotFoundError:
        message = f"Error: PDF file not found at '{pdf_file_path}'."
        print(message)
        return False, message
    except Exception as e:
        message = f"An unexpected error occurred during PDF text extraction: {e}"
        print(message)
        return False, message

    # Step 2: Synthesize speech from extracted text
    try:
        print(f"\nSynthesizing speech to '{output_audio_path}' using voice '{voice}'...")
        success = await synthesize_speech(
            text=extracted_text,
            output_filename=output_audio_path,
            voice=voice
        )

        if success:
            message = f"Successfully converted PDF to speech. Audio saved to '{output_audio_path}'."
            print(message)
            return True, message
        else:
            message = "Speech synthesis failed. Please check earlier logs from speech_synthesizer for details."
            print(message)
            return False, message
    except Exception as e:
        message = f"An unexpected error occurred during speech synthesis orchestration: {e}"
        print(message)
        return False, message

async def main_test_controller():
    """
    A simple main function to test the PDF to speech conversion process.
    For this test to run, you'll need a sample PDF file.
    Create a dummy PDF, for example, 'sample.pdf' in the root of your project.
    """
    # Create a dummy PDF for testing if it doesn't exist
    # You should replace 'sample.pdf' with an actual PDF file for a real test.
    sample_pdf_path = "../sample.pdf"
    # For this test, let's ensure a dummy PDF exists.
    # In a real scenario, the user provides this.
    try:
        with open(sample_pdf_path, "rb") as f:
            pass
        print(f"Using existing PDF for test: {sample_pdf_path}")
    except FileNotFoundError:
        try:
            from PyPDF2 import PdfWriter, PageRange # Using PyPDF2 to create a dummy PDF
            # You might need to install PyPDF2: pip install PyPDF2
            # This is just for the sake of a self-contained test example.
            # In a real application, the PDF would be provided by the user.
            writer = PdfWriter()
            # Add a blank page (or some text if you prefer)
            # Creating a truly valid PDF programmatically with text can be complex,
            # so for a simple test, a PDF with metadata or a blank page might suffice
            # or better, the user should provide their own sample.pdf
            # For now, let's assume the user will create a 'sample.pdf'
            # If you want to create one with text:
            # import io
            # from reportlab.pdfgen import canvas
            # from reportlab.lib.pagesizes import letter
            # packet = io.BytesIO()
            # can = canvas.Canvas(packet, pagesize=letter)
            # can.drawString(72, 720, "This is a sample PDF for testing the text-to-speech application.")
            # can.save()
            # packet.seek(0)
            # from PyPDF2 import PdfReader
            # new_pdf = PdfReader(packet)
            # for page in new_pdf.pages:
            #    writer.add_page(page)
            # with open(sample_pdf_path, "wb") as f:
            #    writer.write(f)
            print(f"'{sample_pdf_path}' not found. Please create a sample PDF named 'sample.pdf' in the project root for testing.")
            print("For example, a simple one-page PDF with some text.")
            return
        except ImportError:
            print("PyPDF2 is not installed. Cannot create a dummy PDF for testing.")
            print(f"Please create a sample PDF named '{sample_pdf_path}' in the project root for testing.")
            return
        except Exception as e:
            print(f"Could not create dummy PDF: {e}")
            print(f"Please create a sample PDF named '{sample_pdf_path}' in the project root for testing.")
            return


    output_audio = "controller_test_output.mp3"
    # You can try a different voice here if you know one from `edge-tts --list-voices`
    # e.g., "en-GB-LibbyNeural" for a British voice
    selected_voice = "en-US-JennyNeural"

    print(f"\n--- Running Controller Test ---")
    print(f"Input PDF: {sample_pdf_path}")
    print(f"Output Audio: {output_audio}")
    print(f"Selected Voice: {selected_voice}")
    print(f"-----------------------------\n")

    success, message = await convert_pdf_to_speech(
        pdf_file_path=sample_pdf_path,
        output_audio_path=output_audio,
        voice=selected_voice
    )

    print(f"\n--- Controller Test Result ---")
    print(f"Success: {success}")
    print(f"Message: {message}")
    print(f"------------------------------\n")

if __name__ == "__main__":
    # This allows testing core/main_controller.py directly
    # Ensure you have a 'sample.pdf' in your project's root directory.
    # You might need to install PyPDF2 if you want the dummy PDF creation to work:
    # pip install PyPDF2
    # However, it's better if you provide your own 'sample.pdf'.
    try:
        asyncio.run(main_test_controller())
    except KeyboardInterrupt:
        print("\nController test interrupted by user.")