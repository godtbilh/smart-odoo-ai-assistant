# smart_assistant.py - Smart Multilingual AI Assistant with Fixed Multilingual Support

import os
import time
import random
import re
from dotenv import load_dotenv

# --- CrewAI Imports ---
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Optional

# --- Import our organized tools ---
from tools.odoo_connection import OdooConnection
from tools.customer_tools import OdooCustomerInfoTool
from tools.multilingual_product_tools import (
    OdooMultilingualProductFinder, 
    OdooMultilingualProductUpdater,
    MultilingualProductContentGenerator
)

load_dotenv()
print("🚀 Smart Multilingual AI Assistant: Online")
print("🎯 Capabilities: Customer Service | Product Management | Email Communication")
print("=" * 70)

# --- 1. Establish Odoo Connection ---
odoo_conn = OdooConnection()
if not odoo_conn.connect():
    print("❌ Failed to connect to Odoo. Exiting...")
    exit()

if not odoo_conn.test_connection():
    print("❌ Odoo connection test failed. Exiting...")
    exit()

# Get connection info for tools
conn_info = odoo_conn.get_connection_info()

# --- 2. Initialize Tools with Connection ---
customer_info_tool = OdooCustomerInfoTool(
    models=conn_info['models'],
    db=conn_info['db'],
    uid=conn_info['uid'],
    password=conn_info['password']
)

product_finder_tool = OdooMultilingualProductFinder(
    models=conn_info['models'],
    db=conn_info['db'],
    uid=conn_info['uid'],
    password=conn_info['password']
)

product_updater_tool = OdooMultilingualProductUpdater(
    models=conn_info['models'],
    db=conn_info['db'],
    uid=conn_info['uid'],
    password=conn_info['password']
)

content_generator_tool = MultilingualProductContentGenerator()

# --- 3. Email Communication Tool ---
class EmailDraftInput(BaseModel):
    recipient: str = Field(description="The recipient of the email")
    subject: str = Field(description="The email subject")
    language: str = Field(description="The language for the email (English, Dutch, French)")
    context: str = Field(description="Context or purpose of the email")

class EmailDraftTool(BaseTool):
    name: str = "Email Draft Generator"
    description: str = "Generates professional email drafts in multiple languages"
    args_schema: Type[BaseModel] = EmailDraftInput

    def _run(self, recipient: str, subject: str, language: str, context: str) -> str:
        print(f"\n✉️ TOOL EXECUTING: Drafting email to {recipient} in {language}...")
        
        result = f"Email Draft Request:\n"
        result += f"To: {recipient}\n"
        result += f"Subject: {subject}\n"
        result += f"Language: {language}\n"
        result += f"Context: {context}\n"
        result += f"Status: Ready for AI composition\n\n"
        
        result += "Instructions for AI Agent:\n"
        result += f"1. Write a professional email in {language}\n"
        result += f"2. Address the recipient as {recipient}\n"
        result += f"3. Use the subject: {subject}\n"
        result += f"4. Context: {context}\n"
        result += "5. Include appropriate greeting and closing\n"
        result += "6. Maintain professional business tone\n"
        
        return result

email_draft_tool = EmailDraftTool()

# --- 4. AI Workforce Assembly ---
print("\n--- Assembling the AI Workforce ---")

# LLM Configuration with rate limiting protection
gemini_llm = LLM(
    model="gemini/gemini-1.5-flash",
    api_key=os.environ["GOOGLE_API_KEY"],
    temperature=0.7
)

# Define agents with proper tool assignments
customer_service_agent = Agent(
    role='Customer Service Specialist',
    goal='Find customer contact details and order history in Odoo database efficiently.',
    backstory="You are an expert in querying the Odoo ERP system for customer information. You provide complete, accurate customer details and order history.",
    tools=[customer_info_tool],
    llm=gemini_llm,
    verbose=True,
    max_iter=1,  # Reduced to minimize API calls
    memory=False
)

product_specialist = Agent(
    role='Multilingual Product Management Specialist',
    goal='Handle all product-related tasks including finding, updating, and content generation in multiple languages (English, Dutch).',
    backstory="""You are an expert in Odoo product management with deep knowledge of multilingual content handling. 
    You can find products, generate compelling multilingual descriptions, and update product information across all languages.
    When updating products, you always generate content in both languages: English and Dutch.
    You focus on creating engaging, benefit-focused descriptions that appeal to customers.""",
    tools=[product_finder_tool, product_updater_tool, content_generator_tool],
    llm=gemini_llm,
    verbose=True,
    max_iter=2,  # Reduced to minimize API calls
    memory=False
)

email_communication_agent = Agent(
    role='Multilingual Email Communication Specialist',
    goal='Draft professional emails in the specified customer language (English, Dutch).',
    backstory="""You are an expert in business communication, fluent in English and Dutch. 
    You write professional, engaging emails that maintain appropriate tone and cultural sensitivity for each language.
    You always include proper greetings, clear content, and appropriate closings.""",
    tools=[email_draft_tool],
    llm=gemini_llm,
    verbose=True,
    max_iter=1,  # Reduced to minimize API calls
    memory=False
)

print("✅ Smart AI workforce is ready.")

# --- 5. Smart Request Analysis ---
def analyze_request_type(user_request: str) -> str:
    """Analyze user request and determine the appropriate routing"""
    request_lower = user_request.lower()
    
    # Customer-related keywords
    customer_keywords = ['customer', 'client', 'contact', 'who is', 'find customer', 'customer info']
    
    # Product-related keywords  
    product_keywords = ['product', 'item', 'update product', 'polish product', 'create product', 
                       'find product', 'description', 'multilingual', 'translate']
    
    # Email-related keywords
    email_keywords = ['email', 'draft', 'write email', 'send email', 'communication', 'message']
    
    # Analyze request type
    if any(keyword in request_lower for keyword in customer_keywords):
        return "customer_service"
    elif any(keyword in request_lower for keyword in product_keywords):
        return "product_management"
    elif any(keyword in request_lower for keyword in email_keywords):
        return "email_communication"
    else:
        return "general"

# --- 6. Main Application Loop ---
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
            
            # Add longer delay to prevent rate limiting
            delay = random.uniform(5, 8)
            print(f"⏳ Processing... ({delay:.1f}s)")
            time.sleep(delay)
            
            # Smart routing based on request analysis
            request_type = analyze_request_type(user_request)
            print(f"🧠 Request type identified: {request_type}")
            
            if request_type == "customer_service":
                print("📋 Routing to Customer Service...")
                main_task = Task(
                    description=f"Find the customer information requested in: '{user_request}'. Extract the customer name and search for their complete contact details and recent order history.",
                    expected_output="Complete customer information including contact details and recent orders with clear formatting.",
                    agent=customer_service_agent
                )
                agents_list = [customer_service_agent]
                tasks_list = [main_task]
                
            elif request_type == "product_management":
                print("🛠️ Routing to Product Management...")
                main_task = Task(
                    description=f"""Handle the product management request: '{user_request}'. 
                    
                    Follow this process:
                    1. First, search for the product using the product finder tool
                    2. If the request involves updating or improving content, generate compelling, professional descriptions in BOTH languages (English, Dutch)
                    3. Update the product in Odoo using the multilingual updater tool
                    4. Verify the updates were successful
                    
                    Focus on creating engaging, benefit-focused descriptions that highlight the product's value to customers.""",
                    expected_output="Complete product management action with results of searches, content generation in all languages, updates, and verification of success.",
                    agent=product_specialist
                )
                agents_list = [product_specialist]
                tasks_list = [main_task]
                
            elif request_type == "email_communication":
                print("✉️ Routing to Email Communication...")
                main_task = Task(
                    description=f"Draft the requested email: '{user_request}'. Use professional business tone and appropriate language. Include subject line and complete email body with proper greeting and closing.",
                    expected_output="A complete professional email draft with subject line and body in the requested language, properly formatted and ready to send.",
                    agent=email_communication_agent
                )
                agents_list = [email_communication_agent]
                tasks_list = [main_task]
                
            else:
                print("🔍 Routing to General Assistance...")
                main_task = Task(
                    description=f"Provide helpful assistance for this general request: '{user_request}'. Try to understand what the user needs and provide the most helpful response possible using available tools.",
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
                max_rpm=3  # Reduced from 8 to 3 requests per minute
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
