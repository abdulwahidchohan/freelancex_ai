# FreelanceX.AI Control System

This directory contains the control system for FreelanceX.AI, which includes the Master Control Panel (MCP), automation rules, and voice control.

## Components

### Master Control Panel (MCP)

The MCP is the central hub for controlling and monitoring the FreelanceX.AI system. It provides a user interface for:

- Starting and stopping agents
- Pausing and resuming automation
- Toggling safety checks
- Starting and stopping voice control
- Viewing logs

### Automation Rules

The automation rules system enforces specific rules for different agents, such as:

- Job Hunter: Maximum applications per day, minimum job match score, required skills
- Proposal Writer: Maximum proposals per day, minimum proposal length, required sections
- Email Replier: Maximum emails per day, response time limit, required tone

### Voice Control

The voice control system allows users to control the FreelanceX.AI system using voice commands. It includes:

- Speech-to-text conversion
- Content generation using Gemini Flash
- Start and stop voice control

## Usage

To use the control system, import the necessary functions from the `control` package:

```python
from control import render_controls, toggle_system, is_system_active, toggle_safety_checks, is_safety_checks_enabled, enforce_rules, update_rules_ui, process_voice, start_voice_control, stop_voice_control, update_voice_control_ui
```

Then, you can use these functions to control and monitor the FreelanceX.AI system.

## Integration

The control system is designed to be modular and scalable, allowing for easy integration with other components of the FreelanceX.AI system. It uses the Chainlit library for the user interface and the Gemini Flash API for content generation.

## Safety

The control system includes safety checks to ensure that the FreelanceX.AI system operates within defined rules and limits. These checks can be toggled on and off using the MCP.

## Monitoring

The control system includes a monitoring function that runs in a separate thread, checking system activity, safety checks, and rules every minute. This ensures that the system operates within defined limits and rules.

## Setup

1. Install the required packages:

```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the `control` directory and add your Gemini API key:

```
GEMINI_API_KEY=your_gemini_api_key_here
```

3. Run the control panel:

```bash
python run.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For any questions or concerns, please contact the FreelanceX.AI team at support@freelancex.ai.

## Acknowledgments

We would like to thank the following open-source projects for their contributions:

- Chainlit: For providing the user interface library
- Google Generative AI: For providing the Gemini Flash API
- Python-dotenv: For managing environment variables

## Changelog

### Version 1.0.0 (2024-03-14)

- Initial release of the FreelanceX.AI Control System
- Implemented Master Control Panel (MCP)
- Added automation rules for different agents
- Integrated voice control with Gemini Flash
- Added safety checks and monitoring

## Roadmap

### Version 1.1.0 (Planned)

- Add support for more agents
- Enhance automation rules with machine learning
- Improve voice control accuracy
- Add real-time monitoring and alerts
- Implement user authentication and authorization

### Version 1.2.0 (Planned)

- Add support for custom rules and workflows
- Enhance integration with external systems
- Improve performance and scalability
- Add support for multiple languages
- Implement advanced analytics and reporting

## Troubleshooting

### Common Issues

1. **Gemini API Key Not Set**

   If you encounter an error stating that the Gemini API key is not set, make sure you have created a `.env` file in the `control` directory and added your Gemini API key:

   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

2. **Voice Control Not Working**

   If voice control is not working, make sure you have installed the required packages and that your microphone is properly connected and configured.

3. **Safety Checks Not Working**

   If safety checks are not working, make sure you have enabled them in the MCP and that the system is active.

### Getting Help

If you encounter any issues not listed above, please contact the FreelanceX.AI team at support@freelancex.ai or open an issue on the GitHub repository.

## Development

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git

### Setting Up the Development Environment

1. Clone the repository:

```bash
git clone https://github.com/freelancex-ai/control.git
cd control
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install the required packages:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file and add your Gemini API key:

```
GEMINI_API_KEY=your_gemini_api_key_here
```

5. Run the control panel:

```bash
python run.py
```

### Running Tests

To run the tests, use the following command:

```bash
python -m pytest tests/
```

### Code Style

This project follows the PEP 8 style guide for Python code. To check your code style, use the following command:

```bash
flake8 control/
```

### Documentation

The documentation is written in Markdown and is located in the `docs` directory. To build the documentation, use the following command:

```bash
mkdocs build
```

To serve the documentation locally, use the following command:

```bash
mkdocs serve
``` 