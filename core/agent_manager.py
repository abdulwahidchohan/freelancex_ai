# Manages agent lifecycle
class AgentManager:
    def __init__(self):
        self.agents = []
        self.agent_status = {}

    def register_agent(self, agent):
        """Register a new agent with the manager"""
        self.agents.append(agent)
        self.agent_status[agent.id] = "registered"
        
    def boot_agents(self):
        """Boot up all registered agents and track their status"""
        print("AgentManager: Booting up all agents...")
        
        for agent in self.agents:
            try:
                agent.initialize()
                self.agent_status[agent.id] = "running"
            except Exception as e:
                print(f"Failed to boot agent {agent.id}: {str(e)}")
                self.agent_status[agent.id] = "failed"
                return False
                
        return all(status == "running" for status in self.agent_status.values())

    def shutdown_agents(self):
        """Gracefully shutdown all running agents"""
        for agent in self.agents:
            if self.agent_status[agent.id] == "running":
                agent.shutdown()
                self.agent_status[agent.id] = "stopped"
