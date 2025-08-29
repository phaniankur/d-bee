# from intent_classifier import IntentClassifier
import time
import mysql.connector
from mysql.connector import Error
import ollama
from tabulate import tabulate
from dotenv import load_dotenv
import os
from typing import Optional, Any
from server.utils.redis_client import redis_client

# Load environment variables from .env file
load_dotenv()

# Database connection details from environment variables with default values
host = os.getenv('DB_HOST', '127.0.0.1')
port = int(os.getenv('DB_PORT', '3306'))
user = os.getenv('DB_USER', 'root')
password = os.getenv('DB_PASSWORD', '')
database = os.getenv('DB_NAME', 'db01')
model_name = os.getenv('MODEL_NAME', 'codellama:7b')
ttl = os.getenv('SCHEMA_TTL', 3600)


class DatabaseQueryAssistant:
    def __init__(self, ttl: int = 3600):
        try:
            # Database connection
            connection = mysql.connector.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database
            )

            if connection.is_connected():
                # Get server info
                db_info = connection.get_server_info()
                
                # Create a cursor object
                cursor = connection.cursor()
                
                # Execute a test query
                cursor.execute("SELECT DATABASE();")
                record = cursor.fetchone()
                if record and isinstance(record, tuple):
                    print("Connected to", record[0])
            
            # Store model and initialize schema context
            self.model = model_name
            self.connection = connection
            self.ttl = ttl
            self._schema_context = None
            self._last_fetched = 0
        
        except mysql.connector.Error as e:
            print("Db Error", e)
            raise
    
    def get_table_names(self):
        """
        Get a list of all table names in the database
        
        Returns:
            list: List of table names
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            
            # Extract table names from the result tuples
            table_names = [str(table[0]) for table in tables if table and len(table) > 0]
            return table_names
            
        except mysql.connector.Error as e:
            print(f"Error fetching table names: {e}")
            return []
    
    def _generate_schema_context(self):
        """
        Generate comprehensive database schema context
        
        Returns:
            str: Formatted schema description
        """
        try:
            schema_context = "Database Schema:\n"
            
            # Get all table names
            table_names = self.get_table_names()
            print("Tables:", table_names)
            
            cursor = self.connection.cursor()
            
            for table_name in table_names:
                # Get column details for each table
                columns_query = f"DESCRIBE {table_name}"
                cursor.execute(columns_query)
                columns = cursor.fetchall()
                
                schema_context += f"Table: {table_name}\n"
                schema_context += "Columns: " + ", ".join([
                    f"{str(col[0])} ({str(col[1])})" if isinstance(col, (tuple, list)) and len(col) > 1 
                    else "unknown" for col in columns
                ]) + "\n\n"
            
            return schema_context
        
        except mysql.connector.Error as e:
            print(f"Error generating schema context: {e}")
            return ""
    
    def _get_schema_cache_key(self) -> str:
        """Generate Redis key for storing schema cache."""
        return f"db_schema:{database}"

    def get_schema_context(self) -> str:
        """Return schema context, checking Redis cache first."""
        cache_key = self._get_schema_cache_key()
        
        # Try to get from Redis cache first
        cached_schema = redis_client.get(cache_key)
        if cached_schema:
            print("\n=== Using cached schema from Redis ===")
            self._schema_context = cached_schema
            self._last_fetched = time.time()
            return self._schema_context
            
        # If not in cache or cache miss, generate and cache it
        if not self._schema_context or (time.time() - self._last_fetched > self.ttl):
            print("\n=== Generating schema context ===")
            self._schema_context = self._generate_schema_context()
            self._last_fetched = time.time()
            
            # Cache in Redis with 1 week expiration (604800 seconds)
            if self._schema_context:
                redis_client.set(cache_key, self._schema_context, ex=604800)
                print("\n=== Schema cached in Redis for 1 week ===")
            
        return self._schema_context
        
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
                # f"User Query: {user_prompt}\n\n"
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
                "You are a helpful assistant that converts natural language into SQL queries.\n"
                "Analyze the following database schema carefully. Then, based on the user's input, generate a syntactically correct MySQL query that retrieves the correct data.\n"
                "Return SELECT, DESC, UPDATE queries **only**\n"
                "Return **only** the final SQL query without any explanations or extra text.\n\n"
                # f"User Request: {user_prompt}\n\n"
            )
        else:
            raise ValueError(f"Invalid intent {intent}")
        
        return full_prompt

    def generate_query(self, user_prompt: str) -> Optional[str]:
        # print(user_prompt)
        try:
            if not isinstance(self.model, str):
                raise ValueError("Model name must be a string")
                
            response = ollama.generate(
                model=self.model,
                prompt=user_prompt,
                options={
                    'temperature': 0.2,
                    'top_p': 0.9,
                    'max_tokens': 500
                }
            )
            
            return response['response']
        
        except Exception as e:
            print(f"Error generating query: {e}")
            return None
        
    def execute_query(self, query):
        """
        Execute a SQL query and return the results
        
        Args:
            query (str): SQL query to execute
        
        Returns:
            list: Query results
            
        Raises:
            mysql.connector.Error: If there is a database error
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            
            if cursor.description:  # Check if query returns results
                results = cursor.fetchall()
                columns = [col[0] for col in cursor.description]
                return {'columns': columns, 'results': results}
            else:
                self.connection.commit()  # For INSERT/UPDATE/DELETE queries
                return {'affected_rows': cursor.rowcount}
                
        except mysql.connector.Error as e:
            raise # Re-raise the database error
    
    def print_query_results(self, query_result):
        """
        Print SQL query results in a MySQL-style table format.

        Args:
            query_result (dict): The result from `execute_query`.
        """
        if query_result is None:
            print("No results to display due to an error.")
            return

        if isinstance(query_result, dict):
            if 'columns' in query_result and 'results' in query_result:
                print(tabulate(query_result['results'], headers=query_result['columns'], tablefmt='grid'))
            elif 'affected_rows' in query_result:
                print(f"Query OK, {query_result['affected_rows']} rows affected.")
            else:
                print("Unexpected result format.")
        else:
            print("Query result must be a dictionary.")

# Example Usage
def main():
    try:
        # Replace with your actual credentials
        assistant = DatabaseQueryAssistant()
        
        print("Query assistant started. Press Ctrl+C to exit.")
        while True:
            try:
                # Example query generation
                user_prompt = input("\nStart Querying: ")
                # intent = IntentClassifier().classify_intent(user_prompt, assistant.schema_context)
                # print("user's intent:", intent)

                prompt = assistant.initialize_prompt(user_prompt, "execute")
                # print("Response:", prompt)
                # generated_query = assistant.generate_query(prompt)
                # openRouterResult = execute_openrouter_api(prompt, user_prompt) // uncomment to test
                
                
                # print("Final Query:", openRouterResult)
                # query_result = assistant.execute_query(generated_query)
                # print("Query Result:", query_result)
                # assistant.print_query_results(query_result)
            
            except KeyboardInterrupt:
                print("\nExiting...")
                break
    
    except Exception as e:
        print(f"Initialization failed: {e}")

if __name__ == "__main__":
    main()