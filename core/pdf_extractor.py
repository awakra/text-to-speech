# core/pdf_extractor.py

import PyPDF2

def extract_text_from_pdf(pdf_file_path: str) -> str | None:
    """
    Extracts all text content from a given PDF file.

    Args:
        pdf_file_path (str): The path to the PDF file.

    Returns:
        str | None: The extracted text as a single string, or None if
                    the file cannot be opened, is encrypted, or an error occurs.
    """
    try:
        with open(pdf_file_path, 'rb') as pdf_file_obj:
            pdf_reader = PyPDF2.PdfReader(pdf_file_obj)

            # Check if the PDF is encrypted
            if pdf_reader.is_encrypted:
                try:
                    # Attempt to decrypt with an empty password
                    # For PDFs with actual passwords, this would need to be handled differently
                    pdf_reader.decrypt('')
                except Exception as e:
                    print(f"Error: Could not decrypt PDF '{pdf_file_path}'. It might be password-protected. Error: {e}")
                    return None

            text_content = []
            for page_num in range(len(pdf_reader.pages)):
                page_obj = pdf_reader.pages[page_num]
                text_content.append(page_obj.extract_text())

            full_text = "\n".join(text_content).strip()
            if not full_text:
                print(f"Warning: No text found in '{pdf_file_path}', or text extraction yielded an empty string.")
            return full_text
    except FileNotFoundError:
        print(f"Error: The file '{pdf_file_path}' was not found.")
        return None
    except PyPDF2.errors.PdfReadError as e:
        print(f"Error: Could not read PDF file '{pdf_file_path}'. It might be corrupted or not a valid PDF. Details: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while processing '{pdf_file_path}': {e}")
        return None

if __name__ == '__main__':
    # This is a simple test block that runs if you execute this script directly.
    # For this to work, you'll need a sample PDF.
    # Let's assume you have a 'sample.pdf' in the same directory as this script
    # or provide a full path to a test PDF.

    # Create a dummy sample.pdf for testing if it doesn't exist
    # For a more robust test, replace this with a real PDF.
    test_pdf_path = "sample_for_extractor_test.pdf"
    try:
        with open(test_pdf_path, "rb") as f:
            print(f"Using existing PDF for test: {test_pdf_path}")
    except FileNotFoundError:
        try:
            # Create a very simple PDF with one line of text using PyPDF2
            # This requires reportlab to be installed: pip install reportlab
            import io
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            from PyPDF2 import PdfWriter, PdfReader

            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)
            can.drawString(72, 750, "This is a test sentence for the PDF extractor module.")
            can.drawString(72, 730, "Hello world from PyPDF2 and ReportLab!")
            can.save()
            packet.seek(0) # Move the "cursor" to the beginning of the BytesIO stream

            new_pdf_reader = PdfReader(packet)
            writer = PdfWriter()
            for page in new_pdf_reader.pages:
                writer.add_page(page)

            with open(test_pdf_path, "wb") as f_out:
                writer.write(f_out)
            print(f"Created a dummy PDF for testing: {test_pdf_path}")

        except ImportError:
            print(f"'{test_pdf_path}' not found, and reportlab is not installed to create a dummy one.")
            print("Please create a sample PDF named 'sample_for_extractor_test.pdf' or use an existing PDF for testing.")
            test_pdf_path = None
        except Exception as e:
            print(f"Could not create dummy PDF: {e}")
            test_pdf_path = None


    if test_pdf_path:
        print(f"\nAttempting to extract text from: '{test_pdf_path}'")
        extracted_text = extract_text_from_pdf(test_pdf_path)

        if extracted_text is not None:
            print("\n--- Extracted Text ---")
            print(extracted_text)
            print("----------------------")
            print(f"\nSuccessfully extracted {len(extracted_text)} characters.")
        else:
            print("\nText extraction failed or returned no text.")

    # Test with a non-existent file
    print("\nAttempting to extract text from a non-existent file:")
    non_existent_text = extract_text_from_pdf("non_existent_file.pdf")
    if non_existent_text is None:
        print("Correctly handled non-existent file.")

    # You might also want to test with an encrypted PDF (without password)
    # and a corrupted PDF if you have samples.