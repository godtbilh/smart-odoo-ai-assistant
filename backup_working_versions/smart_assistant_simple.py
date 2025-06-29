#!/usr/bin/env python3
"""
Simple Smart Assistant - Direct Tool Usage (No CrewAI LLM issues)
"""
import os
from dotenv import load_dotenv
from tools.odoo_connection import OdooConnection
from tools.customer_tools import OdooCustomerInfoTool
from tools.multilingual_product_tools import (
    OdooMultilingualProductFinder, 
    OdooMultilingualProductUpdater,
    MultilingualProductContentGenerator
)

load_dotenv()
print("🎯 Simple Smart Assistant - Direct Odoo Integration")
print("✅ No LLM rate limit issues - Direct tool usage")
print("=" * 60)

# --- Initialize Odoo Connection ---
print("\n🔗 Connecting to Odoo...")
odoo_conn = OdooConnection()
if not odoo_conn.connect():
    print("❌ Failed to connect to Odoo. Exiting...")
    exit()

if not odoo_conn.test_connection():
    print("❌ Odoo connection test failed. Exiting...")
    exit()

# Get connection info for tools
conn_info = odoo_conn.get_connection_info()

# --- Initialize Tools ---
print("🛠️ Initializing tools...")
customer_tool = OdooCustomerInfoTool(
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

print("✅ All tools initialized successfully!")

# --- Request Analysis ---
def analyze_request(user_request: str) -> str:
    """Analyze user request and determine the appropriate action"""
    request_lower = user_request.lower()
    
    # Customer/Contact related keywords
    customer_keywords = [
        'customer', 'who is', 'find customer', 'contact', 'email address', 'phone', 'mobile',
        'email of', 'contact for', 'address of', 'phone of', 'mobile of', 'information about',
        'details of', 'find', 'search for', 'look up', 'brico', 'company', 'client',
        'partner', 'supplier', 'vendor', 'contact details', 'customer info'
    ]
    
    # Product related keywords
    product_keywords = [
        'product', 'item', 'inventory', 'stock', 'catalog', 'price', 'description',
        'update product', 'modify product', 'product info', 'product details'
    ]
    
    # Check for customer/contact queries first
    if any(keyword in request_lower for keyword in customer_keywords):
        return "customer_search"
    elif any(keyword in request_lower for keyword in product_keywords):
        return "product_search"
    else:
        return "customer_search"  # Default to customer search

def extract_search_term(user_request: str) -> str:
    """Extract the search term from user request"""
    original_request = user_request
    request_lower = user_request.lower()
    
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

# --- Main Application ---
def main():
    print("\n🎉 Welcome to your Simple Smart Assistant!")
    print("💡 Features:")
    print("   • 🔍 Customer information lookup")
    print("   • 📦 Product information search")
    print("   • ⚡ Direct tool usage (no LLM rate limits)")
    print("   • 🇧🇪 Optimized for Belgium")
    
    while True:
        try:
            user_request = input("\n🤖 What can I help you with? (or 'exit'): ").strip()
            if user_request.lower() in ["exit", "quit"]:
                print("👋 Goodbye!")
                break
            if not user_request:
                print("⚠️ Please enter your request.")
                continue

            print(f"\n🎯 Processing: '{user_request}'")
            
            # Analyze request type
            request_type = analyze_request(user_request)
            search_term = extract_search_term(user_request)
            
            print(f"🧠 Analysis: {request_type}")
            print(f"🔍 Search term: '{search_term}'")
            
            if request_type == "customer_search":
                print("\n⚡ Searching customer database...")
                try:
                    result = customer_tool._run(search_term)
                    print("\n" + "="*60)
                    print("✅ CUSTOMER INFORMATION FOUND:")
                    print("="*60)
                    print(result)
                    print("="*60)
                except Exception as e:
                    print(f"❌ Customer search error: {e}")
                    
            elif request_type == "product_search":
                print("\n⚡ Searching product database...")
                try:
                    result = product_finder_tool._run(search_term)
                    print("\n" + "="*60)
                    print("✅ PRODUCT INFORMATION FOUND:")
                    print("="*60)
                    print(result)
                    print("="*60)
                except Exception as e:
                    print(f"❌ Product search error: {e}")
            
        except KeyboardInterrupt:
            print("\n👋 Operation cancelled by user. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            print("🔄 Please try again with a different request.")
            continue

if __name__ == "__main__":
    main()
