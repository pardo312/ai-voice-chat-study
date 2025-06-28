"""
AI Chat Module for Voice Chat Application
Handles communication with OpenRouter API for conversational AI responses
"""

import os
import json
import requests
import time
from typing import List, Dict, Optional

try:
    # Try relative imports first (when used as a module)
    from .config import *
except ImportError:
    # Fall back to absolute imports (when run as a script)
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from config import *


class AIChat:
    def __init__(self):
        self.conversation_history: List[Dict[str, str]] = []
        self.api_key = OPENROUTER_API_KEY
        self.model = OPENROUTER_MODEL
        self.base_url = OPENROUTER_BASE_URL
        self.system_prompt = AI_SYSTEM_PROMPT
        self.max_history = CONVERSATION_MEMORY_LENGTH
        
        # Validate API key
        if self.api_key == "your-api-key-here" or not self.api_key:
            print("⚠️  Warning: OpenRouter API key not configured!")
            print("💡 Please set your API key in src/config.py")
            self.api_configured = False
        else:
            self.api_configured = True
    
    def add_to_history(self, user_message: str, ai_response: str):
        """Add a message exchange to conversation history"""
        self.conversation_history.append({
            "user": user_message,
            "assistant": ai_response
        })
        
        # Keep only the last N exchanges
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
    
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
            "HTTP-Referer": "https://github.com/your-username/voice-chat",  # Optional
            "X-Title": "Voice Chat AI"  # Optional
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
                print(f"🔄 Calling OpenRouter API with model: {self.model}")
            
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
                    print("✅ OpenRouter API call successful")
                
                return ai_response
            else:
                print(f"❌ OpenRouter API error: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            print("❌ OpenRouter API timeout")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ OpenRouter API request error: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error calling OpenRouter API: {e}")
            return None
    
    def get_response(self, user_input: str) -> str:
        """Get AI response for user input"""
        if not user_input or user_input.strip() == "":
            return "I didn't catch that. Could you say something?"
        
        # Clean up the input
        user_input = user_input.strip()
        
        if VERBOSE_MODE:
            print(f"🤖 Getting AI response for: '{user_input}'")
        
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
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        if VERBOSE_MODE:
            print("🧹 Conversation history cleared")
    
    def get_history_summary(self) -> str:
        """Get a summary of conversation history for debugging"""
        if not self.conversation_history:
            return "No conversation history"
        
        summary = f"Conversation history ({len(self.conversation_history)} exchanges):\n"
        for i, exchange in enumerate(self.conversation_history, 1):
            summary += f"  {i}. User: {exchange['user'][:50]}...\n"
            summary += f"     AI: {exchange['assistant'][:50]}...\n"
        
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
