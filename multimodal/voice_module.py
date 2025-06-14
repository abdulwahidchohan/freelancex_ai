# Voice I/O
def speak(text: str) -> bool:
    """
    Converts text to speech and outputs it through the system's audio.
    
    Args:
        text (str): The text to be converted to speech
        
    Returns:
        bool: True if speech was successful, False otherwise
    """
    try:
        print(f"VoiceModule: Speaking: '{text}'")
        # In a real scenario, this would use a text-to-speech API to generate audio.
        
        # Add error handling and validation
        if not text or not isinstance(text, str):
            raise ValueError("Invalid input: text must be a non-empty string")
            
        # Here you would add the actual TTS implementation
        # Example:
        # engine = pyttsx3.init()
        # engine.say(text)
        # engine.runAndWait()
        
        return True
    except Exception as e:
        print(f"VoiceModule Error: Failed to speak - {str(e)}")
        return False
