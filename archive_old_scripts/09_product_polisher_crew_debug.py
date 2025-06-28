# 09_product_polisher_crew_debug.py - Enhanced version with verification and debugging

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
print("🚀 Odoo Product Polishing Crew: Online (Debug Version)")
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
    print(f"🔍 Connected as user ID: {uid}")
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
        print(f"\n🔍 TOOL EXECUTING: Searching for product '{product_name}'...")
        try:
            search_domain = [('name', '=ilike', product_name)]
            fields = ['id', 'name', 'description_sale', 'description', 'description_purchase']
            product_data = models.execute_kw(db, uid, password, 'product.product', 'search_read',
                [search_domain], {'fields': fields, 'limit': 1})
            if product_data:
                product = product_data[0]
                print(f"📋 BEFORE UPDATE - Product Details:")
                print(f"   ID: {product['id']}")
                print(f"   Name: {product['name']}")
                print(f"   Sales Description: {product.get('description_sale', 'None')}")
                print(f"   Internal Description: {product.get('description', 'None')}")
                print(f"   Purchase Description: {product.get('description_purchase', 'None')}")
                return f"✅ Found product data: {product}"
            else:
                return f"❌ Could not find a product named '{product_name}'."
        except Exception as e:
            return f"❌ An error occurred: {e}"

# Tool to update a product with verification
class UpdateProductInput(BaseModel):
    product_id: int = Field(description="The unique integer ID of the product to update.")
    new_description: str = Field(description="The new, polished sales description to write to the product record.")

class OdooUpdateProductTool(BaseTool):
    name: str = "Odoo Product Updater"
    description: str = "Updates the sales description for a specific product using its ID and verifies the change."
    args_schema: Type[BaseModel] = UpdateProductInput

    def _run(self, product_id: int, new_description: str) -> str:
        print(f"\n🔧 TOOL EXECUTING: Updating product ID '{product_id}'...")
        print(f"📝 New description to write: {new_description[:100]}...")
        
        try:
            # First, get the current description for comparison
            current_data = models.execute_kw(db, uid, password, 'product.product', 'read',
                [product_id], {'fields': ['description_sale', 'name']})
            
            if not current_data:
                return f"❌ Product ID {product_id} not found."
            
            current_desc = current_data[0].get('description_sale', '')
            product_name = current_data[0].get('name', 'Unknown')
            
            print(f"📋 BEFORE UPDATE:")
            print(f"   Product: {product_name}")
            print(f"   Current description: {current_desc}")
            
            # Perform the update
            update_values = {'description_sale': new_description}
            result = models.execute_kw(db, uid, password, 'product.product', 'write', 
                [[product_id], update_values])
            
            print(f"🔄 Update operation result: {result}")
            
            # Verify the update by reading the data again
            updated_data = models.execute_kw(db, uid, password, 'product.product', 'read',
                [product_id], {'fields': ['description_sale', 'name', 'write_date']})
            
            if updated_data:
                updated_desc = updated_data[0].get('description_sale', '')
                write_date = updated_data[0].get('write_date', 'Unknown')
                
                print(f"📋 AFTER UPDATE:")
                print(f"   Product: {product_name}")
                print(f"   Updated description: {updated_desc}")
                print(f"   Last write date: {write_date}")
                
                # Check if the update actually worked
                if updated_desc == new_description:
                    return f"✅ Successfully updated and VERIFIED product ID {product_id} in Odoo. Last modified: {write_date}"
                else:
                    return f"⚠️ Update command executed but verification failed. Expected: {new_description[:50]}... Got: {updated_desc[:50]}..."
            else:
                return f"❌ Could not verify update for product ID {product_id}."
                
        except Exception as e:
            return f"❌ An error occurred during update: {e}"

# Tool to verify the final result
class VerifyProductInput(BaseModel):
    product_id: int = Field(description="The unique integer ID of the product to verify.")

class OdooVerifyProductTool(BaseTool):
    name: str = "Odoo Product Verifier"
    description: str = "Verifies the current state of a product after updates."
    args_schema: Type[BaseModel] = VerifyProductInput

    def _run(self, product_id: int) -> str:
        print(f"\n🔍 TOOL EXECUTING: Verifying product ID '{product_id}'...")
        try:
            fields = ['id', 'name', 'description_sale', 'write_date', 'write_uid']
            product_data = models.execute_kw(db, uid, password, 'product.product', 'read',
                [product_id], {'fields': fields})
            
            if product_data:
                product = product_data[0]
                print(f"📋 FINAL VERIFICATION:")
                print(f"   ID: {product['id']}")
                print(f"   Name: {product['name']}")
                print(f"   Sales Description: {product.get('description_sale', 'None')}")
                print(f"   Last Modified: {product.get('write_date', 'Unknown')}")
                print(f"   Modified by User ID: {product.get('write_uid', 'Unknown')}")
                return f"✅ Verification complete: {product}"
            else:
                return f"❌ Could not verify product ID {product_id}."
        except Exception as e:
            return f"❌ An error occurred during verification: {e}"

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
verify_tool = OdooVerifyProductTool()

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
    goal="Reliably execute data updates in the Odoo system with full verification.",
    backstory="You are a precise and careful operator who updates database records and always verifies the changes.",
    tools=[update_tool], # This agent can only update things
    llm=gemini_llm,
    verbose=True
)

quality_inspector = Agent(
    role="Quality Control Inspector",
    goal="Verify that all database changes have been properly applied.",
    backstory="You are a thorough inspector who double-checks all work to ensure quality and accuracy.",
    tools=[verify_tool], # This agent verifies the final result
    llm=gemini_llm,
    verbose=True
)

print("✅ Agents are ready for their assignments.")

# --- 3. THE MAIN APPLICATION ---
if __name__ == "__main__":
    print("\n🎉 Welcome to the Odoo Product Polishing Crew! (Debug Version)")
    product_name_to_polish = input("Enter the name of the product you want to polish: ").strip()

    if not product_name_to_polish:
        print("❌ No product name provided. Exiting.")
        exit()

    # --- 4. DEFINE THE ASSEMBLY LINE (THE TASKS) ---
    
    # Task 1: Find the product data
    find_task = Task(
        description=f"Go to the Odoo database and find the current data for the product named '{product_name_to_polish}'. Show all description fields.",
        expected_output="A string containing the product's ID, name, and current sales description with detailed logging.",
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

    # Task 3: Update the product in Odoo with verification
    update_task = Task(
        description="""Take the polished description from the previous step and update the corresponding product in the Odoo database.
        You will need to extract the product ID from the initial research data. Verify that the update was successful.""",
        expected_output="A confirmation message with verification that the product was successfully updated.",
        agent=odoo_operator,
        context=[find_task, polish_task] # This task uses context from BOTH previous tasks!
    )

    # Task 4: Final verification
    verify_task = Task(
        description="""Perform a final verification of the product update by reading the current state of the product from the database.
        Extract the product ID from the previous tasks and confirm the changes are visible.""",
        expected_output="A detailed verification report showing the final state of the product.",
        agent=quality_inspector,
        context=[find_task, update_task] # This task verifies the update
    )

    # --- 5. ASSEMBLE AND RUN THE CREW ---
    
    product_crew = Crew(
        agents=[product_analyst, marketing_copywriter, odoo_operator, quality_inspector],
        tasks=[find_task, polish_task, update_task, verify_task],
        process=Process.sequential,
        verbose=True
    )

    print("\n🚀 Crew has received its mission. Kicking off...")
    print("-" * 50)

    result = product_crew.kickoff()

    print("\n\n" + "-"*50)
    print("✅ MISSION COMPLETE! Final Report:")
    print(result)
    print("-" * 50)
    
    print("\n🔍 DEBUGGING SUMMARY:")
    print("If you still don't see changes in Odoo UI, try:")
    print("1. Hard refresh the browser (Ctrl+F5)")
    print("2. Check the 'Sales Description' field specifically")
    print("3. Verify you're looking at the correct product variant")
    print("4. Check if you have proper permissions to edit products")
