#!/usr/bin/env python3
"""
Test Odoo connection and customer search functionality
"""
import os
from dotenv import load_dotenv
from tools.odoo_connection import OdooConnection
from tools.customer_tools import OdooCustomerInfoTool

def test_odoo_connection():
    print("🧪 Testing Odoo Connection and Customer Search")
    print("=" * 50)
    
    load_dotenv()
    
    # Test 1: Basic connection
    print("\n1️⃣ Testing Odoo Connection...")
    odoo_conn = OdooConnection()
    
    if not odoo_conn.connect():
        print("❌ Failed to connect to Odoo")
        return False
    
    if not odoo_conn.test_connection():
        print("❌ Odoo connection test failed")
        return False
    
    print("✅ Odoo connection successful!")
    
    # Test 2: Customer tool initialization
    print("\n2️⃣ Testing Customer Tool...")
    conn_info = odoo_conn.get_connection_info()
    
    customer_tool = OdooCustomerInfoTool(
        models=conn_info['models'],
        db=conn_info['db'],
        uid=conn_info['uid'],
        password=conn_info['password']
    )
    print("✅ Customer tool initialized!")
    
    # Test 3: Search for a customer
    print("\n3️⃣ Testing Customer Search...")
    test_searches = [
        "Brico Boncelles",
        "Test Customer",
        "Administrator"
    ]
    
    for search_term in test_searches:
        print(f"\n🔍 Searching for: '{search_term}'")
        try:
            result = customer_tool._run(search_term)
            print(f"📋 Result:")
            print(result)
            print("-" * 30)
        except Exception as e:
            print(f"❌ Error searching for '{search_term}': {e}")
    
    print("\n✅ Odoo connection test completed!")
    return True

if __name__ == "__main__":
    test_odoo_connection()
