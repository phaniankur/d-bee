import json
from typing import List, Tuple
from server.utils.redis_client import redis_client

# ChatMemory class to manage short-term chat history using Redis
class ChatMemory:
    """A class to manage short-term chat history using Redis."""
    
    def __init__(self, max_history_len: int = 10):
        """Initialize chat history storage.
        
        Args:
            max_history_len: Maximum number of message pairs (user+AI) to store per user
        """
        self.max_len = max_history_len * 2  # Multiply by 2 to store pairs

    def _get_user_key(self, user_id: str) -> str:
        """Generate Redis key for user's chat history."""
        return f"user:{user_id}:chathistory"
    
    def add_message(self, user_id: str, user_message: str, ai_message: str):
        """Add a user and AI message to the user's chat history in Redis.
        
        Args:
            user_id: Unique identifier for the user
            user_message: The message from the user
            ai_message: The response from the AI
        """
        user_key = self._get_user_key(user_id)
        
        # Create message pair
        messages = [
            json.dumps({"role": "user", "content": user_message}),
            json.dumps({"role": "ai", "content": ai_message})
        ]
        
        try:
            # Push to Redis list and trim to maintain max length
            if messages:  # Only proceed if there are messages to add
                redis_client.rpush(user_key, *messages)
                redis_client.ltrim(user_key, -self.max_len, -1)
        except Exception as e:
            print(f"Error adding message to Redis: {e}")
            raise

    def get_history(self, user_id: str) -> List[Tuple[str, str]]:
        """Retrieve the chat history for a given user.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            List of tuples in the form (role, message)
        """
        user_key = self._get_user_key(user_id)
        try:
            messages = redis_client.lrange(user_key, 0, -1)
            
            # Parse messages and convert to list of tuples
            history = []
            for msg in messages:
                try:
                    if not msg:
                        continue
                    data = json.loads(msg)
                    if not isinstance(data, dict):
                        continue
                    history.append((data.get('role', 'unknown'), data.get('content', '')))
                except (json.JSONDecodeError, KeyError, AttributeError) as e:
                    print(f"Error parsing message: {e}")
                    continue
        except Exception as e:
            print(f"Error retrieving messages from Redis: {e}")
            history = []
        print("History for user", user_id, history)
        return history
    
    def clear_history(self, user_id: str) -> None:
        """Clear the chat history for a given user.
        
        Args:
            user_id: The user ID whose history should be cleared
        """
        user_key = self._get_user_key(user_id)
        redis_client.delete(user_key)

# Singleton instance to be used across the application
chat_memory = ChatMemory()
