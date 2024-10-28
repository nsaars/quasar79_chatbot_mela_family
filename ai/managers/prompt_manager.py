import json
import logging
from ai.data.config import DEFAULT_PROMPT_PATH, SPECIAL_PROMPT_PATH, COMPANY_NAME, COMPANY_ABOUT

class PromptManager:
    """
    Manages prompt templates.
    """

    def __init__(self):
        self.default_prompts = self._load_default_prompts(DEFAULT_PROMPT_PATH)
        self.special_prompts = self._load_prompts(SPECIAL_PROMPT_PATH)

    @staticmethod
    def _load_prompts(file_path):
        """
        Load prompt templates from a JSON file.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError as e:
            logging.error(f"Prompt file not found: {e}")
            raise

    @staticmethod
    def _load_default_prompts(file_path):
        """
        Load prompt formatted default templates from a JSON file.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                result = {}
                tmp_json = json.load(f)
                for key, value in tmp_json.items():
                    value = PromptManager.format_text(value)
                    result[key] = value
                return result
        except FileNotFoundError as e:
            logging.error(f"Default prompts file not found: {e}")
            raise

    @staticmethod
    def format_text(text):
        return text.format(company_name=COMPANY_NAME, company_about=COMPANY_ABOUT)