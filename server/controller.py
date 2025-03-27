from main import DatabaseQueryAssistant
from intent_classifier import IntentClassifier


def receive_prompt(user_prompt: str):
    try:
        # Replace with your actual credentials
        assistant = DatabaseQueryAssistant()
        
        # Example query generation
        # user_prompt = input("Query anything: ")
        intent = IntentClassifier().classify_intent(user_prompt, assistant.schema_context)
        print("user's intent:", intent)

        prompt = assistant.initialize_prompt(user_prompt, intent)
        generated_query = assistant.generate_query(prompt)
        
        # print("Response:", assistant.schema_context)
        
        print("Generated Query:", generated_query)

        return generated_query
    
    except Exception as e:
        print(f"Initialization failed: {e}")
        return {"error": str(e)}