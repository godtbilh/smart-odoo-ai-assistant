# tools/customer_tools.py - Customer Service Tools for Odoo

import xmlrpc.client
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type

class GetCustomerInfoInput(BaseModel):
    customer_name: str = Field(description="The full name of the customer you want to search for.")

class OdooCustomerInfoTool(BaseTool):
    name: str = "Odoo Customer Info Finder"
    description: str = "Finds contact details and order history for a specific customer by their full name."
    args_schema: Type[BaseModel] = GetCustomerInfoInput
    
    def __init__(self, models, db, uid, password):
        super().__init__()
        # Store connection info in a way that doesn't conflict with Pydantic
        object.__setattr__(self, '_models', models)
        object.__setattr__(self, '_db', db)
        object.__setattr__(self, '_uid', uid)
        object.__setattr__(self, '_password', password)
    
    def _run(self, customer_name: str) -> str:
        print(f"\n🔍 TOOL EXECUTING: Searching for customer '{customer_name}'...")
        try:
            search_domain = [('name', '=ilike', customer_name)]
            fields = ['name', 'email', 'phone', 'mobile', 'street', 'city', 'country_id']
            partner_data = self._models.execute_kw(self._db, self._uid, self._password, 
                'res.partner', 'search_read', [search_domain], {'fields': fields, 'limit': 1})
            
            if partner_data:
                customer = partner_data[0]
                print(f"✅ Found customer: {customer['name']}")
                
                try:
                    # Get recent orders
                    order_domain = [('partner_id', '=', customer['id'])]
                    order_fields = ['name', 'date_order', 'state', 'amount_total']
                    order_data = self._models.execute_kw(self._db, self._uid, self._password, 
                        'sale.order', 'search_read', [order_domain], 
                        {'fields': order_fields, 'limit': 5, 'order': 'date_order desc'})
                    
                    # Format customer information
                    result = f"Customer Information:\n"
                    result += f"Name: {customer['name']}\n"
                    result += f"Email: {customer.get('email', 'Not provided')}\n"
                    result += f"Phone: {customer.get('phone', 'Not provided')}\n"
                    result += f"Mobile: {customer.get('mobile', 'Not provided')}\n"
                    result += f"Address: {customer.get('street', 'Not provided')}\n"
                    result += f"City: {customer.get('city', 'Not provided')}\n"
                    
                    if customer.get('country_id'):
                        result += f"Country: {customer['country_id'][1]}\n"
                    
                    if order_data:
                        result += f"\nRecent Orders ({len(order_data)}):\n"
                        for order in order_data:
                            result += f"- Order {order.get('name', 'N/A')} on {order.get('date_order', 'N/A')[:10]} "
                            result += f"(Status: {order.get('state', 'N/A')}, Amount: {order.get('amount_total', 'N/A')})\n"
                    else:
                        result += "\nNo recent orders found.\n"
                    
                    return result
                    
                except Exception as order_error:
                    return f"Customer: {customer['name']}\nEmail: {customer.get('email', 'Not provided')}\nPhone: {customer.get('phone', 'Not provided')}\nNote: Could not retrieve order history due to: {order_error}"
            else:
                return f"No customer found matching '{customer_name}'. Please check the spelling or try a different name."
                
        except Exception as e:
            return f"Error searching for customer: {e}"
