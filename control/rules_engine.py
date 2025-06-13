import chainlit as cl
from .automation_switch import is_system_active, is_safety_checks_enabled

# Rules for different agents
rules = {
    "job_hunter": {
        "max_applications_per_day": 10,
        "min_job_match_score": 0.7,
        "required_skills": ["Python", "AI", "Machine Learning"]
    },
    "proposal_writer": {
        "max_proposals_per_day": 5,
        "min_proposal_length": 500,
        "required_sections": ["Introduction", "Approach", "Timeline", "Budget"]
    },
    "email_replier": {
        "max_emails_per_day": 20,
        "response_time_limit": 24,  # hours
        "required_tone": "Professional"
    }
}

def enforce_rules(agent_name, action):
    if not is_system_active() or not is_safety_checks_enabled():
        return True

    if agent_name not in rules:
        return True

    agent_rules = rules[agent_name]
    if action == "job_hunt":
        return check_job_hunting_rules(agent_rules)
    elif action == "write_proposal":
        return check_proposal_writing_rules(agent_rules)
    elif action == "reply_email":
        return check_email_replying_rules(agent_rules)
    return True

def check_job_hunting_rules(rules):
    # Implement job hunting rule checks
    return True

def check_proposal_writing_rules(rules):
    # Implement proposal writing rule checks
    return True

def check_email_replying_rules(rules):
    # Implement email replying rule checks
    return True

def update_rules_ui():
    with cl.sidebar():
        cl.title("Automation Rules")
        for agent, agent_rules in rules.items():
            cl.subtitle(agent)
            for rule, value in agent_rules.items():
                cl.text(f"{rule}: {value}")
            cl.button(f"Edit {agent} Rules", on_click=lambda: edit_rules(agent))

def edit_rules(agent):
    if agent in rules:
        # Implement logic to edit rules
        pass
