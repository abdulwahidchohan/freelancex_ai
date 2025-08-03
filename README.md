# FreelanceX.AI

A powerful AI-driven platform for freelancers that leverages cutting-edge technologies to streamline and enhance your freelancing career. FreelanceX.AI implements a comprehensive agent-based architecture with three core AI agents working in harmony to provide personalized, intelligent assistance for freelancers worldwide.

## 🚀 Features

### Core AI Agents

1. **JobSearchAgent** - Intelligent job matching and discovery
   - Real-time job alerts across multiple platforms (Upwork, Fiverr, Freelancer, LinkedIn, Toptal)
   - AI-powered job ranking and matching based on your skills and preferences
   - Competitive salary analysis and market insights
   - Personalized job recommendations with learning from your behavior

2. **WebSearchAgent** - Comprehensive research and market intelligence
   - In-depth research on business strategies, AI tools, and industry trends
   - Multi-source search across Google, Bing, DuckDuckGo, arXiv, and GitHub
   - Semantic understanding for tailored research outputs
   - Trend analysis and competitive intelligence

3. **MathAgent** - Financial planning and analytical support
   - Real-time formula solving and statistical analysis
   - Financial projections and budget planning
   - Tax estimation and profit margin calculations
   - Data visualization and performance analytics

### Advanced Features

- **Agent Collaboration & Negotiation** - Agents work together via a centralized API layer, negotiating when recommendations conflict
- **Extended Personalization** - Rich user profiles that learn and adapt based on your behavior
- **Daily Routines** - Automated morning routines, work session monitoring, and end-of-day summaries
- **Shadow Learning & Self-Repair** - Continuous learning from real-world applications and self-improvement
- **Legacy Memory** - Long-term memory of all interactions for enhanced personalization
- **Marketplace Integration** - Support for major freelancing platforms with analytics

## 🏗️ Architecture

```
FreelanceX.AI/
├── core/                          # Core system components
│   ├── agent_manager.py          # Orchestrates all agents
│   ├── user_profile_manager.py   # Manages user profiles and learning
│   ├── daily_routines.py         # Automated daily workflows
│   └── executive_agent.py        # High-level decision making
├── agents/                       # AI Agent implementations
│   ├── job_search_agent.py       # Job discovery and matching
│   ├── web_search_agent.py       # Research and intelligence
│   └── math_agent.py            # Financial and analytical support
├── config/                       # Configuration files
├── main.py                      # Main application entry point
└── requirements.txt             # Python dependencies
```

### System Components

1. **Agent Manager** - Centralized coordination of all agents with task queuing, conflict resolution, and transparency logging
2. **User Profile Manager** - Comprehensive profile system with skills, work history, financial data, and behavior tracking
3. **Daily Routines Manager** - Automated workflows for morning routines, work sessions, and end-of-day summaries
4. **Executive Agent** - High-level decision making and system governance

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- pip package manager

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd FreelanceX.AI
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API keys** (optional for demo)
   Create a `.env` file in the root directory:
   ```env
   GOOGLE_API_KEY=your_google_api_key
   OPENAI_API_KEY=your_openai_api_key
   ```

4. **Run the application**
   ```bash
   # Run in demo mode
   python main.py --demo
   
   # Run in normal mode
   python main.py
   ```

## 🎯 Usage

### Quick Start

Run the demonstration to see FreelanceX.AI in action:

```bash
python main.py --demo
```

This will:
- Create a sample user profile
- Demonstrate all three core agents
- Show personalized recommendations
- Display system capabilities

### Core Functionality

#### 1. Job Search and Matching

```python
# Find jobs matching your profile
response = await app.process_user_request(
    "Find me high-paying Python development jobs on Upwork"
)
```

#### 2. Research and Intelligence

```python
# Research market trends
response = await app.process_user_request(
    "Research the latest trends in AI and machine learning for freelancers"
)
```

#### 3. Financial Planning

```python
# Calculate optimal rates
response = await app.process_user_request(
    "Calculate my optimal hourly rate based on my expenses and income goals"
)
```

### User Profile Management

```python
# Update your profile
await app.update_user_profile({
    'basic_info': {
        'name': 'Your Name',
        'email': 'your.email@example.com',
        'location': 'Your Location'
    },
    'skills': [
        {
            'name': 'Python',
            'level': 'expert',
            'years_experience': 5.0,
            'proficiency_score': 0.9,
            'is_preferred': True
        }
    ],
    'financial_profile': {
        'desired_annual_income': 120000,
        'current_hourly_rate': 75,
        'tax_rate': 0.25
    }
})
```

### Daily Routines

The system automatically runs daily routines:

- **Morning Routine (9:00 AM)**: Job market review, research digest, financial check
- **Work Session (Every 30 min)**: Job alerts, financial calculations
- **End of Day (6:00 PM)**: Performance summary, research insights
- **Weekly Reflection (Sunday 10:00 AM)**: Weekly analysis, skill assessment

## 🔧 Configuration

### Agent Settings

Configure agent behavior in `config/agents_config.yaml`:

```yaml
job_search:
  preferred_platforms: [upwork, fiverr, freelancer]
  alert_frequency: daily
  salary_threshold: 50

web_search:
  research_depth: comprehensive
  preferred_sources: [medium.com, github.com, stackoverflow.com]

math:
  calculation_precision: 2
  preferred_currency: USD
```

### Daily Routines

Customize daily routines in the `DailyRoutinesManager`:

```python
# Modify routine schedules
routine_configs[RoutineType.MORNING]['scheduled_time'] = '08:00'
routine_configs[RoutineType.END_OF_DAY]['scheduled_time'] = '17:00'
```

## 📊 System Monitoring

### Get System Status

```python
status = await app.get_system_status()
print(f"Total requests: {status['total_requests_processed']}")
print(f"Agent performance: {status['agent_manager']['agent_performance']}")
```

### Export System Data

```python
exported_files = await app.export_system_data()
# Exports: user profile, agent logs, routine data, system status
```

### Personalized Recommendations

```python
recommendations = await app.get_personalized_recommendations()
# Returns: agent-specific recommendations, behavior insights, learning suggestions
```

## 🔒 Privacy and Security

- **Data Privacy**: No personal data is retained without user consent
- **Encryption**: All interactions are encrypted and anonymized
- **User Control**: Users can manage memory retention and delete previous data
- **Transparency**: All agent negotiations and decisions are logged for review

## 🚀 Advanced Features

### Agent Negotiation

When agents have conflicting recommendations, they automatically negotiate:

```python
# Example: JobSearchAgent finds low-paying jobs, MathAgent suggests filtering
conflicts = agent_manager._identify_conflicts(results)
resolved_results = await agent_manager._negotiate_conflicts(conflicts, results)
```

### Shadow Learning

The system learns from successful patterns:

```python
# Track successful behaviors
user_profile_manager.track_behavior(
    action_type='job_application',
    action_data={'job_id': '123', 'salary': 5000},
    success_rate=1.0,
    satisfaction_score=0.9
)
```

### Self-Repair

Agents monitor their own performance and flag improvements:

```python
# System automatically identifies and logs performance issues
if performance_drop > threshold:
    agent_manager._flag_performance_issue(agent_id, issue_details)
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest tests/

# Run specific agent tests
pytest tests/test_job_search_agent.py
pytest tests/test_web_search_agent.py
pytest tests/test_math_agent.py
```

## 📈 Performance Metrics

The system tracks various performance metrics:

- **Agent Performance**: Success rates, response times, task completion
- **User Engagement**: Behavior patterns, satisfaction scores, feature usage
- **System Health**: Uptime, error rates, resource utilization
- **Business Impact**: Jobs found, applications sent, income optimization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [Wiki](https://github.com/your-repo/freelancex_ai/wiki)
- **Discord Community**: [Join our Discord](https://discord.gg/freelancex)
- **Issues**: [GitHub Issues](https://github.com/your-repo/freelancex_ai/issues)

## 🎯 Roadmap

### Phase 1 (Current)
- ✅ Core agent architecture
- ✅ User profile management
- ✅ Daily routines automation
- ✅ Agent coordination and negotiation

### Phase 2 (Next)
- 🔄 Marketplace API integrations
- 🔄 Advanced AI model integration
- 🔄 Mobile application
- 🔄 Real-time collaboration features

### Phase 3 (Future)
- 📋 Blockchain-based reputation system
- 📋 AI-powered proposal generation
- 📋 Advanced analytics dashboard
- 📋 Multi-language support

---

**FreelanceX.AI** - Empowering freelancers with cutting-edge AI tools to enhance productivity, decision-making, and market adaptability, fostering a seamless connection between talent and opportunities globally.
