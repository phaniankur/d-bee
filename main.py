from intent_classifier import IntentClassifier
import mysql.connector
from mysql.connector import Error
import ollama

# Database connection details
host = "127.0.0.1"
port = 3306
user = "root"
password = None
database = "db01"
# model_name='sqlcoder'
model_name='llama3.1:latest'

class DatabaseQueryAssistant:
    def __init__(self):
        try:
            # connection string
            connection = mysql.connector.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database
            )

            if connection.is_connected():
                # print("Connected to MySQL database successfully!")
                # Test connection
                # Get server info
                db_info = connection.get_server_info()
                # print("MySQL Server version:", db_info)
                
                # Create a cursor object
                cursor = connection.cursor()
                
                # Execute a test query
                cursor.execute("SELECT DATABASE();")
                record = cursor.fetchone()
                print("Connected to", record[0])
            
            # Store model and generate schema context
            self.model = model_name
            self.connection = connection
            self.schema_context = self._generate_schema_context()
        
        except mysql.connector.Error as e:
            print("Db Error", e)
            raise
    
    def _generate_schema_context(self):
        # print("Generating schema context...")
        """
        Generate comprehensive database schema context
        
        Returns:
            str: Formatted schema description
        """
        try:
            schema_context = "Database Schema:\n"
            
            # Query to get all tables in the database
            cursor = self.connection.cursor()
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            print("Tables:", tables)
            
            for (table_name,) in tables:
                # Get column details for each table
                columns_query = f"DESCRIBE {table_name}"
                cursor.execute(columns_query)
                columns = cursor.fetchall()
                
                schema_context += f"Table: {table_name}\n"
                schema_context += "Columns: " + ", ".join([
                    f"{col[0]} ({col[1]})" for col in columns
                ]) + "\n\n"
            
            return schema_context
        
        except mysql.connector.Error as e:
            print(f"Error generating schema context: {e}")
            return ""
    
    def initialize_prompt(self, user_prompt, intent):
        """
        Generate SQL query using Ollama model
        
        Args:
            user_prompt (str): Natural language query description
            intent (str): Intent of the query (write, explain, execute)
        
        Returns:
            str: Generated SQL query
        """
        
        if intent == 'write':
            full_prompt = (
                f"{self.schema_context}\n\n"
                f"User Query: {user_prompt}\n\n"
                "Generate a precise SQL query based on the schema and user request. "
                "Ensure the query is syntactically correct and optimized."
            )
        elif intent == 'explain':
            full_prompt = (
                f"{self.schema_context}\n\n"
                f"User Query: {user_prompt}\n\n"
                "Explain the following SQL query in detail. "
                "Include the purpose of the query, the tables and columns involved, "
                "any joins or complex operations, and potential performance considerations."
            )
        elif intent == 'execute':
            full_prompt = (
                f"{self.schema_context}\n\n"
                f"User Query: {user_prompt}\n\n"
                "Explain the following SQL query in detail. "
                "Include the purpose of the query, the tables and columns involved, "
                "any joins or complex operations, and potential performance considerations."
            )
        else:
            raise ValueError(f"Invalid intent {intent}")
        
        return full_prompt

    def generate_query(self, user_prompt):
        
        try:
            response = ollama.generate(
                model=self.model,
                prompt=user_prompt,
                options={
                    'temperature': 0.2,  # Lower temperature for more deterministic results
                    'top_p': 0.9,
                    'max_tokens': 500
                }
            )
            
            return response['response']
        
        except Exception as e:
            print(f"Error generating query: {e}")
            return None

# Example Usage
def main():
    try:
        # Replace with your actual credentials
        assistant = DatabaseQueryAssistant()
        
        # Example query generation
        user_prompt = input("Query anything: ")
        intent = IntentClassifier().classify_intent(user_prompt, assistant.schema_context)
        print("user's intent:", intent)

        prompt = assistant.initialize_prompt(user_prompt, intent)
        generated_query = assistant.generate_query(prompt)
        
        # print("Response:", assistant.schema_context)
        
        print("Generated Query:", generated_query)
    
    except Exception as e:
        print(f"Initialization failed: {e}")

if __name__ == "__main__":
    main()