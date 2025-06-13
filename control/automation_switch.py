import time
import threading
import chainlit as cl
from .rules_engine import enforce_rules

# Global ON/OFF kill switch
system_active = False
safety_checks_enabled = True

def toggle_system():
    global system_active
    system_active = not system_active
    if system_active:
        start_monitoring()
    else:
        stop_monitoring()

def is_system_active():
    return system_active

def toggle_safety_checks():
    global safety_checks_enabled
    safety_checks_enabled = not safety_checks_enabled

def is_safety_checks_enabled():
    return safety_checks_enabled

def start_monitoring():
    monitoring_thread = threading.Thread(target=monitor_system)
    monitoring_thread.daemon = True
    monitoring_thread.start()

def stop_monitoring():
    # Implement logic to stop monitoring
    pass

def monitor_system():
    while system_active:
        # Check system activity
        if not is_system_active():
            break

        # Check safety checks
        if not is_safety_checks_enabled():
            break

        # Check rules
        for agent in ["job_hunter", "proposal_writer", "email_replier"]:
            enforce_rules(agent, "check")

        time.sleep(60)  # Check every minute

def update_automation_switch_ui():
    with cl.sidebar():
        cl.title("Automation Switch")
        cl.button("Toggle System", on_click=lambda: toggle_system())
        cl.button("Toggle Safety Checks", on_click=lambda: toggle_safety_checks())
