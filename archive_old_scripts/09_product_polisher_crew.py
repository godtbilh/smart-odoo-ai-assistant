# 09_product_polisher_crew.py

import os
import xmlrpc.client
from dotenv import load_dotenv

# --- CrewAI Imports ---
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type

# --- Load Environment Variables & Connect to Odoo ---
load_dotenv()
print("🚀 Odoo Product Polishing Crew: Online")
print("=" * 50)

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
    print(f"❌ Failed to connect to Odoo. Error: {e}")
    exit()

# --- 1. DEFINE ALL CUSTOM ODOO TOOLS ---

# Tool to find a product
class FindProductInput(BaseModel):
    product_name: str = Field(description="The name of the product to search for.")

class OdooFindProductTool(BaseTool):
    name: str = "Odoo Product Finder"
    description: str = "Finds a product in Odoo by name and returns its ID, name, and current sales description."
    args_schema: Type[BaseModel] = FindProductInput

    def _run(self, product_name: str) -> str:
        print(f"\nTOOL EXECUTING: Searching for product '{product_name}'...")
        try:
            search_domain = [('name', '=ilike', product_name)]
            fields = ['id', 'name', 'description_sale']
            product_data = models.execute_kw(db, uid, password, 'product.product', 'search_read',
                [search_domain], {'fields': fields, 'limit': 1})
            if product_data:
                return f"✅ Found product data: {product_data[0]}"
            else:
                return f"❌ Could not find a product named '{product_name}'."
        except Exception as e:
            return f"❌ An error occurred: {e}"

# Tool to update a product
class UpdateProductInput(BaseModel):
    product_id: int = Field(description="The unique integer ID of the product to update.")
    new_description: str = Field(description="The new, polished sales description to write to the product record.")

class OdooUpdateProductTool(BaseTool):
    name: str = "Odoo Product Updater"
    description: str = "Updates the sales description for a specific product using its ID."
    args_schema: Type[BaseModel] = UpdateProductInput

    def _run(self, product_id: int, new_description: str) -> str:
        print(f"\nTOOL EXECUTING: Updating product ID '{product_id}'...")
        try:
            update_values = {'description_sale': new_description}
            models.execute_kw(db, uid, password, 'product.product', 'write', [[product_id], update_values])
            return f"✅ Successfully updated product ID {product_id} in Odoo."
        except Exception as e:
            return f"❌ An error occurred during update: {e}"

# --- 2. ASSEMBLE THE AI WORKFORCE ---
print("\n--- Assembling the AI Workforce ---")

# LLM Configuration
gemini_llm = LLM(
    model="gemini/gemini-1.5-flash",
    api_key=os.environ["GOOGLE_API_KEY"]
)

# Instantiate your tools
find_tool = OdooFindProductTool()
update_tool = OdooUpdateProductTool()

# Define your agents
product_analyst = Agent(
    role="Product Data Analyst",
    goal="Fetch raw product data from the Odoo database accurately.",
    backstory="You are a meticulous data analyst who excels at querying databases for precise information.",
    tools=[find_tool], # This agent can only find things
    llm=gemini_llm,
    verbose=True
)

marketing_copywriter = Agent(
    role="Senior Marketing Copywriter",
    goal="Transform technical product data into compelling marketing copy that drives sales.",
    backstory="You are a creative writer with a knack for making any product sound appealing.",
    tools=[], # This agent has no database tools, its skill is writing
    llm=gemini_llm,
    verbose=True
)

odoo_operator = Agent(
    role="Odoo Database Operator",
    goal="Reliably execute data updates in the Odoo system.",
    backstory="You are a precise and careful operator who updates database records as instructed.",
    tools=[update_tool], # This agent can only update things
    llm=gemini_llm,
    verbose=True
)

print("✅ Agents are ready for their assignments.")

# --- 3. THE MAIN APPLICATION ---
if __name__ == "__main__":
    print("\n🎉 Welcome to the Odoo Product Polishing Crew!")
    product_name_to_polish = input("Enter the name of the product you want to polish: ").strip()

    if not product_name_to_polish:
        print("❌ No product name provided. Exiting.")
        exit()

    # --- 4. DEFINE THE ASSEMBLY LINE (THE TASKS) ---
    
    # Task 1: Find the product data
    find_task = Task(
        description=f"Go to the Odoo database and find the current data for the product named '{product_name_to_polish}'.",
        expected_output="A string containing the product's ID, name, and current sales description.",
        agent=product_analyst
    )

    # Task 2: Polish the description
    polish_task = Task(
        description="""Using the provided product data, rewrite the sales description to be more engaging, professional, and appealing to customers. 
        Focus on benefits over features. Keep the new description to two or three paragraphs.""",
        expected_output="A string containing only the new, polished product description.",
        agent=marketing_copywriter,
        context=[find_task] # This task depends on the output of the find_task!
    )

    # Task 3: Update the product in Odoo
    update_task = Task(
        description="""Take the polished description from the previous step and update the corresponding product in the Odoo database.
        You will need to extract the product ID from the initial research data.""",
        expected_output="A confirmation message stating that the product was successfully updated.",
        agent=odoo_operator,
        context=[find_task, polish_task] # This task uses context from BOTH previous tasks!
    )

    # --- 5. ASSEMBLE AND RUN THE CREW ---
    
    product_crew = Crew(
        agents=[product_analyst, marketing_copywriter, odoo_operator],
        tasks=[find_task, polish_task, update_task],
        process=Process.sequential,
        verbose=True
    )

    print("\n🚀 Crew has received its mission. Kicking off...")
    print("-" * 50)

    result = product_crew.kickoff()

    print("\n\n" + "-"*50)
    print("✅ MISSION COMPLETE! Final Report:")
    print(result)
