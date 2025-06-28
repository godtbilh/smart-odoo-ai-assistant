# 06_interactive_crew.py - Interactive Terminal-based Odoo Agent Testing

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
print("🚀 Interactive Odoo Agent Testing System")
print("=" * 50)

# --- 1. Odoo Connection Logic ---
print("--- Initializing Odoo Connection ---")
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
        print(f"\n🔍 TOOL EXECUTING: Searching for '{customer_name}'...")
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

class GetCustomerOrdersInput(BaseModel):
    customer_name: str = Field(description="The full name of the customer whose orders you want to find.")

class OdooGetOrdersTool(BaseTool):
    name: str = "Odoo Customer Orders Finder"
    description: str = "Use this tool to find recent orders for a specific customer by providing their full name."
    args_schema: Type[BaseModel] = GetCustomerOrdersInput

    def _run(self, customer_name: str) -> str:
        print(f"\n📋 TOOL EXECUTING: Searching for orders for '{customer_name}'...")
        try:
            # First find the customer
            search_domain = [('name', '=ilike', customer_name)]
            partner_data = models.execute_kw(db, uid, password, 'res.partner', 'search_read',
                [search_domain], {'fields': ['id', 'name'], 'limit': 1})
            
            if not partner_data:
                return f"❌ Could not find customer '{customer_name}'"
            
            partner_id = partner_data[0]['id']
            
            # Find orders for this customer
            order_domain = [('partner_id', '=', partner_id)]
            order_data = models.execute_kw(db, uid, password, 'sale.order', 'search_read',
                [order_domain], {'fields': ['name', 'date_order', 'state', 'amount_total'], 'limit': 5})
            
            if order_data:
                return f"✅ Found {len(order_data)} recent orders for {customer_name}: {order_data}"
            else:
                return f"ℹ️ No orders found for customer '{customer_name}'"
        except Exception as e:
            return f"❌ An error occurred in the tool: {e}"

class GetProductInfoInput(BaseModel):
    product_name: str = Field(description="The name of the product you want to search for.")

class OdooGetProductTool(BaseTool):
    name: str = "Odoo Product Information Finder"
    description: str = "Use this tool to find product information by providing the product name."
    args_schema: Type[BaseModel] = GetProductInfoInput

    def _run(self, product_name: str) -> str:
        print(f"\n📦 TOOL EXECUTING: Searching for product '{product_name}'...")
        try:
            search_domain = [('name', '=ilike', product_name)]
            fields_to_read = ['name', 'list_price', 'qty_available', 'categ_id']
            product_data = models.execute_kw(db, uid, password, 'product.product', 'search_read',
                [search_domain], {'fields': fields_to_read, 'limit': 3})
            
            if product_data:
                return f"✅ Found {len(product_data)} products matching '{product_name}': {product_data}"
            else:
                return f"❌ No products found matching '{product_name}'"
        except Exception as e:
            return f"❌ An error occurred in the tool: {e}"

# --- 3. Create the LLM Configuration ---
print("\n--- Building the Odoo Agents ---")

# Configure the LLM to use Google Gemini
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
    You excel at finding customer information quickly and accurately to help resolve customer inquiries.
    Always provide clear, helpful responses to customer service requests.""",
    verbose=False,  # Reduced verbosity for cleaner terminal output
    allow_delegation=False,
    tools=[email_finder_tool, orders_finder_tool],
    llm=gemini_llm
)

# Sales Analyst
sales_analyst = Agent(
    role='Sales Data Analyst',
    goal='Analyze customer purchase patterns and provide insights on sales data.',
    backstory="""You are a skilled sales analyst who specializes in interpreting customer data and sales patterns. 
    You can identify trends and provide valuable insights for business decisions. You focus on actionable insights.""",
    verbose=False,
    allow_delegation=False,
    tools=[orders_finder_tool],
    llm=gemini_llm
)

# Product Specialist
product_specialist = Agent(
    role='Product Information Specialist',
    goal='Provide detailed product information including pricing and availability.',
    backstory="""You are a product expert who knows the inventory inside and out. 
    You can quickly find product details, pricing, and availability information. You provide clear product recommendations.""",
    verbose=False,
    allow_delegation=False,
    tools=[product_finder_tool],
    llm=gemini_llm
)

# Email Drafter
email_drafter = Agent(
    role='Email Communication Specialist',
    goal='Draft professional and effective email communications.',
    backstory="""You are an expert at writing professional business emails. You create clear, 
    concise, and effective email communications that get results. You always maintain a professional tone.""",
    verbose=False,
    allow_delegation=False,
    tools=[],
    llm=gemini_llm
)

print("✅ All agents created successfully.")

# --- 5. Interactive Functions ---

def test_customer_lookup():
    """Test the customer lookup functionality"""
    print("\n" + "="*50)
    print("🔍 TESTING: Customer Lookup")
    print("="*50)
    
    customer_name = input("Enter customer name to search for: ").strip()
    if not customer_name:
        print("❌ No customer name provided.")
        return
    
    # Create task
    task = Task(
        description=f"Find comprehensive information for customer '{customer_name}' including contact details and order history.",
        expected_output="Customer information with contact details and order history.",
        agent=customer_service_agent
    )
    
    # Create and run crew
    crew = Crew(
        agents=[customer_service_agent],
        tasks=[task],
        process=Process.sequential,
        verbose=False
    )
    
    print(f"\n🚀 Searching for customer: {customer_name}")
    try:
        result = crew.kickoff()
        print("\n" + "="*50)
        print("📋 RESULT:")
        print("="*50)
        print(result)
    except Exception as e:
        print(f"❌ Error occurred: {e}")

def test_product_search():
    """Test the product search functionality"""
    print("\n" + "="*50)
    print("📦 TESTING: Product Search")
    print("="*50)
    
    product_name = input("Enter product name to search for: ").strip()
    if not product_name:
        print("❌ No product name provided.")
        return
    
    # Create task
    task = Task(
        description=f"Find detailed information about the product '{product_name}' including pricing and availability.",
        expected_output="Product information with pricing and availability details.",
        agent=product_specialist
    )
    
    # Create and run crew
    crew = Crew(
        agents=[product_specialist],
        tasks=[task],
        process=Process.sequential,
        verbose=False
    )
    
    print(f"\n🚀 Searching for product: {product_name}")
    try:
        result = crew.kickoff()
        print("\n" + "="*50)
        print("📋 RESULT:")
        print("="*50)
        print(result)
    except Exception as e:
        print(f"❌ Error occurred: {e}")

def test_sales_analysis():
    """Test the sales analysis functionality"""
    print("\n" + "="*50)
    print("📊 TESTING: Sales Analysis")
    print("="*50)
    
    customer_name = input("Enter customer name for sales analysis: ").strip()
    if not customer_name:
        print("❌ No customer name provided.")
        return
    
    # Create task
    task = Task(
        description=f"Analyze the sales data and order history for customer '{customer_name}'. Provide insights about their purchasing patterns and recommendations for future engagement.",
        expected_output="Sales analysis with insights and recommendations.",
        agent=sales_analyst
    )
    
    # Create and run crew
    crew = Crew(
        agents=[sales_analyst],
        tasks=[task],
        process=Process.sequential,
        verbose=False
    )
    
    print(f"\n🚀 Analyzing sales data for: {customer_name}")
    try:
        result = crew.kickoff()
        print("\n" + "="*50)
        print("📋 RESULT:")
        print("="*50)
        print(result)
    except Exception as e:
        print(f"❌ Error occurred: {e}")

def test_email_drafting():
    """Test the email drafting functionality"""
    print("\n" + "="*50)
    print("✉️ TESTING: Email Drafting")
    print("="*50)
    
    customer_name = input("Enter customer name for email: ").strip()
    if not customer_name:
        print("❌ No customer name provided.")
        return
    
    email_purpose = input("Enter email purpose (e.g., 'follow-up on proposal', 'thank you', 'product inquiry'): ").strip()
    if not email_purpose:
        email_purpose = "follow-up"
    
    # Create tasks
    find_email_task = Task(
        description=f"Find the email address and contact information for customer '{customer_name}'.",
        expected_output="Customer's name and verified email address.",
        agent=customer_service_agent
    )
    
    draft_email_task = Task(
        description=f"""Using the customer information provided, draft a professional email for {email_purpose}.
        Keep the tone friendly and professional. Sign off as 'Your Odoo Team'.""",
        expected_output="A complete, well-formatted email including subject line, body, and closing.",
        agent=email_drafter,
        context=[find_email_task]
    )
    
    # Create and run crew
    crew = Crew(
        agents=[customer_service_agent, email_drafter],
        tasks=[find_email_task, draft_email_task],
        process=Process.sequential,
        verbose=False
    )
    
    print(f"\n🚀 Creating email for: {customer_name}")
    try:
        result = crew.kickoff()
        print("\n" + "="*50)
        print("📋 RESULT:")
        print("="*50)
        print(result)
    except Exception as e:
        print(f"❌ Error occurred: {e}")

def test_full_team_analysis():
    """Test the full team analysis with multiple agents"""
    print("\n" + "="*50)
    print("👥 TESTING: Full Team Analysis")
    print("="*50)
    
    customer_name = input("Enter customer name for comprehensive analysis: ").strip()
    if not customer_name:
        print("❌ No customer name provided.")
        return
    
    # Create tasks
    customer_info_task = Task(
        description=f"Find comprehensive information for customer '{customer_name}' including contact details and order history.",
        expected_output="Complete customer profile with contact details and order history.",
        agent=customer_service_agent
    )
    
    sales_analysis_task = Task(
        description=f"Analyze the sales data for customer '{customer_name}' and provide insights about their purchasing patterns.",
        expected_output="Sales analysis report with insights and recommendations.",
        agent=sales_analyst,
        context=[customer_info_task]
    )
    
    # Create and run crew
    crew = Crew(
        agents=[customer_service_agent, sales_analyst],
        tasks=[customer_info_task, sales_analysis_task],
        process=Process.sequential,
        verbose=False
    )
    
    print(f"\n🚀 Running full team analysis for: {customer_name}")
    try:
        result = crew.kickoff()
        print("\n" + "="*50)
        print("📋 RESULT:")
        print("="*50)
        print(result)
    except Exception as e:
        print(f"❌ Error occurred: {e}")

def show_menu():
    """Display the interactive menu"""
    print("\n" + "="*50)
    print("🤖 ODOO AGENT TESTING MENU")
    print("="*50)
    print("1. 🔍 Test Customer Lookup")
    print("2. 📦 Test Product Search")
    print("3. 📊 Test Sales Analysis")
    print("4. ✉️ Test Email Drafting")
    print("5. 👥 Test Full Team Analysis")
    print("6. ❌ Exit")
    print("="*50)

def main():
    """Main interactive loop"""
    print("\n🎉 Welcome to the Interactive Odoo Agent Testing System!")
    print("This tool allows you to test all your agents and tasks interactively.")
    
    while True:
        show_menu()
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            test_customer_lookup()
        elif choice == '2':
            test_product_search()
        elif choice == '3':
            test_sales_analysis()
        elif choice == '4':
            test_email_drafting()
        elif choice == '5':
            test_full_team_analysis()
        elif choice == '6':
            print("\n👋 Thank you for using the Odoo Agent Testing System!")
            break
        else:
            print("❌ Invalid choice. Please enter a number between 1-6.")
        
        input("\nPress Enter to continue...")

# --- 6. Run the Interactive System ---
if __name__ == "__main__":
    main()
