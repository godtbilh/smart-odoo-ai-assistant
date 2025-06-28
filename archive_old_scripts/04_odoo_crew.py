# 04_odoo_crew.py (Version 2 - with a single agent crew)

import os
import xmlrpc.client
from dotenv import load_dotenv

# --- CrewAI & Pydantic Imports ---
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type

# --- Load Environment Variables ---
load_dotenv()
print("--- Initializing Odoo Connection ---")

# --- 1. Odoo Connection Logic ---
# This part is the same and should be working for you.
try:
    url = os.environ["ODOO_URL"]
    db = os.environ["ODOO_DB"]
    username = os.environ["ODOO_USERNAME"]
    password = os.environ["ODOO_PASSWORD"]
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    print("✅ Successfully connected and authenticated with Odoo.")
except Exception as e:
    print(f"❌ Failed to connect to Odoo. Check your .env file and connection. Error: {e}")
    exit()


# --- 2. Define the Custom Odoo Tool ---
# This is your working tool class from the last step.
class GetCustomerEmailInput(BaseModel):
    customer_name: str = Field(description="The full name of the customer you want to search for.")

class OdooGetEmailTool(BaseTool):
    name: str = "Odoo Customer Email Finder"
    description: str = "Use this tool to find the email address for a specific customer by providing their full name."
    args_schema: Type[BaseModel] = GetCustomerEmailInput

    def _run(self, customer_name: str) -> str:
        print(f"\nTOOL EXECUTING: Searching for '{customer_name}'...")
        try:
            search_domain = [('name', '=ilike', customer_name)]
            fields_to_read = ['name', 'email']
            partner_data = models.execute_kw(db, uid, password, 'res.partner', 'search_read',
                [search_domain], {'fields': fields_to_read, 'limit': 1})
            if partner_data and partner_data[0].get('email'):
                return f"Successfully found data: {partner_data[0]}"
            else:
                return f"Could not find a customer named '{customer_name}' or they do not have an email."
        except Exception as e:
            return f"An error occurred in the tool: {e}"

# --- 3. Create the Agent ---
print("-" * 30)
print("--- Building the Odoo Agent ---")

# Configure the LLM to use Google Gemini
gemini_llm = LLM(
    model="gemini/gemini-1.5-flash",
    api_key=os.environ["GOOGLE_API_KEY"]
)

# First, we create an instance of our tool.
email_finder_tool = OdooGetEmailTool()

# Now, we define our first specialized agent.
odoo_specialist = Agent(
  role='Odoo Database Inquiry Specialist',
  goal='Accurately retrieve customer information from the Odoo database.',
  backstory="""You are an expert at querying the Odoo ERP system. 
  You are meticulous and only provide information that you can verify directly from the database.
  You use the tools at your disposal to find the facts.""",
  verbose=True,
  allow_delegation=False,
  tools=[email_finder_tool], # We give our agent the tool we built!
  llm=gemini_llm
)
print("✅ Odoo Specialist Agent created.")

# --- 4. Define the Task and Assemble the Crew ---

# We define a specific task for the agent to accomplish.
inquiry_task = Task(
  description="I need to send an urgent follow-up email. What is the precise email address for the customer 'A. Bendada'?",
  expected_output="The final, verified email address for the specified customer.",
  agent=odoo_specialist # Assign the task to our agent
)
print("✅ Task defined.")

# Assemble a simple crew with our single agent and task.
my_crew = Crew(
  agents=[odoo_specialist],
  tasks=[inquiry_task],
  process=Process.sequential,
  verbose=True
)
print("✅ Crew assembled. Kicking off the mission...")
print("-" * 30)

# --- 5. Run the Crew ---
if __name__ == "__main__":
    # We "kick off" the crew to start the work.
    result = my_crew.kickoff()

    print("\n\n" + "-"*30)
    print("MISSION COMPLETE! Here is the final result:")
    print(result)
