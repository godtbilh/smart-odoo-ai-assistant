# 12_multilingual_crew_final.py - Smart Multilingual AI Assistant with Dispatcher

import os
import xmlrpc.client
from dotenv import load_dotenv

# --- CrewAI Imports ---
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Optional
import time
import random
import re

load_dotenv()
print("🚀 Smart Multilingual AI Assistant: Online")
print("🎯 Capabilities: Customer Service | Product Management | Email Communication")
print("=" * 70)

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
    print(f"🔍 Connected as user ID: {uid}")
except Exception as e:
    print(f"❌ Failed to connect to Odoo. Error: {e}")
    exit()

# --- 2. Enhanced Multilingual Odoo Tools ---

class GetCustomerInfoInput(BaseModel):
    customer_name: str = Field(description="The full name of the customer you want to search for.")

class OdooGetInfoTool(BaseTool):
    name: str = "Odoo Customer Info Finder"
    description: str = "Finds contact details for a specific customer by their full name."
    args_schema: Type[BaseModel] = GetCustomerInfoInput
    
    def _run(self, customer_name: str) -> str:
        print(f"\n🔍 TOOL EXECUTING: Searching for customer '{customer_name}'...")
        try:
            search_domain = [('name', '=ilike', customer_name)]
            fields = ['name', 'email', 'phone', 'mobile', 'street', 'city']
            partner_data = models.execute_kw(db, uid, password, 'res.partner', 'search_read',
                [search_domain], {'fields': fields, 'limit': 1})
            
            if partner_data:
                customer = partner_data[0]
                print(f"✅ Found customer: {customer['name']}")
                
                try:
                    order_domain = [('partner_id', '=', customer['id'])]
                    order_fields = ['name', 'date_order', 'state', 'amount_total']
                    order_data = models.execute_kw(db, uid, password, 'sale.order', 'search_read',
                        [order_domain], {'fields': order_fields, 'limit': 3, 'order': 'date_order desc'})
                    
                    result = f"Customer: {customer['name']}\n"
                    result += f"Email: {customer.get('email', 'Not provided')}\n"
                    result += f"Phone: {customer.get('phone', 'Not provided')}\n"
                    result += f"Mobile: {customer.get('mobile', 'Not provided')}\n"
                    
                    if order_data:
                        result += f"\nRecent Orders ({len(order_data)}):\n"
                        for order in order_data:
                            result += f"- Order {order.get('name', 'N/A')} on {order.get('date_order', 'N/A')} (Status: {order.get('state', 'N/A')})\n"
                    else:
                        result += "\nNo recent orders found.\n"
                    
                    return result
                except Exception as order_error:
                    return f"Customer: {customer['name']}\nEmail: {customer.get('email', 'Not provided')}\nPhone: {customer.get('phone', 'Not provided')}\nNote: Could not retrieve order history."
            else:
                return f"No customer found matching '{customer_name}'. Please check the spelling or try a different name."
                
        except Exception as e:
            return f"Error searching for customer: {e}"

class FindProductInput(BaseModel):
    product_name: str = Field(description="The name of the product to search for.")

class OdooMultilingualProductFinder(BaseTool):
    name: str = "Odoo Multilingual Product Finder"
    description: str = "Finds product information including multilingual descriptions (English, Dutch, French)."
    args_schema: Type[BaseModel] = FindProductInput

    def _run(self, product_name: str) -> str:
        print(f"\n🔍 TOOL EXECUTING: Searching for product '{product_name}'...")
        try:
            search_domain = [('name', '=ilike', product_name)]
            fields = ['id', 'name', 'description_sale', 'list_price', 'categ_id']
            product_data = models.execute_kw(db, uid, password, 'product.product', 'search_read',
                [search_domain], {'fields': fields, 'limit': 5})
            
            if product_data:
                result = f"Found {len(product_data)} product(s):\n\n"
                for product in product_data:
                    result += f"Product ID: {product['id']}\n"
                    result += f"Name: {product['name']}\n"
                    result += f"Price: {product.get('list_price', 'N/A')}\n"
                    result += f"Category: {product.get('categ_id', ['N/A'])[1] if product.get('categ_id') else 'N/A'}\n"
                    result += f"Current Description: {product.get('description_sale', 'No description') or 'No description'}\n"
                    result += "-" * 40 + "\n"
                return result
            else:
                return f"No products found matching '{product_name}'. Try a broader search term."
                
        except Exception as e:
            return f"Error searching for product: {e}"

class UpdateProductInput(BaseModel):
    product_id: int = Field(description="The unique integer ID of the product to update.")
    field_name: str = Field(description="The field to update (e.g., 'name', 'description_sale').")
    new_content: str = Field(description="The new content for the specified field.")
    language: Optional[str] = Field(description="Language code (en_US, nl_NL, fr_FR) for multilingual fields.", default="en_US")

class OdooMultilingualProductUpdater(BaseTool):
    name: str = "Odoo Multilingual Product Updater"
    description: str = "Updates product fields with proper multilingual support (English, Dutch, French)."
    args_schema: Type[BaseModel] = UpdateProductInput

    def _run(self, product_id: int, field_name: str, new_content: str, language: str = "en_US") -> str:
        print(f"\n🔄 TOOL EXECUTING: Updating product ID {product_id}, field '{field_name}' in language '{language}'...")
        try:
            # For multilingual fields, we need to use the context to specify language
            context = {'lang': language}
            update_values = {field_name: new_content}
            
            models.execute_kw(db, uid, password, 'product.product', 'write', 
                [[product_id], update_values], {'context': context})
            
            return f"✅ Successfully updated product ID {product_id}, field '{field_name}' in {language}."
        except Exception as e:
            return f"❌ Error updating product: {e}"

class ProductContentGeneratorInput(BaseModel):
    base_info: str = Field(description="Base information about the product to generate content from.")
    content_type: str = Field(description="Type of content to generate: 'title', 'description', or 'features'.")
    target_language: str = Field(description="Target language: 'English', 'Dutch', or 'French'.")

class ProductContentGenerator(BaseTool):
    name: str = "Product Content Generator"
    description: str = "Generates compelling product titles, descriptions, or feature lists based on base information."
    args_schema: Type[BaseModel] = ProductContentGeneratorInput

    def _run(self, base_info: str, content_type: str, target_language: str) -> str:
        print(f"\n✍️ TOOL EXECUTING: Generating {content_type} in {target_language}...")
        
        # This tool doesn't actually call external APIs, it returns structured content
        # that the AI agent will then enhance based on the base_info provided
        
        result = f"Base Information Processed: {base_info}\n"
        result += f"Content Type: {content_type}\n"
        result += f"Target Language: {target_language}\n"
        result += f"Status: Ready for AI enhancement"
        
        return result

# --- 3. Simple Request Analysis Function ---
def analyze_request(user_request: str) -> dict:
    """Simple function to analyze user requests without tool complexity"""
    request_lower = user_request.lower()
    
    # Customer-related keywords
    customer_keywords = ['customer', 'client', 'contact', 'person', 'who is', 'find customer']
    
    # Product-related keywords
    product_keywords = ['product', 'item', 'update product', 'polish product', 'create product', 'find product']
    
    # Email-related keywords
    email_keywords = ['email', 'draft', 'write email', 'send email', 'communication']
    
    # Analyze request type
    if any(keyword in request_lower for keyword in customer_keywords):
        request_type = "customer_service"
    elif any(keyword in request_lower for keyword in product_keywords):
        request_type = "product_management"
    elif any(keyword in request_lower for keyword in email_keywords):
        request_type = "email_communication"
    else:
        request_type = "general"
    
    # Extract entities (simple pattern matching)
    entities = {}
    
    # Try to extract names (capitalized words)
    name_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
    potential_names = re.findall(name_pattern, user_request)
    if potential_names:
        entities['names'] = potential_names
    
    # Try to extract product IDs
    id_pattern = r'\bid\s*:?\s*(\d+)\b'
    product_ids = re.findall(id_pattern, request_lower)
    if product_ids:
        entities['product_ids'] = [int(id) for id in product_ids]
    
    # Try to extract languages
    language_pattern = r'\b(english|dutch|french|en|nl|fr)\b'
    languages = re.findall(language_pattern, request_lower)
    if languages:
        entities['languages'] = languages
    
    return {
        'request_type': request_type,
        'entities': entities,
        'original_request': user_request
    }

# --- 4. AI Workforce Assembly ---
print("\n--- Assembling the AI Workforce ---")

# LLM Configuration
gemini_llm = LLM(
    model="gemini/gemini-1.5-flash",
    api_key=os.environ["GOOGLE_API_KEY"],
    temperature=0.7
)

# Instantiate tools
customer_info_tool = OdooGetInfoTool()
product_finder_tool = OdooMultilingualProductFinder()
product_updater_tool = OdooMultilingualProductUpdater()
content_generator_tool = ProductContentGenerator()

# Define agents
dispatcher_agent = Agent(
    role='Smart Request Dispatcher',
    goal='Analyze user requests and route them to the appropriate specialist agents.',
    backstory="You are an intelligent dispatcher who understands different types of business requests and routes them efficiently.",
    tools=[],  # No tools needed, uses built-in intelligence
    llm=gemini_llm,
    verbose=True,
    max_iter=1,
    memory=False
)

customer_service_agent = Agent(
    role='Customer Service Specialist',
    goal='Find customer contact details and order history in Odoo database efficiently.',
    backstory="You are an expert in querying the Odoo ERP system for customer information.",
    tools=[customer_info_tool],
    llm=gemini_llm,
    verbose=True,
    max_iter=2,
    memory=False
)

product_specialist = Agent(
    role='Multilingual Product Management Specialist',
    goal='Handle all product-related tasks including finding, updating, and content generation in multiple languages.',
    backstory="You are an expert in Odoo product management with deep knowledge of multilingual content handling.",
    tools=[product_finder_tool, product_updater_tool, content_generator_tool],
    llm=gemini_llm,
    verbose=True,
    max_iter=3,
    memory=False
)

email_drafter = Agent(
    role='Multilingual Email Communication Specialist',
    goal='Draft professional emails in the specified customer language.',
    backstory="You are an expert in business communication, fluent in English, French, and Dutch.",
    tools=[],
    llm=gemini_llm,
    verbose=True,
    max_iter=1,
    memory=False
)

print("✅ Smart AI workforce is ready.")

# --- 5. The Main Application Loop ---
def main():
    print("\n🎉 Welcome to your Smart Multilingual AI Assistant!")
    print("💡 You can ask me to:")
    print("   • Find customer information: 'Who is customer Marina?'")
    print("   • Manage products: 'Update product Inloopdouche 120 with modern design features'")
    print("   • Draft emails: 'Draft a follow-up email to Marina in Dutch'")
    print("   • And much more - just ask naturally!")
    
    while True:
        try:
            user_request = input("\n🤖 What can I help you with? (or 'exit'): ").strip()
            if user_request.lower() in ["exit", "quit"]:
                print("👋 Goodbye!")
                break
            if not user_request:
                print("⚠️ Please enter your request.")
                continue

            print(f"\n🎯 Processing your request: '{user_request}'")
            
            # Add delay to prevent rate limiting
            delay = random.uniform(2, 4)
            print(f"⏳ Processing... ({delay:.1f}s)")
            time.sleep(delay)
            
            # --- SMART ROUTING: Direct task assignment based on keywords ---
            print(f"🧠 Analyzing request type...")
            
            if any(keyword in user_request.lower() for keyword in ['customer', 'client', 'contact', 'who is']):
                # Customer service path
                print("📋 Routing to Customer Service...")
                main_task = Task(
                    description=f"Find the customer information requested in: '{user_request}'. Extract the customer name and search for their contact details and recent orders.",
                    expected_output="Complete customer information including contact details and recent orders.",
                    agent=customer_service_agent
                )
                
                agents_list = [customer_service_agent]
                tasks_list = [main_task]
                
            elif any(keyword in user_request.lower() for keyword in ['product', 'update', 'polish', 'create']):
                # Product management path
                print("🛠️ Routing to Product Management...")
                main_task = Task(
                    description=f"Handle the product management request: '{user_request}'. First search for the product, then if updating content, generate compelling, professional descriptions and update the product in Odoo.",
                    expected_output="Complete product management action with results of any searches, updates, or content generation.",
                    agent=product_specialist
                )
                
                agents_list = [product_specialist]
                tasks_list = [main_task]
                
            elif any(keyword in user_request.lower() for keyword in ['email', 'draft', 'write']):
                # Email communication path
                print("✉️ Routing to Email Communication...")
                main_task = Task(
                    description=f"Draft the requested email: '{user_request}'. Use professional business tone and appropriate language. Include subject line and complete email body.",
                    expected_output="A complete professional email draft with subject line and body in the requested language.",
                    agent=email_drafter
                )
                
                agents_list = [email_drafter]
                tasks_list = [main_task]
                
            else:
                # General assistance - default to customer service
                print("🔍 Routing to General Assistance...")
                main_task = Task(
                    description=f"Provide helpful assistance for this general request: '{user_request}'. Try to understand what the user needs and provide the most helpful response possible.",
                    expected_output="A helpful response addressing the user's request as best as possible.",
                    agent=customer_service_agent
                )
                
                agents_list = [customer_service_agent]
                tasks_list = [main_task]

            # Assemble and run the crew
            smart_crew = Crew(
                agents=agents_list,
                tasks=tasks_list,
                process=Process.sequential,
                verbose=True,
                max_rpm=8
            )
            
            print("\n🚀 AI team is working on your request...")
            print("-" * 50)
            
            result = smart_crew.kickoff()
            
            print("\n" + "="*60)
            print("✅ TASK COMPLETE! Here's your result:")
            print("="*60)
            print(result)
            print("="*60)
            
        except KeyboardInterrupt:
            print("\n👋 Operation cancelled by user. Goodbye!")
            break
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "Too Many Requests" in error_msg:
                print("⚠️ Rate limit exceeded. Waiting 30 seconds...")
                time.sleep(30)
            else:
                print(f"\n❌ An error occurred: {e}")
            print("🔄 Please try again with a different request.")
            continue


if __name__ == "__main__":
    main()
