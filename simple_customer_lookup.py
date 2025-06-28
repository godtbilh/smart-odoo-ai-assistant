# simple_customer_lookup.py - Direct Customer Lookup (No AI Agents, No Rate Limits)

import os
from dotenv import load_dotenv
from tools.odoo_connection import OdooConnection
from tools.customer_tools import OdooCustomerInfoTool

load_dotenv()

def main():
    print("🔍 Simple Customer Lookup Tool (No Rate Limits)")
    print("=" * 50)
    
    # Connect to Odoo
    odoo_conn = OdooConnection()
    if not odoo_conn.connect():
        print("❌ Failed to connect to Odoo. Exiting...")
        return
    
    if not odoo_conn.test_connection():
        print("❌ Odoo connection test failed. Exiting...")
        return
    
    # Get connection info
    conn_info = odoo_conn.get_connection_info()
    
    # Initialize customer tool
    customer_tool = OdooCustomerInfoTool(
        models=conn_info['models'],
        db=conn_info['db'],
        uid=conn_info['uid'],
        password=conn_info['password']
    )
    
    print("✅ Connected to Odoo successfully!")
    print("\n💡 This tool directly searches Odoo without AI agents (no rate limits)")
    
    while True:
        try:
            customer_name = input("\n🔍 Enter customer name to search (or 'exit'): ").strip()
            
            if customer_name.lower() in ['exit', 'quit']:
                print("👋 Goodbye!")
                break
                
            if not customer_name:
                print("⚠️ Please enter a customer name.")
                continue
            
            print(f"\n🔍 Searching for customer: {customer_name}")
            print("-" * 40)
            
            # Direct tool call - no AI agents involved
            result = customer_tool._run(customer_name)
            
            print("📋 RESULT:")
            print(result)
            print("-" * 40)
            
        except KeyboardInterrupt:
            print("\n👋 Operation cancelled by user. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            continue

if __name__ == "__main__":
    main()
