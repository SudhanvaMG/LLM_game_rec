"""
LLM Client Wrapper

Handles API communication with LLM providers, specifically optimized for Google Gemini.
Supports task-specific model selection and configuration.
"""

import os
import time
import json
import google.generativeai as genai
from typing import Dict, Any, Optional, List
from enum import Enum
from src.utils.config_loader import load_config, load_env_file


class TaskType(Enum):
    """Different types of tasks requiring different model configurations"""
    ATTRIBUTE_GENERATION = "attribute_generation"
    GAME_GENERATION = "game_generation"
    VALIDATION = "validation"
    SIMILARITY_ANALYSIS = "similarity_analysis"
    EMBEDDINGS_SUMMARY = "embeddings_summary"


class LLMClient:
    """
    Multi-model LLM client supporting task-specific configurations.
    Optimized for Google Gemini with fallback support.
    """
    
    def __init__(self, config_path: str = "config/llm_config.yaml"):
        """Initialize LLM client with configuration"""
        # Load environment variables from .env file
        load_env_file()
        
        # Load configuration with environment variable substitution
        self.config = load_config(config_path)
        
        # Initialize Gemini client
        genai.configure(api_key=self.config['api_key'])
        
        # Rate limiting
        self.last_request_time = 0
        self.request_interval = 60 / self.config['rate_limits']['requests_per_minute']
        
        print(f"✅ LLM Client initialized with {self.config['provider']}")
        print(f"🔑 API key loaded from environment variable: {self.config['api_key_env']}")
    
    def generate(self, 
                prompt: str, 
                task_type: TaskType,
                **kwargs) -> str:
        """
        Generate response using task-appropriate model configuration.
        
        Args:
            prompt: The input prompt
            task_type: Type of task to determine model config
            **kwargs: Additional parameters to override defaults
            
        Returns:
            Generated text response
        """
        # Apply rate limiting
        self._handle_rate_limit()
        
        # Get model configuration for this task
        model_config = self._get_model_config(task_type)
        
        # Initialize model
        model = genai.GenerativeModel(model_config['model'])
        
        # Prepare generation config
        generation_config = genai.types.GenerationConfig(
            temperature=kwargs.get('temperature', model_config['temperature'])
        )
        
        # Add max_output_tokens only if specified
        if 'max_tokens' in model_config:
            generation_config.max_output_tokens = kwargs.get('max_tokens', model_config['max_tokens'])
        elif 'max_tokens' in kwargs:
            generation_config.max_output_tokens = kwargs['max_tokens']
        
        # Retry logic
        max_retries = self.config['rate_limits']['retry_attempts']
        retry_delay = self.config['rate_limits']['retry_delay']
        
        for attempt in range(max_retries + 1):
            try:
                response = model.generate_content(
                    prompt,
                    generation_config=generation_config
                )
                
                if response.text:
                    return response.text.strip()
                else:
                    raise Exception("Empty response from model")
                    
            except Exception as e:
                if attempt < max_retries:
                    print(f"⚠️ Attempt {attempt + 1} failed: {e}. Retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                else:
                    raise Exception(f"Failed after {max_retries + 1} attempts: {e}")
    
    def batch_generate(self, 
                      prompts: List[str], 
                      task_type: TaskType) -> List[str]:
        """
        Generate multiple responses efficiently.
        
        Args:
            prompts: List of input prompts
            task_type: Type of task for all prompts
            
        Returns:
            List of generated responses
        """
        results = []
        batch_size = self.config['rate_limits']['batch_size']
        
        for i in range(0, len(prompts), batch_size):
            batch = prompts[i:i + batch_size]
            batch_results = []
            
            for prompt in batch:
                try:
                    result = self.generate(prompt, task_type)
                    batch_results.append(result)
                except Exception as e:
                    print(f"❌ Failed to generate for prompt: {e}")
                    batch_results.append("")  # Empty result for failed generation
            
            results.extend(batch_results)
            
            # Small delay between batches
            if i + batch_size < len(prompts):
                time.sleep(1)
        
        return results
    
    def _get_model_config(self, task_type: TaskType) -> Dict[str, Any]:
        """Get model configuration for specific task type"""
        return self.config['models'][task_type.value]
    
    def _handle_rate_limit(self):
        """Handle rate limiting between requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.request_interval:
            sleep_time = self.request_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time() 
    
    async def generate_async(self, 
                            prompt: str, 
                            task_type: str,
                            **kwargs) -> str:
        """
        Async version of generate method.
        
        Args:
            prompt: The input prompt
            task_type: Type of task to determine model config (string version)
            **kwargs: Additional parameters to override defaults
            
        Returns:
            Generated text response
        """
        # Convert string task_type to TaskType enum
        try:
            task_enum = TaskType(task_type)
        except ValueError:
            # Default to game generation if unknown task type
            task_enum = TaskType.GAME_GENERATION
        
        # Use the synchronous generate method (Gemini client doesn't require async)
        return self.generate(prompt, task_enum, **kwargs)