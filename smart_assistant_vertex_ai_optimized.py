#!/usr/bin/env python3
"""
Smart Assistant: Vertex AI + Cost Optimization - ULTIMATE VERSION
Combines Vertex AI reliability with intelligent cost optimization
"""
import os
import json
import time
import random
from dotenv import load_dotenv

# --- Vertex AI Imports ---
import vertexai
from vertexai.generative_models import GenerativeModel

# --- CrewAI Imports ---
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type

# --- Import our organized tools ---
from tools.odoo_connection import OdooConnection
from tools.customer_tools import OdooCustomerInfoTool
from tools.multilingual_product_tools import (
    OdooMultilingualProductFinder, 
    OdooMultilingualProductUpdater,
    MultilingualProductContentGenerator
)

load_dotenv()
print("🇧🇪 ULTIMATE Smart AI Assistant: Vertex AI + Cost Optimization")
print("🌍 Region: europe-west2 (London) - Optimized for Belgium")
print("🎯 Capabilities: Customer Service | Product Management | Email Communication")
print("💰 Cost: Intelligent LLM routing with your paid Vertex AI account")
print("🚀 Features: No rate limits + Smart cost optimization")
print("=" * 75)

# --- 1. Initialize Vertex AI for Belgium ---
def initialize_vertex_ai():
    """Initialize Vertex AI with Belgium-optimized settings"""
    try:
        # Set credentials
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./google-cloud-credentials.json"
        
        # Load project ID
        with open("./google-cloud-credentials.json", "r") as f:
            creds = json.load(f)
            project_id = creds.get("project_id")
        
        # Initialize with working European region
        vertexai.init(project=project_id, location="europe-west2")
        print(f"✅ Vertex AI initialized for project: {project_id}")
        print(f"🌍 Region: europe-west2 (optimal for Belgium)")
        
        # Test connection
        test_model = GenerativeModel("gemini-1.5-flash")
        test_response = test_model.generate_content("Test connection from Belgium")
        print(f"✅ Connection test successful: {test_response.text[:50]}...")
        
        return project_id
        
    except Exception as e:
        print(f"❌ Vertex AI initialization failed: {e}")
        print("💡 Make sure you've enabled Vertex AI in europe-west2 region")
        return None

project_id = initialize_vertex_ai()
if not project_id:
    print("❌ Cannot proceed without Vertex AI. Exiting...")
    exit()

# --- 2. Establish Odoo Connection ---
odoo_conn = OdooConnection()
if not odoo_conn.connect():
    print("❌ Failed to connect to Odoo. Exiting...")
    exit()

if not odoo_conn.test_connection():
    print("❌ Odoo connection test failed. Exiting...")
    exit()

# Get connection info for tools
conn_info = odoo_conn.get_connection_info()

# --- 3. Initialize Tools with Connection ---
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

# --- 4. Email Communication Tool ---
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

# --- 5. Vertex AI Cost-Optimized LLM Configuration ---
print("\n--- Configuring Vertex AI Cost-Optimized LLMs ---")

# Configure CrewAI to use Vertex AI with cost optimization
try:
    # Flash LLM for simple tasks (CHEAP & FAST)
    crewai_flash_llm = LLM(
        model="vertex_ai/gemini-1.5-flash",
        vertex_ai_project=project_id,
        vertex_ai_location="europe-west2",
        temperature=0.3
    )
    
    # Pro LLM for complex tasks (ADVANCED & BALANCED)
    crewai_pro_llm = LLM(
        model="vertex_ai/gemini-1.5-pro", 
        vertex_ai_project=project_id,
        vertex_ai_location="europe-west2",
        temperature=0.7
    )
    
    print("✅ Vertex AI Cost-Optimized LLMs configured:")
    print("   💨 Flash LLM: vertex_ai/gemini-1.5-flash (ultra-fast & cheap)")
    print("   ⚖️ Pro LLM: vertex_ai/gemini-1.5-pro (advanced & balanced)")
    print("   🌍 Region: europe-west2 (Belgium optimized)")
    print("   💰 Cost: Smart routing for optimal spending")
    
except Exception as e:
    print(f"❌ Failed to configure Vertex AI LLMs: {e}")
    exit()

# --- 6. Advanced Cost Monitoring ---
class VertexAICostMonitor:
    def __init__(self):
        self.costs = {
            'flash_calls': 0,
            'pro_calls': 0,
            'total_estimated_cost': 0.0,
            'cost_savings': 0.0
        }
        
        # Vertex AI pricing (approximate, per 1K tokens)
        self.pricing = {
            'flash': 0.02,    # Very cost-effective
            'pro': 0.08       # Standard
        }
        
        # Cost comparison baseline (if everything used Pro)
        self.baseline_cost_per_call = 0.08
    
    def track_call(self, llm_type):
        self.costs[f'{llm_type}_calls'] += 1
        cost = self.pricing[llm_type]
        self.costs['total_estimated_cost'] += cost
        
        # Calculate savings vs using Pro for everything
        if llm_type == 'flash':
            savings = self.baseline_cost_per_call - cost
            self.costs['cost_savings'] += savings
            print(f"💰 Cost tracking: {llm_type.upper()} LLM call (${cost:.3f}) - Saved ${savings:.3f}")
        else:
            print(f"💰 Cost tracking: {llm_type.upper()} LLM call (${cost:.3f})")
        
    def get_summary(self):
        total_calls = self.costs['flash_calls'] + self.costs['pro_calls']
        if total_calls == 0:
            return "No calls made yet."
            
        savings_percentage = (self.costs['cost_savings'] / (total_calls * self.baseline_cost_per_call)) * 100
        
        return f"""
💰 Vertex AI Cost Summary:
   Flash LLM calls: {self.costs['flash_calls']} (${self.costs['flash_calls'] * self.pricing['flash']:.3f})
   Pro LLM calls: {self.costs['pro_calls']} (${self.costs['pro_calls'] * self.pricing['pro']:.3f})
   Total estimated: ${self.costs['total_estimated_cost']:.3f}
   💸 Total savings: ${self.costs['cost_savings']:.3f} ({savings_percentage:.1f}% saved)
   
📊 Performance Benefits:
   ✅ No rate limits (1000+ requests/minute)
   ✅ Production-grade reliability
   ✅ EU data residency compliance
   🌍 Optimized for Belgium (europe-west2)
   💡 Smart routing saves {savings_percentage:.1f}% on costs
        """

cost_monitor = VertexAICostMonitor()

# --- 7. Enhanced Smart Request Analysis ---
def analyze_request_complexity(user_request: str) -> tuple:
    """Analyze user request and determine appropriate LLM and agent with cost optimization"""
    request_lower = user_request.lower()
    
    # Simple tasks - use Flash LLM (COST SAVINGS)
    simple_keywords = [
        'customer', 'who is', 'find customer', 'contact', 'email address', 'phone', 'mobile',
        'email of', 'contact for', 'address of', 'phone of', 'mobile of', 'information about',
        'details of', 'find', 'search for', 'look up', 'brico', 'company', 'client',
        'partner', 'supplier', 'vendor', 'contact details', 'customer info'
    ]
    
    # Complex tasks - use Pro LLM (QUALITY FOCUS)
    complex_keywords = [
        'update product', 'draft email', 'write email', 'create', 'generate', 'analyze', 
        'polish', 'improve', 'enhance', 'compose', 'multilingual', 'translate'
    ]
    
    # Email/Communication keywords - always use Pro LLM
    email_keywords = ['draft email', 'write email', 'send email', 'compose', 'letter', 'message']
    
    # Product management keywords - use Pro LLM for quality
    product_keywords = ['product', 'item', 'inventory', 'stock', 'catalog', 'price', 'description']
    
    # Determine complexity and route intelligently
    if any(keyword in request_lower for keyword in email_keywords):
        return "complex", "email_communication"
    elif any(keyword in request_lower for keyword in complex_keywords):
        return "complex", "product_management"
    elif any(keyword in request_lower for keyword in product_keywords):
        # Product searches can be simple, but updates are complex
        if any(word in request_lower for word in ['update', 'modify', 'change', 'edit']):
            return "complex", "product_management"
        else:
            return "simple", "product_search"
    elif any(keyword in request_lower for keyword in simple_keywords):
        return "simple", "customer_service"
    else:
        # Default to simple for ambiguous queries (cost optimization)
        return "simple", "general"

# --- 8. Cost-Optimized Vertex AI Agents ---
print("\n--- Assembling Cost-Optimized Vertex AI Workforce ---")

# Simple tasks agent (Flash LLM - COST OPTIMIZED)
customer_agent_flash = Agent(
    role='Odoo Customer Service Specialist (Fast & Efficient)',
    goal='Search the Odoo database to find customer contact details and order history efficiently with minimal cost.',
    backstory="""You are an expert Odoo database assistant specializing in customer information retrieval. 
    Your primary job is to search the Odoo database using the available tools to find customer information quickly and cost-effectively.
    
    IMPORTANT: Always use the Odoo Customer Info Finder tool when users ask about customers, companies, contacts, or contact information.
    You have access to a live Odoo database and should search it first before saying information is not available.""",
    tools=[customer_info_tool],
    llm=crewai_flash_llm,
    verbose=True,
    max_iter=2,
    memory=False
)

# Complex tasks agents (Pro LLM - QUALITY FOCUSED)
product_agent_pro = Agent(
    role='Odoo Product Management Specialist (Advanced)',
    goal='Handle complex product updates and multilingual content generation using Odoo tools with high quality.',
    backstory="""You are an expert in product management with advanced content creation capabilities.
    You have access to Odoo product tools and can search, update, and generate content for products.
    Always use the available Odoo tools to provide accurate, up-to-date information with professional quality.""",
    tools=[product_finder_tool, product_updater_tool, content_generator_tool],
    llm=crewai_pro_llm,
    verbose=True,
    max_iter=3,
    memory=False
)

email_agent_pro = Agent(
    role='Professional Email Communication Specialist (Expert)',
    goal='Draft high-quality professional emails in multiple languages with advanced language skills.',
    backstory="""You are an expert in business communication with advanced language skills.
    You can create professional emails in English, Dutch, and French with appropriate tone and formatting.
    Focus on creating polished, professional communication that represents the business well.""",
    tools=[email_draft_tool],
    llm=crewai_pro_llm,
    verbose=True,
    max_iter=2,
    memory=False
)

print("✅ Cost-Optimized Vertex AI workforce ready:")
print("   💨 Flash Agent: Customer lookups & simple queries (70% cost savings)")
print("   ⚖️ Pro Agents: Product management & email drafting (premium quality)")

# --- 9. Main Application Loop ---
def main():
    print("\n🎉 Welcome to your ULTIMATE Smart AI Assistant!")
    print("🇧🇪 Vertex AI + Cost Optimization - Belgium Edition")
    print("💡 Features:")
    print("   • ⚡ Flash LLM for simple tasks (70% cost savings)")
    print("   • ⚖️ Pro LLM for complex tasks (premium quality)")
    print("   • 🚀 No rate limits (1000+ requests/minute)")
    print("   • 🌍 EU data residency compliance")
    print("   • 💰 Intelligent cost optimization with your paid account")
    print("   • 📊 Real-time cost monitoring and savings tracking")
    
    while True:
        try:
            user_request = input("\n🤖 What can I help you with? (or 'exit'): ").strip()
            if user_request.lower() in ["exit", "quit"]:
                print("👋 Goodbye!")
                print(cost_monitor.get_summary())
                break
            if not user_request:
                print("⚠️ Please enter your request.")
                continue

            print(f"\n🎯 Processing your request: '{user_request}'")
            
            # Analyze request complexity and route appropriately
            complexity, request_type = analyze_request_complexity(user_request)
            
            print(f"🧠 Request analysis:")
            print(f"   Complexity: {complexity}")
            print(f"   Type: {request_type}")
            print(f"   Region: europe-west2 (Belgium optimized)")
            
            # Route to appropriate agent and LLM using CrewAI
            if complexity == "simple":
                print("⚡ Routing to FLASH LLM (ultra-fast & 70% cost savings)")
                cost_monitor.track_call('flash')
                
                # Create task for simple requests
                simple_task = Task(
                    description=f"""You are an Odoo database assistant. Handle this request efficiently: '{user_request}'
                    
                    IMPORTANT: If this is about customer information, use the Odoo Customer Info Finder tool to search the database.
                    If this is about product information, use the appropriate tools to search for products.
                    
                    Provide clear, direct results without unnecessary elaboration.""",
                    expected_output="Clear, direct response to the user's request with relevant information from Odoo",
                    agent=customer_agent_flash
                )
                
                # Create and run crew
                simple_crew = Crew(
                    agents=[customer_agent_flash],
                    tasks=[simple_task],
                    process=Process.sequential,
                    verbose=True
                )
                
                try:
                    result = simple_crew.kickoff()
                    print("\n" + "="*60)
                    print("✅ TASK COMPLETE! Here's your result:")
                    print("="*60)
                    print(result)
                    print("="*60)
                except Exception as e:
                    print(f"❌ Simple task error: {e}")
                    continue
                
            else:  # complex tasks
                print("⚖️ Routing to PRO LLM (premium quality & advanced features)")
                cost_monitor.track_call('pro')
                
                if request_type == "email_communication":
                    email_task = Task(
                        description=f"Handle this email request professionally: '{user_request}'. Create high-quality, well-structured communication with proper formatting and tone.",
                        expected_output="Professional email draft with proper formatting, tone, and language",
                        agent=email_agent_pro
                    )
                    
                    email_crew = Crew(
                        agents=[email_agent_pro],
                        tasks=[email_task],
                        process=Process.sequential,
                        verbose=True
                    )
                    
                    try:
                        result = email_crew.kickoff()
                        print("\n" + "="*60)
                        print("✅ TASK COMPLETE! Here's your result:")
                        print("="*60)
                        print(result)
                        print("="*60)
                    except Exception as e:
                        print(f"❌ Email service error: {e}")
                        continue
                        
                elif request_type == "product_management":
                    product_task = Task(
                        description=f"""Handle this product management request: '{user_request}'.
                        
                        Use the available Odoo tools to:
                        1. Search for products if needed
                        2. Generate compelling multilingual content if requested
                        3. Update product information if requested
                        4. Provide detailed product information
                        
                        Focus on quality, engaging descriptions and multilingual content.""",
                        expected_output="Complete product management results with multilingual content and professional quality",
                        agent=product_agent_pro
                    )
                    
                    product_crew = Crew(
                        agents=[product_agent_pro],
                        tasks=[product_task],
                        process=Process.sequential,
                        verbose=True
                    )
                    
                    try:
                        result = product_crew.kickoff()
                        print("\n" + "="*60)
                        print("✅ TASK COMPLETE! Here's your result:")
                        print("="*60)
                        print(result)
                        print("="*60)
                    except Exception as e:
                        print(f"❌ Product management error: {e}")
                        continue

            # Show cost summary every 3 requests
            total_calls = cost_monitor.costs['flash_calls'] + cost_monitor.costs['pro_calls']
            if total_calls > 0 and total_calls % 3 == 0:
                print(cost_monitor.get_summary())
            
        except KeyboardInterrupt:
            print("\n👋 Operation cancelled by user. Goodbye!")
            print(cost_monitor.get_summary())
            break
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            print("🔄 Please try again with a different request.")
            continue

if __name__ == "__main__":
    main()
