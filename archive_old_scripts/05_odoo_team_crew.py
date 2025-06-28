# 05_odoo_team_crew.py (Version 3 - Multi-agent team crew)

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

# --- 2. Define Custom Odoo Tools ---

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
            fields_to_read = ['name', 'email', 'phone', 'mobile']
            partner_data = models.execute_kw(db, uid, password, 'res.partner', 'search_read',
                [search_domain], {'fields': fields_to_read, 'limit': 1})
            if partner_data:
                return f"Successfully found customer data: {partner_data[0]}"
            else:
                return f"Could not find a customer named '{customer_name}'."
        except Exception as e:
            return f"An error occurred in the tool: {e}"

class GetCustomerOrdersInput(BaseModel):
    customer_name: str = Field(description="The full name of the customer whose orders you want to find.")

class OdooGetOrdersTool(BaseTool):
    name: str = "Odoo Customer Orders Finder"
    description: str = "Use this tool to find recent orders for a specific customer by providing their full name."
    args_schema: Type[BaseModel] = GetCustomerOrdersInput

    def _run(self, customer_name: str) -> str:
        print(f"\nTOOL EXECUTING: Searching for orders for '{customer_name}'...")
        try:
            # First find the customer
            search_domain = [('name', '=ilike', customer_name)]
            partner_data = models.execute_kw(db, uid, password, 'res.partner', 'search_read',
                [search_domain], {'fields': ['id', 'name'], 'limit': 1})
            
            if not partner_data:
                return f"Could not find customer '{customer_name}'"
            
            partner_id = partner_data[0]['id']
            
            # Find orders for this customer
            order_domain = [('partner_id', '=', partner_id)]
            order_data = models.execute_kw(db, uid, password, 'sale.order', 'search_read',
                [order_domain], {'fields': ['name', 'date_order', 'state', 'amount_total'], 'limit': 5})
            
            if order_data:
                return f"Found {len(order_data)} recent orders for {customer_name}: {order_data}"
            else:
                return f"No orders found for customer '{customer_name}'"
        except Exception as e:
            return f"An error occurred in the tool: {e}"

class GetProductInfoInput(BaseModel):
    product_name: str = Field(description="The name of the product you want to search for.")

class OdooGetProductTool(BaseTool):
    name: str = "Odoo Product Information Finder"
    description: str = "Use this tool to find product information by providing the product name."
    args_schema: Type[BaseModel] = GetProductInfoInput

    def _run(self, product_name: str) -> str:
        print(f"\nTOOL EXECUTING: Searching for product '{product_name}'...")
        try:
            search_domain = [('name', '=ilike', product_name)]
            fields_to_read = ['name', 'list_price', 'qty_available', 'categ_id']
            product_data = models.execute_kw(db, uid, password, 'product.product', 'search_read',
                [search_domain], {'fields': fields_to_read, 'limit': 3})
            
            if product_data:
                return f"Found {len(product_data)} products matching '{product_name}': {product_data}"
            else:
                return f"No products found matching '{product_name}'"
        except Exception as e:
            return f"An error occurred in the tool: {e}"

# --- 3. Create the LLM Configuration ---
print("-" * 30)
print("--- Building the Odoo Team ---")

# Configure the LLM to use Google Gemini
gemini_llm = LLM(
    model="gemini/gemini-1.5-flash",
    api_key=os.environ["GOOGLE_API_KEY"]
)

# --- 4. Create Specialized Agents ---

# Create tool instances
email_finder_tool = OdooGetEmailTool()
orders_finder_tool = OdooGetOrdersTool()
product_finder_tool = OdooGetProductTool()

# Customer Service Specialist
customer_service_agent = Agent(
    role='Customer Service Specialist',
    goal='Provide excellent customer service by finding customer contact information and order history.',
    backstory="""You are a dedicated customer service representative with expertise in the Odoo ERP system. 
    You excel at finding customer information quickly and accurately to help resolve customer inquiries.""",
    verbose=True,
    allow_delegation=True,
    tools=[email_finder_tool, orders_finder_tool],
    llm=gemini_llm
)

# Sales Analyst
sales_analyst = Agent(
    role='Sales Data Analyst',
    goal='Analyze customer purchase patterns and provide insights on sales data.',
    backstory="""You are a skilled sales analyst who specializes in interpreting customer data and sales patterns. 
    You can identify trends and provide valuable insights for business decisions.""",
    verbose=True,
    allow_delegation=True,
    tools=[orders_finder_tool],
    llm=gemini_llm
)

# Product Specialist
product_specialist = Agent(
    role='Product Information Specialist',
    goal='Provide detailed product information including pricing and availability.',
    backstory="""You are a product expert who knows the inventory inside and out. 
    You can quickly find product details, pricing, and availability information.""",
    verbose=True,
    allow_delegation=True,
    tools=[product_finder_tool],
    llm=gemini_llm
)

# Team Coordinator
coordinator = Agent(
    role='Team Coordinator',
    goal='Coordinate the team efforts and compile comprehensive reports.',
    backstory="""You are an experienced team leader who excels at coordinating different specialists 
    to provide comprehensive customer service. You synthesize information from multiple sources.""",
    verbose=True,
    allow_delegation=True,
    tools=[],
    llm=gemini_llm
)

print("✅ All agents created successfully.")

# --- 5. Define Tasks ---

# Task 1: Customer Information Gathering
customer_info_task = Task(
    description="""Find comprehensive information for customer 'A. Bendada' including:
    - Email address and contact information
    - Recent order history
    Provide a detailed summary of the customer's profile.""",
    expected_output="Complete customer profile with contact details and order history.",
    agent=customer_service_agent
)

# Task 2: Sales Analysis
sales_analysis_task = Task(
    description="""Analyze the sales data for customer 'A. Bendada':
    - Review their purchase patterns
    - Identify any trends in their ordering behavior
    - Provide insights for future customer engagement""",
    expected_output="Sales analysis report with insights and recommendations.",
    agent=sales_analyst
)

# Task 3: Product Recommendations
product_task = Task(
    description="""Based on the customer analysis, find information about products that might interest this customer.
    Look for popular products or items that complement their previous purchases.""",
    expected_output="Product recommendations with pricing and availability.",
    agent=product_specialist
)

# Task 4: Final Report Compilation
final_report_task = Task(
    description="""Compile all the information gathered by the team into a comprehensive customer service report.
    Include customer details, sales analysis, and product recommendations.""",
    expected_output="Comprehensive customer service report combining all team findings.",
    agent=coordinator
)

print("✅ All tasks defined.")

# --- 6. Assemble the Crew ---
# Simplified crew with fewer agents to reduce API calls
odoo_team_crew = Crew(
    agents=[customer_service_agent, coordinator],
    tasks=[customer_info_task, final_report_task],
    process=Process.sequential,
    verbose=True
)

print("✅ Team crew assembled. Starting the mission...")
print("-" * 50)

# --- 7. Run the Crew ---
if __name__ == "__main__":
    # Execute the team mission
    result = odoo_team_crew.kickoff()

    print("\n\n" + "="*50)
    print("TEAM MISSION COMPLETE!")
    print("="*50)
    print(result)
    print("="*50)
