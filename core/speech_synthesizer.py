# core/speech_synthesizer.py

import asyncio
import edge_tts
from edge_tts import VoicesManager

# A default voice to use if none is specified.
# You can find a list of available voices here:
# https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/language-support#text-to-speech
# Or by running: edge-tts --list-voices
DEFAULT_VOICE = "en-US-AriaNeural"
DEFAULT_OUTPUT_FILE = "output.mp3"

async def list_available_voices(language: str = None, gender: str = None, locale_str: str = None) -> list:
    """
    Retrieves a list of available voices from Edge TTS, optionally filtered by language, gender, or locale.

    Args:
        language (str, optional): Filter by language (e.g., "en" for English). Defaults to None.
        gender (str, optional): Filter by gender (e.g., "Male" or "Female"). Defaults to None.
        locale_str (str, optional): Filter by locale (e.g., "en-US"). Defaults to None.

    Returns:
        list: A list of voice details (dictionaries) matching the criteria.
              Each dictionary contains keys like 'Name', 'ShortName', 'Gender', 'Locale'.
    """
    try:
        voices_manager = await VoicesManager.create()
        voices = voices_manager.find_all()

        if language:
            voices = [v for v in voices if language.lower() in v['Locale'].lower().split('-')[0]]
        if gender:
            voices = [v for v in voices if gender.lower() == v['Gender'].lower()]
        if locale_str:
            voices = [v for v in voices if locale_str.lower() in v['Locale'].lower()]
        
        return voices
    except Exception as e:
        print(f"Error listing voices: {e}")
        return []

async def synthesize_speech(
    text: str,
    output_filename: str = DEFAULT_OUTPUT_FILE,
    voice: str = DEFAULT_VOICE
) -> bool:
    """
    Synthesizes speech from the given text using Edge TTS and saves it to an audio file.

    This function is asynchronous and needs to be run in an asyncio event loop.

    Args:
        text (str): The text content to be converted to speech.
        output_filename (str, optional): The path and name of the file where the audio
                                         will be saved. Defaults to "output.mp3".
        voice (str, optional): The voice to be used for synthesis.
                               Defaults to "en-US-AriaNeural".
                               A list of available voices can be obtained using `edge-tts --list-voices`
                               or the `list_available_voices` function.

    Returns:
        bool: True if synthesis was successful and the file was saved, False otherwise.
    """
    if not text.strip():
        print("Error: No text provided for speech synthesis.")
        return False

    try:
        print(f"Starting speech synthesis for: '{text[:50]}...'")
        print(f"Using voice: {voice}")
        print(f"Output file: {output_filename}")

        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_filename)
        
        print(f"Speech successfully synthesized and saved to {output_filename}")
        return True
    except edge_tts.exceptions.NoAudioReceived:
        print(f"Error: No audio received from Edge TTS. This might be due to an invalid voice or an issue with the service.")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during speech synthesis: {e}")
        return False

async def main_test():
    """
    A simple main function to test the speech synthesis functionality.
    This is useful for direct testing of this module.
    """
    sample_text = "Hello, this is a test of the Edge Text to Speech service using Python. I hope you find this useful!"
    
    print("Listing available English voices:")
    english_voices = await list_available_voices(language="en")
    if english_voices:
        for i, v in enumerate(english_voices[:5]): # Print first 5 English voices
            print(f"  {i+1}. {v['Name']} ({v['ShortName']}, {v['Gender']}, {v['Locale']})")
        
        # Pick a specific voice for testing if available, otherwise use default
        test_voice = "en-GB-SoniaNeural" # Example of a British English voice
        selected_voice_details = next((v for v in english_voices if v['ShortName'] == test_voice), None)
        
        if selected_voice_details:
            print(f"\nAttempting to use voice: {selected_voice_details['Name']}")
        else:
            print(f"\nVoice {test_voice} not found. Using default voice: {DEFAULT_VOICE}")
            test_voice = DEFAULT_VOICE # Fallback to default if specific voice not found
    else:
        print("No English voices found. Using default voice.")
        test_voice = DEFAULT_VOICE

    output_file = "test_speech.mp3"

    success = await synthesize_speech(sample_text, output_file, voice=test_voice)

    if success:
        print(f"Test synthesis successful. Check the file: {output_file}")
    else:
        print("Test synthesis failed.")

if __name__ == "__main__":
    # This block allows you to run this script directly for testing.
    try:
        asyncio.run(main_test())
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")