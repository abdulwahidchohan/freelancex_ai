from core.base_agent import BaseAgent
import json
import os

# Writes proposals
class ProposalWriterAgent(BaseAgent):
    def __init__(self):
        super().__init__("ProposalWriterAgent")
        self.jobs_file = "data/jobs.json"
        self.proposals_file = "data/proposals.json"

    def run(self):
        print(f'{self.agent_name} online.')
        print(f"System Prompt loaded: {self.system_prompt[:50]}...") # For verification
        self.write()

    def write(self):
        try:
            # Load jobs from file
            with open(self.jobs_file, 'r') as f:
                jobs = json.load(f)

            proposals = []
            for job in jobs:
                # Generate proposal for each job
                proposal = self.generate_proposal(job)
                proposals.append(proposal)

            # Save proposals to file
            with open(self.proposals_file, 'w') as f:
                json.dump(proposals, f, indent=4)
            print(f"Proposals saved to {self.proposals_file}.")
        except Exception as e:
            print(f"Error writing proposals: {e}")

    def generate_proposal(self, job):
        # Implement proposal generation logic here
        return {
            "job_id": job.get("id"),
            "proposal_text": f"Proposal for job: {job.get('title')}",
            "status": "draft"
        }
