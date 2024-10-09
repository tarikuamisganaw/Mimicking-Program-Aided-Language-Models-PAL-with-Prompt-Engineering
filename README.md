Program-Aided Language Model (PAL) with Prompt Engineering for Neo4j Query Generation
Task Overview

This project explores the concept of Program-Aided Language Models (PAL) through prompt engineering. The objective is to guide a Language Model (LLM) to generate intermediate outputs that resemble a program or structured reasoning process. Additionally, user interaction is provided to "interfere" with these outputs and improve the final result.
Objectives:

Mimic PAL: Design a system that mimics PAL using prompt engineering techniques.
Structured Reasoning: Guide an LLM (Hugging Face's distilgpt2) to generate intermediate reasoning steps and corresponding Python code that interacts with a Neo4j database.
User Interference: Allow users to inspect, modify, and improve the generated Python code before execution.
Final Execution: The system runs the modified Python code and returns query results in a flexible, JSON format.

How This Project Achieves the PAL Challenge:

Guided Generation of Intermediate Outputs: The LLM is prompted to generate structured reasoning steps for each query. For example, if a user asks "Find all users," the model generates reasoning like:
    "Step 1: Fetch all User nodes."
    "Step 2: Return the properties of users."

This reasoning is followed by Python code that translates these steps into Cypher queries.

User Interference: After the Python code is generated, the user can modify the code through a text area before executing it. This allows the user to adjust the query or logic and directly interfere with the generated output for better results.

Execution and Display of Results: Once the code is executed, the query results are displayed in a flexible JSON format, which adapts to the structure of the returned records. The system uses exec() to safely execute the modified Python code, and the results are serialized and displayed as JSON for clarity.
here is a demo video:Screencast.from.09-10-2024.10.39.23.webm

