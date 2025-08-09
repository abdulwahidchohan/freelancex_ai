# FreelanceX.AI API Configuration Guide

## 🚀 Setting Up Multi-API Provider Support

Your FreelanceX.AI system now supports switching between OpenAI and Google Gemini APIs with automatic fallback functionality.

## 📋 Required Setup

### 1. Create Environment File

Create a `.env` file in your project root:

```bash
# On Windows
echo. > .env

# On macOS/Linux
touch .env
```

### 2. Add API Keys

Add the following to your `.env` file:

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Google Gemini API Configuration
GOOGLE_GEMINI_API_KEY=your_gemini_api_key_here

# API Provider Preferences
FREELANCEX_PRIMARY_API_PROVIDER=openai
FREELANCEX_FALLBACK_API_PROVIDER=gemini
FREELANCEX_ENABLE_API_FALLBACK=true

# System Configuration
FREELANCEX_KILL_SWITCH=false
FREELANCEX_ENV=development
```

### 3. Get API Keys

#### OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key and paste it in your `.env` file

#### Google Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and paste it in your `.env` file

## 🔧 Configuration Options

### Primary Provider
Set which API provider to use first:
```env
FREELANCEX_PRIMARY_API_PROVIDER=openai  # or "gemini"
```

### Fallback Provider
Set which API provider to use if primary fails:
```env
FREELANCEX_FALLBACK_API_PROVIDER=gemini  # or "openai"
```

### Enable/Disable Fallback
Control whether fallback is enabled:
```env
FREELANCEX_ENABLE_API_FALLBACK=true  # or "false"
```

## 🧪 Testing Your Configuration

Run the test script to verify your setup:

```bash
python test_api_switching.py
```

This will:
- Check if your API keys are configured
- Test each provider's connectivity
- Demonstrate the switching functionality
- Test a simple conversation

## 🔄 How API Switching Works

### Automatic Fallback Flow
```
1. User Request
   ↓
2. Try Primary Provider (OpenAI)
   ↓
3. Success? → Return Response
   ↓
4. Failure? → Try Fallback Provider (Gemini)
   ↓
5. Success? → Return Response
   ↓
6. Failure? → Try Any Available Provider
   ↓
7. All Failed? → Return Error Message
```

### Manual Switching
You can also manually switch providers using the API switcher:

```python
from fx_agents.api_switcher import switch_provider

# Switch to Gemini
result = switch_provider("gemini")

# Switch to OpenAI
result = switch_provider("openai")
```

## 🎯 Benefits of Multi-API Support

### 1. **Reliability**
- If one API is down, automatically switch to another
- No service interruption for users

### 2. **Cost Optimization**
- Use different providers for different tasks
- Take advantage of different pricing models

### 3. **Performance**
- Choose the best provider for specific use cases
- Load balancing between providers

### 4. **Redundancy**
- Multiple backup options
- Reduced dependency on single provider

## 🔍 Monitoring API Usage

The system logs which provider is being used:

```
INFO:fx_agents.api_provider:Using primary provider: openai
INFO:fx_agents.api_provider:Using fallback provider: gemini
```

## 🚨 Troubleshooting

### Common Issues

1. **"No API providers available"**
   - Check that your API keys are correctly set in `.env`
   - Verify the keys are valid by testing them individually

2. **"Provider not configured"**
   - Make sure you've added the API key to your `.env` file
   - Restart the application after adding keys

3. **"Authentication failed"**
   - Verify your API key is correct
   - Check if you have sufficient credits/quota

### Testing Individual Providers

```python
from fx_agents.api_switcher import test_provider

# Test OpenAI
result = test_provider("openai")

# Test Gemini
result = test_provider("gemini")
```

## 🎉 Ready to Use!

Once configured, your FreelanceX.AI system will automatically:
- Use your preferred primary API provider
- Fall back to your secondary provider if needed
- Provide seamless service regardless of individual API availability

Run your application:
```bash
python -m chainlit run chainlit_app/main.py --host 127.0.0.1 --port 8000
```
