#!/usr/bin/env python3
"""
Smart Assistant using Vertex AI - Fixed Version with Fallback
Combines AI capabilities with reliable tool usage
"""
import os
import json
import time
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
print("🇧🇪 Smart AI Assistant: Vertex AI (Fixed) - Belgium Edition")
print("🌍 Region: europe-west2 (London) - Optimized for Belgium")
print("🎯 Capabilities: AI + Direct Tools (Hybrid Approach)")
print("💰 Cost: Optimized with fallback to direct tools")
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
        print("💡 Will use direct tools only")
        return None

project_id = initialize_vertex_ai()

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

# --- 4. Vertex AI LLM Configuration ---
if project_id:
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
    
    # Initialize models
    flash_llm = VertexAILLM("gemini-1.5-flash", temperature=0.3)
    pro_llm = VertexAILLM("gemini-1.5-pro", temperature=0.7)
    
    print("✅ Vertex AI LLMs configured:")
    print("   💨 Flash LLM: gemini-1.5-flash (fast & cost-effective)")
    print("   ⚖️ Pro LLM: gemini-1.5-pro (advanced reasoning)")

# --- 5. Request Analysis Functions ---
def analyze_request_complexity(user_request: str) -> tuple:
    """Analyze user request and determine appropriate LLM and agent"""
    request_lower = user_request.lower()
    
    # Customer/Contact related keywords - use Flash LLM with Odoo tools
    customer_keywords = [
        'customer', 'who is', 'find customer', 'contact', 'email address', 'phone', 'mobile',
        'email of', 'contact for', 'address of', 'phone of', 'mobile of', 'information about',
        'details of', 'find', 'search for', 'look up', 'brico', 'company', 'client',
        'partner', 'supplier', 'vendor', 'contact details', 'customer info'
    ]
    
    # Product related keywords - use Pro LLM with Odoo tools  
    product_keywords = [
        'product', 'item', 'inventory', 'stock', 'catalog', 'price', 'description',
        'update product', 'modify product', 'product info', 'product details'
    ]
    
    # Email/Communication keywords - use Pro LLM
    email_keywords = ['draft email', 'write email', 'send email', 'compose', 'letter', 'message']
    
    # Complex content generation - use Pro LLM
    complex_keywords = ['create', 'generate', 'analyze', 'polish', 'improve', 'enhance']
    
    # Check for customer/contact queries first (most common)
    if any(keyword in request_lower for keyword in customer_keywords):
        return "simple", "customer_service"
    elif any(keyword in request_lower for keyword in product_keywords):
        return "complex", "product_management"
    elif any(keyword in request_lower for keyword in email_keywords):
        return "complex", "email_communication"
    elif any(keyword in request_lower for keyword in complex_keywords):
        return "complex", "content_generation"
    else:
        # Default to customer service for ambiguous queries
        return "simple", "customer_service"

def extract_search_term(user_request: str) -> str:
    """Extract the search term from user request"""
    original_request = user_request
    
    # Common patterns to remove (in order of specificity)
    patterns_to_remove = [
        'give me information about the customer ',
        'give me information about customer ',
        'give me information about the ',
        'give me information about ',
        'find customer ',
        'search for customer ',
        'search for ',
        'look up customer ',
        'look up ',
        'email of the ',
        'email of ',
        'contact for the ',
        'contact for ',
        'phone of the ',
        'phone of ',
        'address of the ',
        'address of ',
        'details of the ',
        'details of ',
        'information about the ',
        'information about ',
        'who is the ',
        'who is ',
        'what is the email of the ',
        'what is the email of ',
        'what is the phone of the ',
        'what is the phone of ',
        'customer ',
        'the '
    ]
    
    search_term = original_request
    for pattern in patterns_to_remove:
        # Case-insensitive replacement
        if pattern.lower() in search_term.lower():
            # Find the position and replace
            start_pos = search_term.lower().find(pattern.lower())
            if start_pos != -1:
                search_term = search_term[:start_pos] + search_term[start_pos + len(pattern):]
                break  # Only remove the first match
    
    return search_term.strip()

# --- 6. Direct Tool Usage Functions ---
def use_customer_tool_directly(search_term: str) -> str:
    """Use customer tool directly without CrewAI"""
    try:
        print(f"🔍 Direct search for customer: '{search_term}'")
        result = customer_info_tool._run(search_term)
        return result
    except Exception as e:
        return f"❌ Error searching for customer: {e}"

def use_product_tool_directly(search_term: str) -> str:
    """Use product tool directly without CrewAI"""
    try:
        print(f"🔍 Direct search for product: '{search_term}'")
        result = product_finder_tool._run(search_term)
        return result
    except Exception as e:
        return f"❌ Error searching for product: {e}"

def generate_ai_response(user_request: str, tool_result: str, complexity: str) -> str:
    """Generate AI-enhanced response using Vertex AI directly"""
    if not project_id:
        return tool_result  # Return raw tool result if no AI available
    
    try:
        if complexity == "simple":
            llm = flash_llm
            prompt = f"""You are a helpful customer service assistant. 
            
User asked: "{user_request}"
Tool result: "{tool_result}"

Please provide a friendly, professional response based on the tool result. 
If customer information was found, present it clearly. 
If not found, explain politely that the customer is not in the database.
Keep the response concise and helpful."""
        else:
            llm = pro_llm
            prompt = f"""You are an expert business assistant with advanced capabilities.
            
User asked: "{user_request}"
Tool result: "{tool_result}"

Please provide a comprehensive, professional response based on the tool result.
Add insights, suggestions, or additional context where appropriate.
Format the response clearly and professionally."""
        
        ai_response = llm.generate(prompt)
        return ai_response
        
    except Exception as e:
        print(f"⚠️ AI enhancement failed: {e}")
        return tool_result  # Fallback to raw tool result

# --- 7. Main Application Loop ---
def main():
    print("\n🎉 Welcome to your Smart AI Assistant (Fixed Version)!")
    print("🇧🇪 Optimized for Belgium with hybrid approach")
    print("💡 Features:")
    print("   • 🔍 Customer & Product search")
    print("   • 🤖 AI-enhanced responses (when available)")
    print("   • ⚡ Direct tool fallback (always works)")
    print("   • 🌍 EU data residency compliance")
    
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
            
            # Analyze request complexity and route appropriately
            complexity, request_type = analyze_request_complexity(user_request)
            search_term = extract_search_term(user_request)
            
            print(f"🧠 Request analysis:")
            print(f"   Complexity: {complexity}")
            print(f"   Type: {request_type}")
            print(f"   Search term: '{search_term}'")
            
            # Use direct tools (always reliable)
            if request_type == "customer_service":
                print("⚡ Using customer service tools...")
                tool_result = use_customer_tool_directly(search_term)
                
                # Try to enhance with AI
                if project_id:
                    print("🤖 Enhancing response with AI...")
                    final_result = generate_ai_response(user_request, tool_result, complexity)
                else:
                    final_result = tool_result
                    
            elif request_type == "product_management":
                print("⚡ Using product management tools...")
                tool_result = use_product_tool_directly(search_term)
                
                # Try to enhance with AI
                if project_id:
                    print("🤖 Enhancing response with AI...")
                    final_result = generate_ai_response(user_request, tool_result, complexity)
                else:
                    final_result = tool_result
                    
            elif request_type == "email_communication":
                if project_id:
                    print("✉️ Generating email with AI...")
                    prompt = f"Create a professional email based on this request: {user_request}"
                    final_result = pro_llm.generate(prompt)
                else:
                    final_result = "Email generation requires AI capabilities. Please use a more specific request for customer or product information."
                    
            else:  # content_generation or other
                if project_id:
                    print("🎨 Generating content with AI...")
                    prompt = f"Handle this request professionally: {user_request}"
                    final_result = pro_llm.generate(prompt)
                else:
                    # Try customer search as fallback
                    tool_result = use_customer_tool_directly(search_term)
                    final_result = tool_result
            
            # Display results
            print("\n" + "="*60)
            print("✅ RESULT:")
            print("="*60)
            print(final_result)
            print("="*60)
            
        except KeyboardInterrupt:
            print("\n👋 Operation cancelled by user. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            print("🔄 Please try again with a different request.")
            continue

if __name__ == "__main__":
    main()
