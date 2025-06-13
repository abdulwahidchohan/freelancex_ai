import google.generativeai as genai

# Configure Gemini Flash
genai.configure(api_key='YOUR_API_KEY') # Replace with actual API key or environment variable
model = genai.GenerativeModel('gemini-pro-vision')

# Parses UI screenshots
def parse_screenshot(screenshot_path):
    try:
        image = genai.upload_file(screenshot_path)
        response = model.generate_content(image)
        return response.text
    except Exception as e:
        print(f"Error parsing screenshot with Gemini Flash: {e}")
        return None
