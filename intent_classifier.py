import ollama
import json

model_name='llama3.1:latest'

class IntentClassifier:
    def __init__(self, model: str = model_name):

        """
        Initialize Intent Classifier
        
        Args:
            model (str): Ollama model to use for intent classification
        """
        self.model = model
        
        # Predefined intent patterns
        self.intent_patterns = {
            'write': [
                'write or create queries',
                'calculate values',
                'count items',
                'find specific data',
                'list items',
                'retrieve information'
                'users active'
            ],
            'explain': [
                'explain queries or concepts',
                'provide detailed query explanations',
                'describe what is happening',
                'break down query components',
                'analyze query structure'
            ],
            'execute': [
                'run SQL queries',
                'perform database operations',
                'execute database commands',
                'run data retrieval operations'
            ]
        }
    
    def classify_intent(self, user_input: str, schema_context: str) -> str:

        # print("SCHEMA-->", schema_context)

        """
        Classify user intent based on input using LLM
        
        Args:
            user_input (str): User's input text
            
        Returns:
            str: Classified intent (write/explain/execute)
        """
        prompt = f"""
            Given the following intent categories and their descriptions:

            {json.dumps(self.intent_patterns, indent=2)}


            Following is the Database schema around which the user is asking:
            {schema_context}

            Understand the user's intent based on his input. The intent is categorized into write, explain, or execute.
            Classify the following user input into one of these categories (write/explain/execute):
            user:"{user_input}"

            Respond with just the category name in lowercase, nothing else.
        """

        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={
                    'temperature': 0.2,
                    'top_p': 0.9
                }
            )
            return response['response'].strip().lower()
        except Exception as e:
            print(f"Error classifying intent: {e}")
            return None

# Example Usage
def main():
    classifier = IntentClassifier()
    
    # Test cases
    test_inputs = [
        'write a query to calculate count of users with isAdmin true',
        'users who registered on 20th March',
        'SELECT * FROM users',
        'explain the previous query',
        'what is happening in this query?',
        'how many total users do we have?',
        'show me active users'
    ]
    
    for input_text in test_inputs:
        intent = classifier.classify_intent(input_text)
        print(f"Input: '{input_text}'\nIntent: {intent}\n")

if __name__ == "__main__":
    main()