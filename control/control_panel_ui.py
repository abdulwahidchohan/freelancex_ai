import chainlit as cl
from .automation_switch import toggle_system, is_system_active, toggle_safety_checks, is_safety_checks_enabled
from .rules_engine import enforce_rules, update_rules_ui
from .voice_control import start_voice_control, stop_voice_control, update_voice_control_ui

# Chainlit control widgets
def render_controls():
    with cl.sidebar():
        cl.title("FreelanceX.AI Master Control Panel")
        cl.button("Start All Agents", on_click=lambda: start_all_agents())
        cl.button("Stop All Agents", on_click=lambda: stop_all_agents())
        cl.button("Pause Automation", on_click=lambda: pause_automation())
        cl.button("Resume Automation", on_click=lambda: resume_automation())
        cl.button("Toggle Safety Checks", on_click=lambda: toggle_safety_checks())
        cl.button("Start Voice Control", on_click=lambda: start_voice_control())
        cl.button("Stop Voice Control", on_click=lambda: stop_voice_control())
        cl.button("View Logs", on_click=lambda: view_logs())

        # Render rules UI
        update_rules_ui()

        # Render voice control UI
        update_voice_control_ui()

def start_all_agents():
    if is_system_active() and is_safety_checks_enabled():
        # Implement logic to start all agents
        pass

def stop_all_agents():
    if is_system_active() and is_safety_checks_enabled():
        # Implement logic to stop all agents
        pass

def pause_automation():
    if is_system_active() and is_safety_checks_enabled():
        toggle_system()

def resume_automation():
    if not is_system_active() and is_safety_checks_enabled():
        toggle_system()

def view_logs():
    if is_system_active() and is_safety_checks_enabled():
        # Implement logic to view logs
        pass
