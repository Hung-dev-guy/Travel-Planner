from typing import List
from google import genai
from google.genai import types

DEFAULT_MODEL = "gemini-2.5-flash-lite"

class LLM:
    """
    A robust wrapper class for language models via langchain_openai,
    featuring built-in retry logic and API key rotation.
    """
    
    def __init__(
        self, 
        api_keys: List[str], 
        base_url: str = "", 
        model: str = DEFAULT_MODEL, 
        temperature: float = 0.5, 
        max_tokens: int = 4096, 
        top_p: float = 1.0, 
        add_stop_token: List[str] = None,
        response_schema = None
    ):
        """
        Initializes the LLM instance with a list of API keys for rotation.
        Args:
            api_keys (List[str]): A list of API keys to rotate through on failure.
            base_url (str): Base URL for the LLM service.
            model (str): Model name or identifier.
            ...
        """
        if not api_keys or not isinstance(api_keys, list):
            raise ValueError("api_keys must be a non-empty list of strings.")
            
        self.api_keys = api_keys
        self.base_url = base_url
        self.model = model
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.response_schema = response_schema
        
        self.add_stop_token = ["---\n", "STOP_HERE"]
        self.add_stop_token.extend(add_stop_token or [])
            
        self.current_key_index = 0
        self.client = None
        self.config = None
        self.create_llm_instance()
        
        print(f"LLM class initialized for model '{model}' with {len(self.api_keys)} API keys.")

    def create_llm_instance(self):
        """
        Helper method to create or recreate the ChatOpenAI instance.
        It uses the key at the current_key_index.
        """
        current_api_key = self.api_keys[self.current_key_index]
        client_kwargs = {"api_key": current_api_key}
        if self.base_url:
            client_kwargs["http_options"] = {"base_url": self.base_url}
        self.client = genai.Client(**client_kwargs)
        config_args = {
            "temperature": self.temperature,
            "max_output_tokens": self.max_tokens,
            "top_p": self.top_p,
            "stop_sequences": self.add_stop_token
        }
        if self.response_schema:
            config_args["response_schema"] = self.response_schema
            config_args["response_mime_type"] = "application/json"
        self.config = types.GenerateContentConfig(**config_args)
        print(f"Gemini Client instance created/updated with API key index: {self.current_key_index}")

    def rotate_key_and_recreate_instance(self):
        """Rotates to the next API key and recreates the LLM instance."""
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        print(f"Rotating API key. New key index: {self.current_key_index}")
        self.create_llm_instance()

    def invoke(self, prompt: str) -> str:
        """
        Invokes the LLM with a given prompt and returns the text response.
        Automatically rotates the API key and retries if an error (like Quota Exceeded) occurs.
        """
        import time
        max_retries = max(len(self.api_keys) * 2, 5) # Retry up to 5 times
        attempts = 0
        
        while attempts < max_retries:
            try:
                if not self.client:
                    raise RuntimeError("Gemini Client is not initialized.")
                    
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=self.config
                )
                return response.text
            except Exception as e:
                attempts += 1
                error_str = str(e)
                print(f"Lỗi API ở key index {self.current_key_index}: {error_str}")
                
                if "Quota exceeded" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    print("Hết quota API. Ngưng retry.")
                    raise e
                    
                if attempts < max_retries:
                    if "429" in error_str or "503" in error_str:
                        wait_time = 3 * attempts
                        print(f"API đang quá tải (429/503). Đợi {wait_time}s trước khi thử lại...")
                        time.sleep(wait_time)
                        
                    if len(self.api_keys) > 1:
                        print("Đang đổi API key tiếp theo...")
                        self.rotate_key_and_recreate_instance()
                    else:
                        print(f"Đang thử lại (Lần {attempts}/{max_retries})...")
                else:
                    print("Đã hết số lần retry. Bỏ cuộc!")
                    raise e

