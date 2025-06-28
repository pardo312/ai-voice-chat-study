"""
AI Chat Module for Voice Chat Application
Handles communication with OpenRouter API for conversational AI responses
"""

import json
import requests
import time
import logging
from typing import List, Dict, Optional

from ..config import (
    OPENROUTER_API_KEY,
    OPENROUTER_MODEL,
    OPENROUTER_BASE_URL,
    AI_SYSTEM_PROMPT,
    CONVERSATION_MEMORY_LENGTH,
    VERBOSE_MODE
)

logger = logging.getLogger(__name__)


class AIChat:
    """Handles AI conversation using OpenRouter API"""
    
    def __init__(self):
        self.conversation_history: List[Dict[str, str]] = []
        self.api_key = OPENROUTER_API_KEY
        self.model = OPENROUTER_MODEL
        self.base_url = OPENROUTER_BASE_URL
        self.system_prompt = AI_SYSTEM_PROMPT
        self.max_history = CONVERSATION_MEMORY_LENGTH
        
        # Validate API key
        if self.api_key == "your-api-key-here" or not self.api_key:
            logger.warning("OpenRouter API key not configured!")
            print("⚠️  Warning: OpenRouter API key not configured!")
            print("💡 Please set OPENROUTER_API_KEY in your .env file")
            self.api_configured = False
        else:
            self.api_configured = True
            if VERBOSE_MODE:
                logger.info("AI Chat initialized with OpenRouter API")
    
    def add_to_history(self, user_message: str, ai_response: str) -> None:
        """Add a message exchange to conversation history"""
        self.conversation_history.append({
            "user": user_message,
            "assistant": ai_response
        })
        
        # Keep only the last N exchanges
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
            
        if VERBOSE_MODE:
            logger.debug(f"Added to history. Total exchanges: {len(self.conversation_history)}")
    
    def build_messages(self, user_input: str) -> List[Dict[str, str]]:
        """Build the messages array for the API call"""
        messages = []
        
        # Add system prompt
        messages.append({
            "role": "system",
            "content": self.system_prompt
        })
        
        # Add conversation history
        for exchange in self.conversation_history:
            messages.append({
                "role": "user",
                "content": exchange["user"]
            })
            messages.append({
                "role": "assistant",
                "content": exchange["assistant"]
            })
        
        # Add current user input
        messages.append({
            "role": "user",
            "content": user_input
        })
        
        return messages
    
    def call_openrouter_api(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """Make API call to OpenRouter"""
        if not self.api_configured:
            return None
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/voice-chat-ai",
            "X-Title": "Voice Chat AI"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 150,  # Keep responses concise for speech
            "top_p": 0.9
        }
        
        try:
            if VERBOSE_MODE:
                logger.info(f"Calling OpenRouter API with model: {self.model}")
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data["choices"][0]["message"]["content"].strip()
                
                if VERBOSE_MODE:
                    logger.info("OpenRouter API call successful")
                
                return ai_response
            else:
                error_msg = f"OpenRouter API error: {response.status_code}"
                logger.error(f"{error_msg} - {response.text}")
                print(f"❌ {error_msg}")
                return None
                
        except requests.exceptions.Timeout:
            error_msg = "OpenRouter API timeout"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            return None
        except requests.exceptions.RequestException as e:
            error_msg = f"OpenRouter API request error: {e}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            return None
        except Exception as e:
            error_msg = f"Unexpected error calling OpenRouter API: {e}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            return None
    
    def get_response(self, user_input: str) -> str:
        """Get AI response for user input"""
        if not user_input or user_input.strip() == "":
            return "I didn't catch that. Could you say something?"
        
        # Clean up the input
        user_input = user_input.strip()
        
        if VERBOSE_MODE:
            logger.debug(f"Getting AI response for: '{user_input}'")
        
        # Build messages for API call
        messages = self.build_messages(user_input)
        
        # Call OpenRouter API
        ai_response = self.call_openrouter_api(messages)
        
        if ai_response:
            # Add to conversation history
            self.add_to_history(user_input, ai_response)
            return ai_response
        else:
            # Fallback response if API fails
            fallback_responses = [
                "Sorry, I'm having trouble connecting right now. Could you try again?",
                "Hmm, I didn't quite get that. Can you repeat it?",
                "I'm having some technical difficulties. Let's try that again.",
                "Oops, something went wrong on my end. What were you saying?"
            ]
            
            # Use a simple rotation based on history length
            fallback_index = len(self.conversation_history) % len(fallback_responses)
            fallback = fallback_responses[fallback_index]
            
            # Still add to history for context
            self.add_to_history(user_input, fallback)
            return fallback
    
    def clear_history(self) -> None:
        """Clear conversation history"""
        self.conversation_history = []
        if VERBOSE_MODE:
            logger.info("Conversation history cleared")
            print("🧹 Conversation history cleared")
    
    def get_history_summary(self) -> str:
        """Get a summary of conversation history for debugging"""
        if not self.conversation_history:
            return "No conversation history"
        
        summary = f"Conversation history ({len(self.conversation_history)} exchanges):\n"
        for i, exchange in enumerate(self.conversation_history, 1):
            user_text = exchange['user'][:50] + "..." if len(exchange['user']) > 50 else exchange['user']
            ai_text = exchange['assistant'][:50] + "..." if len(exchange['assistant']) > 50 else exchange['assistant']
            summary += f"  {i}. User: {user_text}\n"
            summary += f"     AI: {ai_text}\n"
        
        return summary
    
    def test_connection(self) -> bool:
        """Test the OpenRouter API connection"""
        if not self.api_configured:
            print("❌ API key not configured")
            return False
        
        test_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello' if you can hear me."}
        ]
        
        response = self.call_openrouter_api(test_messages)
        if response:
            print(f"✅ OpenRouter connection test successful: {response}")
            return True
        else:
            print("❌ OpenRouter connection test failed")
            return False
