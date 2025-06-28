# smart_assistant_optimized.py - Cost-Optimized Multi-LLM Smart Assistant

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
print("🚀 Smart Multilingual AI Assistant: Cost-Optimized Multi-LLM")
print("🎯 Capabilities: Customer Service | Product Management | Email Communication")
print("💰 Cost Optimization: Intelligent LLM Selection Based on Task Complexity")
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

# --- 4. Multi-LLM Configuration for Cost Optimization ---
print("\n--- Configuring Multi-LLM Architecture ---")

# Tier 1: Ultra-Fast & Cheap - For simple tasks
flash_llm = LLM(
    model="gemini/gemini-1.5-flash",
    api_key=os.environ["GOOGLE_API_KEY"],
    temperature=0.3
)

# Tier 2: Balanced - For standard business tasks
pro_llm = LLM(
    model="gemini/gemini-1.5-pro",
    api_key=os.environ["GOOGLE_API_KEY"],
    temperature=0.7
)

print("✅ Multi-LLM architecture configured:")
print("   💨 Flash LLM: Simple tasks (customer lookups, basic queries)")
print("   ⚖️ Pro LLM: Complex tasks (content generation, emails, analysis)")

# --- 5. Cost Monitoring ---
class CostMonitor:
    def __init__(self):
        self.costs = {
            'flash_calls': 0,
            'pro_calls': 0,
            'total_estimated_cost': 0.0
        }
        
        # Estimated costs per call (adjust based on actual usage)
        self.pricing = {
            'flash': 0.03,    # Cheap
            'pro': 0.10       # Standard
        }
    
    def track_call(self, llm_type):
        self.costs[f'{llm_type}_calls'] += 1
        cost = self.pricing[llm_type]
        self.costs['total_estimated_cost'] += cost
        print(f"💰 Cost tracking: {llm_type.upper()} LLM call (${cost:.3f})")
        
    def get_summary(self):
        return f"""
💰 Cost Summary:
   Flash LLM calls: {self.costs['flash_calls']} (${self.costs['flash_calls'] * self.pricing['flash']:.3f})
   Pro LLM calls: {self.costs['pro_calls']} (${self.costs['pro_calls'] * self.pricing['pro']:.3f})
   Total estimated: ${self.costs['total_estimated_cost']:.3f}
   
📊 Cost Distribution:
   Flash (cheap): {self.costs['flash_calls']} calls
   Pro (standard): {self.costs['pro_calls']} calls
        """

cost_monitor = CostMonitor()

# --- 6. Smart Request Analysis ---
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

# --- 7. Cost-Optimized Agents ---
print("\n--- Assembling Cost-Optimized AI Workforce ---")

# Simple tasks agent (Flash LLM)
customer_agent_flash = Agent(
    role='Customer Service Specialist (Fast)',
    goal='Find customer contact details and order history efficiently using minimal resources.',
    backstory="You are an expert in quick customer information retrieval, optimized for speed and cost efficiency.",
    tools=[customer_info_tool],
    llm=flash_llm,
    verbose=True,
    max_iter=1,
    memory=False
)

# Complex tasks agents (Pro LLM)
product_agent_pro = Agent(
    role='Product Management Specialist (Advanced)',
    goal='Handle complex product updates and multilingual content generation.',
    backstory="You are an expert in product management with advanced content creation capabilities.",
    tools=[product_finder_tool, product_updater_tool, content_generator_tool],
    llm=pro_llm,
    verbose=True,
    max_iter=2,
    memory=False
)

email_agent_pro = Agent(
    role='Email Communication Specialist (Professional)',
    goal='Draft high-quality professional emails in multiple languages.',
    backstory="You are an expert in business communication with advanced language skills.",
    tools=[email_draft_tool],
    llm=pro_llm,
    verbose=True,
    max_iter=1,
    memory=False
)

print("✅ Cost-optimized AI workforce ready:")
print("   💨 Flash Agent: Customer lookups (ultra-fast & cheap)")
print("   ⚖️ Pro Agents: Product management & email drafting (quality & balanced cost)")

# --- 8. Main Application Loop ---
def main():
    print("\n🎉 Welcome to your Cost-Optimized Smart AI Assistant!")
    print("💡 Features:")
    print("   • ⚡ Flash LLM for simple customer lookups (70% cost savings)")
    print("   • ⚖️ Pro LLM for complex tasks (balanced quality & cost)")
    print("   • 💰 Automatic cost optimization and tracking")
    print("   • 📊 Real-time cost monitoring")
    
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
            
            # Route to appropriate agent and LLM
            if complexity == "simple":
                print("⚡ Routing to FLASH LLM (ultra-fast & cheap)")
                cost_monitor.track_call('flash')
                
                main_task = Task(
                    description=f"Handle this simple request efficiently: '{user_request}'. Provide clear, direct results.",
                    expected_output="Clear, direct response to the user's request",
                    agent=customer_agent_flash
                )
                agents_list = [customer_agent_flash]
                tasks_list = [main_task]
                max_rpm = 10  # Higher rate for simple tasks
                
            else:  # complex
                print("⚖️ Routing to PRO LLM (balanced quality & cost)")
                cost_monitor.track_call('pro')
                
                if request_type == "email_communication":
                    main_task = Task(
                        description=f"Handle this email request professionally: '{user_request}'. Create high-quality, well-structured communication.",
                        expected_output="Professional email draft with proper formatting and tone",
                        agent=email_agent_pro
                    )
                    agents_list = [email_agent_pro]
                    
                elif request_type == "product_management":
                    main_task = Task(
                        description=f"""Handle this product management request: '{user_request}'.
                        
                        Process:
                        1. Search for the product if needed
                        2. Generate compelling multilingual content if requested
                        3. Update product information if requested
                        4. Verify success
                        
                        Focus on quality, engaging descriptions.""",
                        expected_output="Complete product management results with multilingual content",
                        agent=product_agent_pro
                    )
                    agents_list = [product_agent_pro]
                
                tasks_list = [main_task]
                max_rpm = 5  # Standard rate for complex tasks

            # Add delay to prevent rate limiting
            delay = random.uniform(3, 6)
            print(f"⏳ Processing... ({delay:.1f}s)")
            time.sleep(delay)

            # Assemble and run the crew
            smart_crew = Crew(
                agents=agents_list,
                tasks=tasks_list,
                process=Process.sequential,
                verbose=True,
                max_rpm=max_rpm
            )
            
            print("\n🚀 AI team is working on your request...")
            print("-" * 50)
            
            result = smart_crew.kickoff()
            
            print("\n" + "="*60)
            print("✅ TASK COMPLETE! Here's your result:")
            print("="*60)
            print(result)
            print("="*60)
            
            # Show cost summary every 3 requests
            total_calls = cost_monitor.costs['flash_calls'] + cost_monitor.costs['pro_calls']
            if total_calls > 0 and total_calls % 3 == 0:
                print(cost_monitor.get_summary())
            
        except KeyboardInterrupt:
            print("\n👋 Operation cancelled by user. Goodbye!")
            print(cost_monitor.get_summary())
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
