import ollama
from abc import ABC, abstractmethod
from loguru import logger
import os

class AgentBase(ABC):
    def __init__(self, name, max_retries=2, verbose=True):
        self.name = name
        self.max_retries = max_retries
        self.verbose = verbose

    @abstractmethod
    def execute(self, *args, **kwargs):
        """
        Execute the main functionality of the agent
        """
        pass

    def call_llama(self, messages, temperature=0.3, max_tokens=150):
        """
        Calls the llama model via Ollama and retrieves the response
        Args:
            messages(list): A list of message dictionaries.
            temperature(float): Sampling Temperature
            max_tokens(int): Maximum number of tokens in the response
            
        Returns:
               str: the content of model's response
        """
        retries = 0
        while retries < self.max_retries:
            try:
                if self.verbose:
                    logger.info(f"[{self.name}] Sending messages to Ollama:")
                    for msg in messages:
                        logger.debug(f"  {msg['role']}: {msg['content']}")
                response = ollama.chat(
                    model="llama3.2:1b",
                    messages=messages,
                    options={
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                )
                reply = response['message']['content']
                if self.verbose:
                    logger.info(f"[{self.name}] Received response: {reply}")
                return reply
            except Exception as e:
                retries += 1
                logger.error(f"[{self.name}] Error during Ollama call: {e}. Retry {retries}/{self.max_retries}")
        raise Exception(f"[{self.name}] Failed to get response from Ollama after {self.max_retries} retries.")

    def format_message(self, role, content):
        """
        Format a message for the llama model
        Args:
            role(str): The role of the message sender (system/user/assistant)
            content(str): The content of the message
        
        Returns:
            dict: Formatted message dictionary
        """
        return {
            "role": role,
            "content": content
        }