# The CEO Agent - delegates, prioritizes, governs
import os
import yaml
import logging
from typing import Optional, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

class ExecutiveAgent:
    def __init__(self, config_path: str = 'config/system_prompts.yaml'):
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Load SYSTEM_PROMPT from a configuration file
        self.SYSTEM_PROMPT = self._load_config(config_path)
        self.logger.info('ExecutiveAgent online. Initializing with system prompt...')

        # Initialize the LLM with API key from environment
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
            
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=api_key,
            temperature=0.7,
            max_output_tokens=2048
        )
        
        # Create prompt template with more sophisticated structure
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.SYSTEM_PROMPT),
            ("human", "{input}"),
            ("system", "Please provide a clear, actionable response."),
        ])
        
        # Initialize chain
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)

    def _load_config(self, config_path: str) -> str:
        """Load and validate configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                if not config.get('system_prompt'):
                    raise ValueError("system_prompt not found in config file")
                return config['system_prompt']
        except Exception as e:
            self.logger.error(f"Failed to load config: {str(e)}")
            raise

    async def handle_message(self, message_content: str) -> str:
        """
        Handle incoming messages and generate responses.
        
        Args:
            message_content: The input message to process
            
        Returns:
            str: The generated response
        """
        self.logger.info(f"Processing message: {message_content[:100]}...")
        try:
            response = await self.chain.ainvoke({"input": message_content})
            return response['text']
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
            return "I apologize, but I encountered an error processing your request."

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task with proper error handling and logging.
        
        Args:
            task: Dictionary containing task details
            
        Returns:
            Dict containing task results and status
        """
        self.logger.info(f"Executing task: {task}")
        try:
            # Add task validation
            if not isinstance(task, dict) or 'type' not in task:
                raise ValueError("Invalid task format")

            # Task execution logic would go here
            # This is a placeholder for actual implementation
            result = {
                'status': 'completed',
                'task_id': task.get('id'),
                'result': f"Task '{task}' completed successfully",
                'timestamp': None  # Would add actual timestamp in implementation
            }
            
            self.logger.info(f"Task completed successfully: {task.get('id')}")
            return result
            
        except Exception as e:
            self.logger.error(f"Task execution failed: {str(e)}")
            return {
                'status': 'failed',
                'task_id': task.get('id'),
                'error': str(e)
            }
