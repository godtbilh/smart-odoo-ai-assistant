# tools/odoo_connection.py - Odoo Connection Management

import os
import xmlrpc.client
from dotenv import load_dotenv

class OdooConnection:
    """Manages Odoo XML-RPC connection and authentication"""
    
    def __init__(self):
        load_dotenv()
        self.url = None
        self.db = None
        self.username = None
        self.password = None
        self.uid = None
        self.models = None
        self.common = None
        
    def connect(self):
        """Establish connection to Odoo and authenticate"""
        try:
            # Load environment variables
            self.url = os.environ["ODOO_URL"]
            self.db = os.environ["ODOO_DB"]
            self.username = os.environ["ODOO_USERNAME"]
            self.password = os.environ["ODOO_PASSWORD"]
            
            print(f"🔗 Connecting to Odoo at {self.url}...")
            
            # Establish XML-RPC connections
            self.common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
            self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
            
            # Test connection and get version info
            version_info = self.common.version()
            print(f"📋 Odoo Server Version: {version_info.get('server_version', 'Unknown')}")
            
            # Authenticate
            self.uid = self.common.authenticate(self.db, self.username, self.password, {})
            
            if self.uid:
                print(f"✅ Successfully connected and authenticated with Odoo.")
                print(f"🔍 Connected as user ID: {self.uid}")
                return True
            else:
                print("❌ Authentication failed. Please check your credentials.")
                return False
                
        except KeyError as e:
            print(f"❌ Missing environment variable: {e}")
            print("Please ensure your .env file contains: ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD")
            return False
        except Exception as e:
            print(f"❌ Failed to connect to Odoo. Error: {e}")
            return False
    
    def test_connection(self):
        """Test the connection by making a simple query"""
        try:
            if not self.uid or not self.models:
                print("❌ Not connected to Odoo. Call connect() first.")
                return False
            
            # Test with a simple query
            result = self.models.execute_kw(
                self.db, self.uid, self.password,
                'res.users', 'read', [[self.uid]], {'fields': ['name']}
            )
            
            if result:
                user_name = result[0].get('name', 'Unknown')
                print(f"🧪 Connection test successful. Logged in as: {user_name}")
                return True
            else:
                print("❌ Connection test failed.")
                return False
                
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False
    
    def get_connection_info(self):
        """Return connection information for tools"""
        if not self.uid:
            raise Exception("Not connected to Odoo. Call connect() first.")
        
        return {
            'models': self.models,
            'db': self.db,
            'uid': self.uid,
            'password': self.password,
            'url': self.url
        }
    
    def execute_kw(self, model, method, args=None, kwargs=None):
        """Convenience method for executing Odoo operations"""
        if not self.uid:
            raise Exception("Not connected to Odoo. Call connect() first.")
        
        args = args or []
        kwargs = kwargs or {}
        
        return self.models.execute_kw(
            self.db, self.uid, self.password,
            model, method, args, kwargs
        )
    
    def search_read(self, model, domain=None, fields=None, limit=None, order=None):
        """Convenience method for search_read operations"""
        domain = domain or []
        kwargs = {}
        
        if fields:
            kwargs['fields'] = fields
        if limit:
            kwargs['limit'] = limit
        if order:
            kwargs['order'] = order
            
        return self.execute_kw(model, 'search_read', [domain], kwargs)
    
    def create_record(self, model, values):
        """Convenience method for creating records"""
        return self.execute_kw(model, 'create', [values])
    
    def update_record(self, model, record_ids, values):
        """Convenience method for updating records"""
        if not isinstance(record_ids, list):
            record_ids = [record_ids]
        return self.execute_kw(model, 'write', [record_ids, values])
    
    def delete_record(self, model, record_ids):
        """Convenience method for deleting records"""
        if not isinstance(record_ids, list):
            record_ids = [record_ids]
        return self.execute_kw(model, 'unlink', [record_ids])
