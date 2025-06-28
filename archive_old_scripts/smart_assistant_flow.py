# smart_assistant_flow.py - Cost-Optimized CrewAI Flow Implementation

import os
import time
import random
import re
from dotenv import load_dotenv

# --- CrewAI Flow Imports ---
from crewai import Agent, Task, Crew, Process, LLM
from crewai.flow import Flow, listen, start, router, or_
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
print("🚀 Smart Multilingual AI Assistant: Flow-Optimized for Cost Efficiency")
print("🎯 Capabilities: Customer Service | Product Management | Email Communication")
print("💰 Cost Optimization: Multi-LLM Architecture with CrewAI Flow")
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

# Tier 1: Ultra-Fast & Cheap - For simple classification and routing
flash_llm = LLM(
    model="gemini/gemini-1.5-flash",
    api_key=os.environ["GOOGLE_API_KEY"],
    temperature=0.3  # Lower temperature for consistent routing
)

# Tier 2: Balanced - For standard business tasks
pro_llm = LLM(
    model="gemini/gemini-1.5-pro",
    api_key=os.environ["GOOGLE_API_KEY"],
    temperature=0.7
)

# Tier 3: Premium - For complex analysis (when needed)
# Note: Add GPT-4 or Claude if you have access for complex tasks
premium_llm = pro_llm  # Using Pro as premium for now

print("✅ Multi-LLM architecture configured:")
print("   💨 Flash LLM: Classification, routing, simple tasks")
print("   ⚖️ Pro LLM: Standard business operations")
print("   🧠 Premium LLM: Complex analysis and reasoning")

# --- 5. Cost-Optimized Agents ---
print("\n--- Assembling Cost-Optimized AI Workforce ---")

# Lightweight classifier agent (uses cheapest LLM)
classifier_agent = Agent(
    role='Request Classifier',
    goal='Quickly classify user requests to route to appropriate specialized agents.',
    backstory="You are a fast, efficient classifier that determines request types without complex reasoning.",
    tools=[],
    llm=flash_llm,  # Cheapest LLM for classification
    verbose=False,
    max_iter=1,
    memory=False
)

# Customer service agent (optimized for simple lookups)
customer_agent = Agent(
    role='Customer Service Specialist',
    goal='Find customer contact details and order history efficiently.',
    backstory="You are an expert in querying customer information quickly and accurately.",
    tools=[customer_info_tool],
    llm=flash_llm,  # Simple lookups don't need expensive LLM
    verbose=True,
    max_iter=1,
    memory=False
)

# Product specialist (uses balanced LLM for content generation)
product_agent = Agent(
    role='Product Management Specialist',
    goal='Handle product updates and content generation in multiple languages.',
    backstory="You are an expert in product management with multilingual content creation skills.",
    tools=[product_finder_tool, product_updater_tool, content_generator_tool],
    llm=pro_llm,  # Balanced LLM for content generation
    verbose=True,
    max_iter=2,
    memory=False
)

# Email specialist (uses balanced LLM for professional communication)
email_agent = Agent(
    role='Email Communication Specialist',
    goal='Draft professional emails in multiple languages.',
    backstory="You are an expert in business communication across languages.",
    tools=[email_draft_tool],
    llm=pro_llm,  # Balanced LLM for quality communication
    verbose=True,
    max_iter=1,
    memory=False
)

# Analysis agent (uses premium LLM only when needed)
analysis_agent = Agent(
    role='Business Intelligence Analyst',
    goal='Provide complex business insights and strategic analysis.',
    backstory="You are a senior analyst capable of deep business reasoning and complex problem solving.",
    tools=[customer_info_tool, product_finder_tool],
    llm=premium_llm,  # Premium LLM for complex analysis
    verbose=True,
    max_iter=3,
    memory=False
)

print("✅ Cost-optimized AI workforce ready.")

# --- 6. CrewAI Flow Implementation ---
class SmartOdooFlow(Flow):
    """
    Cost-optimized CrewAI Flow for Odoo integration
    Uses different LLMs based on task complexity for maximum cost efficiency
    """
    
    @start()
    def classify_request(self):
        """Step 1: Classify request using cheapest LLM"""
        print(f"\n🎯 Flow Step 1: Classifying request with Flash LLM")
        print(f"📝 Request: '{self.state.user_request}'")
        
        # Use lightweight classifier
        classification_task = Task(
            description=f"""Classify this user request into ONE category: '{self.state.user_request}'
            
            Categories:
            - customer_lookup: Finding customer information, contact details, order history
            - product_simple: Basic product searches or simple updates
            - product_complex: Complex product updates, content generation, multilingual tasks
            - email_simple: Basic email drafts, simple communication
            - email_complex: Complex emails, formal business communication
            - analysis: Business analysis, insights, complex reasoning
            - general: Other requests
            
            Respond with ONLY the category name.""",
            expected_output="Single category name from the list above",
            agent=classifier_agent
        )
        
        crew = Crew(
            agents=[classifier_agent],
            tasks=[classification_task],
            process=Process.sequential,
            verbose=False
        )
        
        result = crew.kickoff()
        self.state.request_type = str(result).strip().lower()
        print(f"🧠 Classification result: {self.state.request_type}")
        
        return self.state.request_type

    @listen(classify_request)
    def route_simple_tasks(self):
        """Route simple tasks to fast, cheap processing"""
        if self.state.request_type in ["customer_lookup", "product_simple", "general"]:
            print(f"⚡ Routing to FAST track (Flash LLM)")
            return self.process_simple_task()
    
    @listen(classify_request)
    def route_standard_tasks(self):
        """Route standard tasks to balanced processing"""
        if self.state.request_type in ["email_simple", "email_complex"]:
            print(f"⚖️ Routing to STANDARD track (Pro LLM)")
            return self.process_email_task()
    
    @listen(classify_request)
    def route_complex_tasks(self):
        """Route complex tasks to appropriate processing"""
        if self.state.request_type == "product_complex":
            print(f"🛠️ Routing to PRODUCT track (Pro LLM)")
            return self.process_product_task()
    
    @listen(classify_request)
    def route_analysis_tasks(self):
        """Route analysis tasks to premium processing"""
        if self.state.request_type == "analysis":
            print(f"🧠 Routing to ANALYSIS track (Premium LLM)")
            return self.process_analysis_task()

    def process_simple_task(self):
        """Process simple tasks with Flash LLM (cheapest)"""
        print("💨 Processing with Flash LLM - Ultra-fast & cost-efficient")
        
        task = Task(
            description=f"Handle this simple request efficiently: '{self.state.user_request}'. Provide clear, direct results.",
            expected_output="Clear, direct response to the user's request",
            agent=customer_agent
        )
        
        crew = Crew(
            agents=[customer_agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True,
            max_rpm=10  # Higher rate for simple tasks
        )
        
        result = crew.kickoff()
        self.state.final_result = result
        return result

    def process_email_task(self):
        """Process email tasks with Pro LLM (balanced cost/quality)"""
        print("✉️ Processing with Pro LLM - Balanced quality & cost")
        
        task = Task(
            description=f"Handle this email request: '{self.state.user_request}'. Create professional, well-structured communication.",
            expected_output="Professional email draft with proper formatting and tone",
            agent=email_agent
        )
        
        crew = Crew(
            agents=[email_agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True,
            max_rpm=5
        )
        
        result = crew.kickoff()
        self.state.final_result = result
        return result

    def process_product_task(self):
        """Process product tasks with Pro LLM (content generation)"""
        print("🛠️ Processing with Pro LLM - Quality content generation")
        
        task = Task(
            description=f"""Handle this product management request: '{self.state.user_request}'.
            
            Process:
            1. Search for the product
            2. Generate compelling multilingual content if needed
            3. Update product information
            4. Verify success
            
            Focus on quality, engaging descriptions.""",
            expected_output="Complete product management results with multilingual content",
            agent=product_agent
        )
        
        crew = Crew(
            agents=[product_agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True,
            max_rpm=3  # Lower rate for complex tasks
        )
        
        result = crew.kickoff()
        self.state.final_result = result
        return result

    def process_analysis_task(self):
        """Process analysis tasks with Premium LLM (complex reasoning)"""
        print("🧠 Processing with Premium LLM - Advanced analysis")
        
        task = Task(
            description=f"Provide comprehensive business analysis for: '{self.state.user_request}'. Use advanced reasoning and provide strategic insights.",
            expected_output="Detailed business analysis with insights and recommendations",
            agent=analysis_agent
        )
        
        crew = Crew(
            agents=[analysis_agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True,
            max_rpm=2  # Lowest rate for premium tasks
        )
        
        result = crew.kickoff()
        self.state.final_result = result
        return result

# --- 7. Cost Monitoring ---
class CostMonitor:
    def __init__(self):
        self.costs = {
            'flash_calls': 0,
            'pro_calls': 0,
            'premium_calls': 0,
            'total_estimated_cost': 0.0
        }
        
        # Estimated costs per 1K tokens (adjust based on actual pricing)
        self.pricing = {
            'flash': 0.0001,  # Very cheap
            'pro': 0.001,     # Medium
            'premium': 0.01   # Expensive
        }
    
    def track_call(self, llm_type, estimated_tokens=1000):
        self.costs[f'{llm_type}_calls'] += 1
        cost = (estimated_tokens / 1000) * self.pricing[llm_type]
        self.costs['total_estimated_cost'] += cost
        
    def get_summary(self):
        return f"""
💰 Cost Summary:
   Flash LLM calls: {self.costs['flash_calls']} (${self.costs['flash_calls'] * 0.0001:.4f})
   Pro LLM calls: {self.costs['pro_calls']} (${self.costs['pro_calls'] * 0.001:.4f})
   Premium LLM calls: {self.costs['premium_calls']} (${self.costs['premium_calls'] * 0.01:.4f})
   Total estimated: ${self.costs['total_estimated_cost']:.4f}
        """

cost_monitor = CostMonitor()

# --- 8. Main Application ---
def main():
    print("\n🎉 Welcome to your Cost-Optimized Smart AI Assistant!")
    print("💡 Features:")
    print("   • ⚡ Fast customer lookups (Flash LLM)")
    print("   • ⚖️ Quality email drafting (Pro LLM)")
    print("   • 🛠️ Advanced product management (Pro LLM)")
    print("   • 🧠 Business analysis (Premium LLM)")
    print("   • 💰 Automatic cost optimization")
    
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

            print(f"\n🎯 Processing your request with cost optimization...")
            
            # Initialize flow
            flow = SmartOdooFlow()
            
            # Run the flow with user request
            print("\n🚀 Starting cost-optimized flow...")
            print("-" * 50)
            
            result = flow.kickoff(inputs={"user_request": user_request})
            
            print("\n" + "="*60)
            print("✅ TASK COMPLETE! Here's your result:")
            print("="*60)
            print(result)
            print("="*60)
            
            # Show cost summary periodically
            if cost_monitor.costs['flash_calls'] + cost_monitor.costs['pro_calls'] + cost_monitor.costs['premium_calls'] > 0:
                if (cost_monitor.costs['flash_calls'] + cost_monitor.costs['pro_calls'] + cost_monitor.costs['premium_calls']) % 5 == 0:
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
