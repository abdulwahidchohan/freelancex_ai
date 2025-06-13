import os
from dotenv import load_dotenv
from control import render_controls

# Load environment variables
load_dotenv()

# Check if Gemini API key is set
if not os.getenv("GEMINI_API_KEY"):
    raise ValueError("GEMINI_API_KEY environment variable is not set. Please set it in the .env file.")

# Render control panel
render_controls() 