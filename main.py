from intent_classifier import IntentClassifier
import mysql.connector
from mysql.connector import Error
import ollama
from tabulate import tabulate

# Database connection details
host = "127.0.0.1"
port = 3306
user = "root"
password = None
database = "db01"
# model_name='sqlcoder'
model_name='codellama:7b'
# model_name='llama3.1:latest'


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
                "You are a helpful assistant that converts natural language into SQL queries.\n"
                "Analyze the following database schema carefully. Then, based on the user's input, generate a syntactically correct MySQL query that retrieves the correct data.\n"
                "Return SELECT, DESC, UPDATE queries **only**\n"
                "Return **only** the final SQL query without any explanations or extra text.\n\n"
                f"User Request: {user_prompt}\n\n"
            )
        else:
            raise ValueError(f"Invalid intent {intent}")
        
        return full_prompt

    def generate_query(self, user_prompt):
        
        print(user_prompt)
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
        
    def execute_query(self, query):
        """
        Execute a SQL query and return the results
        
        Args:
            query (str): SQL query to execute
        
        Returns:
            list: Query results
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
            print(f"Error executing query: {e}")
            return None
    
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
                print("Response:", prompt)
                generated_query = assistant.generate_query(prompt)
                
                
                print("Final Query:", generated_query)
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