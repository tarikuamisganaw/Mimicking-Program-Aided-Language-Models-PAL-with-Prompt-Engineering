import streamlit as st
from neo4j import GraphDatabase
from transformers import pipeline
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Neo4j connection class
class Neo4jConnection:
    def __init__(self, uri, user, pwd):
        """Initialize the Neo4j database connection."""
        self.__uri = uri
        self.__user = user
        self.__password = pwd
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__password))
        except Exception as e:
            st.error(f"Failed to create the Neo4j driver: {e}")

    def close(self):
        """Close the Neo4j database connection."""
        if self.__driver is not None:
            self.__driver.close()

    def query(self, query, parameters=None):
        """Execute a Cypher query on the Neo4j database."""
        assert self.__driver is not None, "Driver not initialized!"
        session = None
        response = None
        try:
            session = self.__driver.session()
            response = list(session.run(query, parameters))
        except Exception as e:
            st.error(f"Query execution failed: {e}")
        finally:
            if session is not None:
                session.close()
        return response

# Fetch sensitive data from the environment variables
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# Initialize Neo4j connection
neo4j_conn = Neo4jConnection(uri=NEO4J_URI, user=NEO4J_USER, pwd=NEO4J_PASSWORD)

# Load the Hugging Face model for text generation
generator = pipeline("text-generation", model="distilgpt2")

# Streamlit UI
st.title("Program-Aided Language Model for Cypher Query Generation")

# Initialize session state
if "generated_code" not in st.session_state:
    st.session_state.generated_code = ""
if "modified_code" not in st.session_state:
    st.session_state.modified_code = ""
if "query_results" not in st.session_state:
    st.session_state.query_results = []
if "reasoning_steps" not in st.session_state:
    st.session_state.reasoning_steps = ""

# Input for the natural language query
user_query = st.text_input("Enter your natural language query", "")

if st.button("Generate Python Code"):
    if user_query:
        # Few-shot prompt examples to guide the model's response
        few_shot_examples = """
        Example 1:
        Natural language: "Find all users in New York."
        Reasoning: Generate a Cypher query to retrieve all User nodes.
        Python code:
        query = "MATCH (u:User {city: 'New York'}) RETURN u.name, u"
        results = neo4j_conn.query(query)

        Example 2:
        Natural language: "Count all users older than 30"
        Reasoning: Generate a Cypher query to count users with age > 30.
        Python code:
        query = "MATCH (u:User) WHERE u.age > 30 RETURN COUNT(u)"
        results = neo4j_conn.query(query)

        Example 3:
        Natural language: "Get all movies released after 2020"
        Reasoning: Create a Cypher query to find movies released after 2020.
        Python code:
        query = "MATCH (m:Movie) WHERE m.release_date > 2020 RETURN m.title"
        results = neo4j_conn.query(query)
        """

        # Create the prompt for the language model
        prompt = f"""
        Translate the following natural language query into intermediate reasoning steps and Python code for Neo4j interaction.
        
        {few_shot_examples}

        Natural language: "{user_query}"

        Intermediate reasoning steps:
        """

        # Generate the reasoning steps and Python code
        output = generator(prompt, max_new_tokens=150, truncation=True)[0]['generated_text'].strip()

        # Extract reasoning steps and generated code from the output
        parts = output.split("Python code:")
        if len(parts) > 1:
            reasoning_steps = parts[0].strip()
            generated_code = parts[1].strip()
        else:
            st.warning("Could not generate valid Python code.")
            reasoning_steps = output.strip()
            generated_code = ""

        # Store generated code and reasoning in session state
        st.session_state.generated_code = generated_code
        st.session_state.modified_code = generated_code
        st.session_state.reasoning_steps = reasoning_steps

# Display reasoning steps and generated code
if st.session_state.reasoning_steps:
    st.write("Reasoning Steps:")
    st.text(st.session_state.reasoning_steps)

if st.session_state.generated_code:
    st.write("Generated Python Code:")
    st.code(st.session_state.generated_code, language="python")

# Allow the user to modify the generated Python code
modified_code = st.text_area("Modify the generated code if necessary:", st.session_state.modified_code)
st.session_state.modified_code = modified_code

# Execute the code when the button is pressed
if st.button("Run Generated Code"):
    try:
        # Clean up the modified code
        clean_code = modified_code.strip()

        # Execute the modified Python code
        exec_globals = {'neo4j_conn': neo4j_conn}  # Provide Neo4j connection context
        exec(clean_code, exec_globals)  # Execute the code in a safe namespace

        # Retrieve and format the results
        results = exec_globals.get('results', None)
        if results is not None:
            # Use a built-in function to format the results as JSON-like data
            formatted_results = [dict(record) for record in results]

            # Display query results in JSON format
            st.write("Query Results:")
            st.json(formatted_results)

    except Exception as e:
        st.error(f"Code execution failed: {e}")

# Close the Neo4j connection when the app finishes
neo4j_conn.close()
