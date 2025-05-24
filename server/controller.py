from main import DatabaseQueryAssistant
from intent_classifier import IntentClassifier


def main_controller(user_prompt: str):
    try:
        # Replace with your actual credentials
        assistant = DatabaseQueryAssistant()
        
        # Example query generation
        # user_prompt = input("Query anything: ")
        # intent = IntentClassifier().classify_intent(user_prompt, assistant.schema_context)
        # print("user's intent:", intent)

        prompt = assistant.initialize_prompt(user_prompt, 'execute')
        generated_query = assistant.generate_query(prompt)
        print("final query:", generated_query)   
        
        query_result = assistant.execute_query(generated_query)
        print("Response:", query_result)

        return {
            "message": "success",
            "query": generated_query,
            "executed_result": query_result,
        }
    
    except Exception as e:
        print(f"Initialization failed: {e}")
        return {"error": str(e)}