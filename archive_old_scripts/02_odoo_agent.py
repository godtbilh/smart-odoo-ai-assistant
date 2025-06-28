# 02_odoo_agent.py (Version 2 - with two tools)

import xmlrpc.client
import os
from dotenv import load_dotenv

# --- LangChain Imports ---
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# --- Load .env file for Odoo credentials ---
load_dotenv()

# --- 1. Odoo Connection Logic ---
try:
    url = os.environ["ODOO_URL"]
    db = os.environ["ODOO_DB"]
    username = os.environ["ODOO_USERNAME"]
    password = os.environ["ODOO_PASSWORD"]

    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    print("✅ Successfully connected and authenticated with Odoo.")
except Exception as e:
    print(f"❌ Failed to connect to Odoo. Check your .env file and connection. Error: {e}")
    exit()

# --- 2. Define the Custom Tools ---

@tool
def get_customer_email(customer_name: str) -> str:
    """
    Use this tool to find the email address for a specific customer by providing their full name.
    It will search the Odoo database for a contact with that name.
    """
    print(f"\nTOOL CALLED: get_customer_email(customer_name='{customer_name}')")
    try:
        search_domain = [('name', '=ilike', customer_name)]
        fields_to_read = ['name', 'email']
        partner_data = models.execute_kw(db, uid, password, 'res.partner', 'search_read',
            [search_domain], {'fields': fields_to_read, 'limit': 1})
        if partner_data and partner_data[0].get('email'):
            return f"Found data: {partner_data[0]}"
        else:
            return f"Could not find a customer named '{customer_name}' or they do not have an email."
    except Exception as e:
        return f"An error occurred in the tool: {e}"

# --- THIS IS OUR NEW TOOL ---
@tool
def create_new_contact(name: str, email: str = None, phone: str = None) -> str:
    """
    Use this tool to create a brand new contact or company in the Odoo database.
    You must provide at least a name. Email and phone are optional.
    """
    print(f"\nTOOL CALLED: create_new_contact(name='{name}', email='{email}', phone='{phone}')")
    try:
        # Build the dictionary of data to send to Odoo
        new_contact_data = {'name': name}
        if email:
            new_contact_data['email'] = email
        if phone:
            new_contact_data['phone'] = phone

        # Call the 'create' method
        new_id = models.execute_kw(db, uid, password, 'res.partner', 'create', [new_contact_data])
        
        return f"Successfully created new contact '{name}' with database ID: {new_id}."
    except Exception as e:
        return f"An error occurred while creating the contact: {e}"

# --- 3. Create the Agent ---

# --- UPDATE THE TOOLBOX ---
# Now our agent has two tools it can choose from!
tools = [get_customer_email, create_new_contact]

# The rest of the setup is the same
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest")
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant that can access an Odoo database to find customer information and create new contacts."),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

print("\n🤖 Odoo Agent is ready. I can now find customer emails OR create new contacts.")
print("-" * 30)

# --- 4. Run the Agent with a new type of task ---
if __name__ == "__main__":
    # Let's give it a task that requires the NEW tool
    question = "We have a new lead. Please create a contact for 'Innovate Corp' with the email 'contact@innovatecorp.com'."
    
    response = agent_executor.invoke({"input": question})
    
    print("\n--- Final Answer ---")
    print(response["output"])