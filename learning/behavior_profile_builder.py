import json
import os

# Updates agent persona
class ProfileBuilder:
    def __init__(self):
        self.profiles_file = "config/behavior_profiles.json"

    def build(self, agent_name, profile_data):
        try:
            # Load existing profiles
            if os.path.exists(self.profiles_file):
                with open(self.profiles_file, 'r') as f:
                    existing_profiles = json.load(f)
            else:
                existing_profiles = {}

            # Update profile for the agent
            existing_profiles[agent_name] = profile_data

            # Save updated profiles
            with open(self.profiles_file, 'w') as f:
                json.dump(existing_profiles, f, indent=4)

            # Evolve profile for continuous improvement
            self.evolve_profile(agent_name, profile_data)

            print(f"Behavior profile built for {agent_name}.")
        except Exception as e:
            print(f"Error building behavior profile for {agent_name}: {e}")

    def evolve_profile(self, agent_name, profile_data):
        # Implement profile evolution logic here
        # This could involve learning from user interactions, feedback, etc.
        pass
