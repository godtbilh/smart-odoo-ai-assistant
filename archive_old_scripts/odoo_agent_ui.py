# odoo_agent_ui.py (Version 4 - With LLM Compatibility Fix)

import os
import xmlrpc.client
from dotenv import load_dotenv
import traceback

from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type

load_dotenv()
print("🚀 Odoo Agent Command Center: Online")
print("=" * 50)

# --- Odoo Connection Logic ---
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

# --- Custom Odoo Tools ---
class GetCustomerInfoInput(BaseModel):
    customer_name: str = Field(description="The full name of the customer you want to search for.")

class OdooGetInfoTool(BaseTool):
    name: str = "Odoo Customer Info Finder"
    description: str = "Finds contact details (email, phone) for a specific customer by their full name."
    args_schema: Type[BaseModel] = GetCustomerInfoInput
    def _run(self, customer_name: str) -> str:
        try:
            search_domain = [('name', '=ilike', customer_name)]
            fields_to_read = ['name', 'email', 'phone', 'mobile']
            partner_data = models.execute_kw(db, uid, password, 'res.partner', 'search_read',
                [search_domain], {'fields': fields_to_read, 'limit': 1})
            if partner_data:
                return f"✅ Successfully found customer data: {partner_data[0]}"
            else:
                return f"❌ Could not find a customer named '{customer_name}'."
        except Exception as e:
            return f"❌ An error occurred in the tool: {e}"

class OdooGetOrdersTool(BaseTool):
    name: str = "Odoo Customer Orders Finder"
    description: str = "Finds the 5 most recent sales orders for a specific customer by their full name."
    args_schema: Type[BaseModel] = GetCustomerInfoInput
    def _run(self, customer_name: str) -> str:
        try:
            partner_data = models.execute_kw(db, uid, password, 'res.partner', 'search_read',
                [[('name', '=ilike', customer_name)]], {'fields': ['id'], 'limit': 1})
            if not partner_data:
                return f"❌ Could not find customer '{customer_name}'"
            partner_id = partner_data[0]['id']
            order_data = models.execute_kw(db, uid, password, 'sale.order', 'search_read',
                [[('partner_id', '=', partner_id)]], {'fields': ['name', 'date_order', 'state', 'amount_total'], 'limit': 5})
            if order_data:
                return f"✅ Found {len(order_data)} orders for {customer_name}: {order_data}"
            else:
                return f"ℹ️ No orders found for customer '{customer_name}'"
        except Exception as e:
            return f"❌ An error occurred in the tool: {e}"

# --- LLM, Tools, and Agents Setup ---
print("\n--- Assembling the AI Workforce ---")

# --- Configure the LLM to use Google Gemini ---
try:
    gemini_llm = LLM(
        model="gemini/gemini-1.5-flash",
        api_key=os.environ["GOOGLE_API_KEY"]
    )
    print("✅ LLM configured successfully")
except Exception as e:
    print(f"❌ Failed to configure LLM: {e}")
    print("Please check your GOOGLE_API_KEY in the .env file")
    exit()

info_finder_tool = OdooGetInfoTool()
orders_finder_tool = OdooGetOrdersTool()

customer_service_agent = Agent(
    role='Customer Service Specialist',
    goal='Provide excellent customer service by finding customer contact information and order history.',
    backstory="You are a dedicated customer service representative with expertise in the Odoo ERP system.",
    tools=[info_finder_tool, orders_finder_tool],
    llm=gemini_llm,
    verbose=True
)
email_drafter = Agent(
    role='Email Communication Specialist',
    goal='Draft professional and effective email communications based on provided context.',
    backstory="You are an expert in writing professional business emails.",
    tools=[],
    llm=gemini_llm,
    verbose=True
)
print("✅ Agents are ready for their assignments.")


# --- Main Application Loop ---
def main():
    print("\n🎉 Welcome to your Odoo Agent Command Center!")
    while True:
        print("\nWhat would you like me to do? (e.g., 'Draft a follow-up for A. Bendada')")
        user_request = input("You: ").strip()
        if user_request.lower() in ["exit", "quit"]:
            print("\n👋 Goodbye!")
            break
        if not user_request:
            continue
        
        research_task = Task(
            description=f"A user wants to interact with a customer based on this request: '{user_request}'. First, find all relevant information for this request, including their contact details and recent order history.",
            expected_output="A summary of the customer's contact information and a list of their recent orders.",
            agent=customer_service_agent
        )
        drafting_task = Task(
            description=f"Based on the research from the previous step regarding '{user_request}', draft a professional email. Use the information provided to make the email relevant and personalized.",
            expected_output="A complete, well-formatted email draft ready to be sent.",
            agent=email_drafter,
            context=[research_task]
        )
        my_crew = Crew(
            agents=[customer_service_agent, email_drafter],
            tasks=[research_task, drafting_task],
            process=Process.sequential,
            verbose=True
        )
        
        print("\n🚀 Crew has received the mission. Kicking off...")
        print("-" * 50)
        try:
            result = my_crew.kickoff()
            print("\n" + "="*50)
            print("✅ MISSION COMPLETE! Final Report:")
            print("="*50)
            print(result)
        except Exception as e:
            print("\n" + "="*50)
            print("❌ A DETAILED ERROR OCCURRED. Please copy the text below.")
            print("="*50)
            traceback.print_exc()
            print("="*50)
        
        print("\n" + "="*50)
        input("Press Enter to give a new command...")

if __name__ == "__main__":
    main()
