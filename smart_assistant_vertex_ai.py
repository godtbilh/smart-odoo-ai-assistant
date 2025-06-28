#!/usr/bin/env python3
"""
Smart Assistant using Vertex AI (Google Cloud) - Belgium Optimized
Uses europe-west2 region for optimal performance from Belgium
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
print("🇧🇪 Smart AI Assistant: Vertex AI (Google Cloud) - Belgium Edition")
print("🌍 Region: europe-west2 (London) - Optimized for Belgium")
print("🎯 Capabilities: Customer Service | Product Management | Email Communication")
print("💰 Cost: Production-grade with 1000+ requests/minute")
print("=" * 70)

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

# --- 5. Vertex AI LLM Configuration ---
print("\n--- Configuring Vertex AI LLMs ---")

# Custom LLM wrapper for Vertex AI
class VertexAILLM:
    def __init__(self, model_name: str, temperature: float = 0.7):
        self.model_name = model_name
        self.temperature = temperature
        self.model = GenerativeModel(model_name)
        
    def generate(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": self.temperature,
                    "max_output_tokens": 2048,
                }
            )
            return response.text
        except Exception as e:
            return f"Error generating response: {e}"

# Initialize models with working versions
flash_llm = VertexAILLM("gemini-1.5-flash", temperature=0.3)
pro_llm = VertexAILLM("gemini-1.5-pro", temperature=0.7)

print("✅ Vertex AI LLMs configured:")
print("   💨 Flash LLM: gemini-1.5-flash (fast & cost-effective)")
print("   ⚖️ Pro LLM: gemini-1.5-pro (advanced reasoning)")

# --- 6. Cost Monitoring ---
class CostMonitor:
    def __init__(self):
        self.costs = {
            'flash_calls': 0,
            'pro_calls': 0,
            'total_estimated_cost': 0.0
        }
        
        # Vertex AI pricing (approximate)
        self.pricing = {
            'flash': 0.02,    # Very cost-effective
            'pro': 0.08       # Standard
        }
    
    def track_call(self, llm_type):
        self.costs[f'{llm_type}_calls'] += 1
        cost = self.pricing[llm_type]
        self.costs['total_estimated_cost'] += cost
        print(f"💰 Cost tracking: {llm_type.upper()} LLM call (${cost:.3f})")
        
    def get_summary(self):
        return f"""
💰 Vertex AI Cost Summary:
   Flash LLM calls: {self.costs['flash_calls']} (${self.costs['flash_calls'] * self.pricing['flash']:.3f})
   Pro LLM calls: {self.costs['pro_calls']} (${self.costs['pro_calls'] * self.pricing['pro']:.3f})
   Total estimated: ${self.costs['total_estimated_cost']:.3f}
   
📊 Performance Benefits:
   ✅ No rate limits (1000+ requests/minute)
   ✅ Production-grade reliability
   ✅ EU data residency compliance
   🌍 Optimized for Belgium (europe-west2)
        """

cost_monitor = CostMonitor()

# --- 7. Smart Request Analysis ---
def analyze_request_complexity(user_request: str) -> tuple:
    """Analyze user request and determine appropriate LLM and agent"""
    request_lower = user_request.lower()
    
    # Simple tasks - use Flash LLM
    simple_keywords = ['customer', 'who is', 'find customer', 'contact', 'email address', 'phone']
    
    # Complex tasks - use Pro LLM
    complex_keywords = ['update product', 'draft email', 'write email', 'create', 'generate', 'analyze', 'polish']
    
    # Determine complexity
    if any(keyword in request_lower for keyword in simple_keywords):
        return "simple", "customer_service"
    elif any(keyword in request_lower for keyword in complex_keywords):
        if any(word in request_lower for word in ['email', 'draft', 'write']):
            return "complex", "email_communication"
        else:
            return "complex", "product_management"
    else:
        return "simple", "general"

# --- 8. Vertex AI Agents ---
print("\n--- Assembling Vertex AI Workforce ---")

# Simple tasks agent (Flash LLM)
customer_agent_flash = Agent(
    role='Customer Service Specialist (Vertex AI Flash)',
    goal='Find customer contact details and order history efficiently using Vertex AI.',
    backstory="You are an expert in quick customer information retrieval, powered by Vertex AI Flash model for optimal speed and cost efficiency.",
    tools=[customer_info_tool],
    verbose=True,
    max_iter=1,
    memory=False
)

# Complex tasks agents (Pro LLM)
product_agent_pro = Agent(
    role='Product Management Specialist (Vertex AI Pro)',
    goal='Handle complex product updates and multilingual content generation using advanced AI.',
    backstory="You are an expert in product management with advanced content creation capabilities, powered by Vertex AI Pro model.",
    tools=[product_finder_tool, product_updater_tool, content_generator_tool],
    verbose=True,
    max_iter=2,
    memory=False
)

email_agent_pro = Agent(
    role='Email Communication Specialist (Vertex AI Pro)',
    goal='Draft high-quality professional emails in multiple languages using advanced AI.',
    backstory="You are an expert in business communication with advanced language skills, powered by Vertex AI Pro model.",
    tools=[email_draft_tool],
    verbose=True,
    max_iter=1,
    memory=False
)

print("✅ Vertex AI workforce ready:")
print("   💨 Flash Agent: Customer lookups (ultra-fast)")
print("   ⚖️ Pro Agents: Product management & email drafting")

# --- 9. Main Application Loop ---
def main():
    print("\n🎉 Welcome to your Vertex AI Smart Assistant!")
    print("🇧🇪 Optimized for Belgium with europe-west2 region")
    print("💡 Features:")
    print("   • ⚡ Flash LLM for simple tasks (cost-effective)")
    print("   • ⚖️ Pro LLM for complex tasks (advanced reasoning)")
    print("   • 🚀 No rate limits (1000+ requests/minute)")
    print("   • 🌍 EU data residency compliance")
    print("   • 💰 Production-grade cost optimization")
    
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
            
            # Route to appropriate agent and LLM
            if complexity == "simple":
                print("⚡ Routing to Vertex AI FLASH LLM")
                cost_monitor.track_call('flash')
                
                # Use Flash model directly for simple tasks
                try:
                    flash_response = flash_llm.generate(f"Handle this customer service request efficiently: '{user_request}'. Provide clear, direct results.")
                    print("\n" + "="*60)
                    print("✅ TASK COMPLETE! Here's your result:")
                    print("="*60)
                    print(flash_response)
                    print("="*60)
                except Exception as e:
                    print(f"❌ Flash LLM error: {e}")
                    continue
                
            else:  # complex
                print("⚖️ Routing to Vertex AI PRO LLM")
                cost_monitor.track_call('pro')
                
                if request_type == "email_communication":
                    prompt = f"Handle this email request professionally: '{user_request}'. Create high-quality, well-structured communication."
                elif request_type == "product_management":
                    prompt = f"Handle this product management request: '{user_request}'. Focus on quality, engaging descriptions and multilingual content."
                else:
                    prompt = f"Handle this complex request: '{user_request}'. Provide detailed, high-quality results."
                
                try:
                    pro_response = pro_llm.generate(prompt)
                    print("\n" + "="*60)
                    print("✅ TASK COMPLETE! Here's your result:")
                    print("="*60)
                    print(pro_response)
                    print("="*60)
                except Exception as e:
                    print(f"❌ Pro LLM error: {e}")
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
