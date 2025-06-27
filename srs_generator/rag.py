import os
import requests
import time
from abc import ABC, abstractmethod
from loguru import logger
from dotenv import load_dotenv

class AgentBase(ABC):
    def __init__(self, name, max_retries=5, verbose=True):  # Increased retries for robustness
        self.name = name
        self.max_retries = max_retries
        self.verbose = verbose
        load_dotenv()
        self.logger = logger

    @abstractmethod
    def execute(self, *args, **kwargs):
        """
        Execute the main functionality of the agent
        """
        pass

    def call_gemini(self, messages, temperature=0.3, max_tokens=150):
        """
        Calls the Gemini API and retrieves the response with exponential backoff
        Args:
            messages(list): A list of message dictionaries with 'role' and 'content' keys
            temperature(float): Sampling temperature for generation
            max_tokens(int): Maximum number of tokens in the response
            
        Returns:
            str: The content of the model's response, or None if all retries fail
        """
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
        headers = {'Content-Type': 'application/json'}

        # Combine messages into a single prompt
        prompt = ""
        for msg in messages:
            prompt += f"{msg['role'].capitalize()}: {msg['content']}\n\n"

        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }

        if self.verbose:
            self.logger.info(f"[{self.name}] Sending prompt to Gemini API:")
            self.logger.debug(f"Prompt:\n{prompt}")

        for attempt in range(self.max_retries):
            try:
                response = requests.post(url, headers=headers, json=payload)
                response.raise_for_status()
                
                json_response = response.json()
                reply = json_response['candidates'][0]['content']['parts'][0]['text']
                
                if self.verbose:
                    self.logger.info(f"[{self.name}] Received response: {reply}")
                return reply
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    self.logger.warning(f"[{self.name}] Rate limit exceeded (429). Waiting {2 ** attempt} seconds before retry.")
                    time.sleep(2 ** attempt)  # Exponential backoff: 1, 2, 4, 8, 16 seconds
                else:
                    self.logger.error(f"[{self.name}] Gemini API call failed: {str(e)}")
                    time.sleep(1)
                if attempt < self.max_retries - 1:
                    self.logger.warning(f"[{self.name}] Retrying attempt {attempt + 2}/{self.max_retries}")
            except Exception as e:
                self.logger.error(f"[{self.name}] Gemini API call failed: {str(e)}")
                time.sleep(1)
                if attempt < self.max_retries - 1:
                    self.logger.warning(f"[{self.name}] Retrying attempt {attempt + 2}/{self.max_retries}")
        
        self.logger.error(f"[{self.name}] Failed to get response from Gemini API after {self.max_retries} retries")
        return None

    def format_message(self, role, content):
        """
        Format a message for compatibility with message-based interfaces
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