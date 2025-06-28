# tools/multilingual_product_tools.py - Proper Multilingual Product Management for Odoo

import os
import xmlrpc.client
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Optional, Dict, List

class FindProductInput(BaseModel):
    product_name: str = Field(description="The name of the product to search for.")

class OdooMultilingualProductFinder(BaseTool):
    name: str = "Odoo Multilingual Product Finder"
    description: str = "Finds product information including ALL multilingual descriptions (English, Dutch, French) using proper Odoo API."
    args_schema: Type[BaseModel] = FindProductInput

    def __init__(self, models, db, uid, password):
        super().__init__()
        # Store connection info in a way that doesn't conflict with Pydantic
        object.__setattr__(self, '_models', models)
        object.__setattr__(self, '_db', db)
        object.__setattr__(self, '_uid', uid)
        object.__setattr__(self, '_password', password)

    def _run(self, product_name: str) -> str:
        print(f"\n🔍 TOOL EXECUTING: Searching for product '{product_name}' with multilingual data...")
        try:
            # Step 1: Find the product
            search_domain = [('name', '=ilike', product_name)]
            fields = ['id', 'name', 'description_sale', 'list_price', 'categ_id']
            product_data = self._models.execute_kw(self._db, self._uid, self._password, 
                'product.product', 'search_read', [search_domain], {'fields': fields, 'limit': 5})
            
            if not product_data:
                return f"No products found matching '{product_name}'. Try a broader search term."
            
            result = f"Found {len(product_data)} product(s) with multilingual data:\n\n"
            
            for product in product_data:
                product_id = product['id']
                result += f"Product ID: {product_id}\n"
                result += f"Name: {product['name']}\n"
                result += f"Price: {product.get('list_price', 'N/A')}\n"
                result += f"Category: {product.get('categ_id', ['N/A'])[1] if product.get('categ_id') else 'N/A'}\n"
                
                # Step 2: Get multilingual descriptions using proper Odoo API
                multilingual_descriptions = self._get_multilingual_descriptions(product_id)
                
                result += "Multilingual Descriptions:\n"
                for lang, desc in multilingual_descriptions.items():
                    result += f"  {lang}: {desc[:100]}{'...' if len(desc) > 100 else ''}\n"
                
                result += "-" * 50 + "\n"
            
            return result
                
        except Exception as e:
            return f"Error searching for product: {e}"
    
    def _get_multilingual_descriptions(self, product_id: int) -> Dict[str, str]:
        """Get descriptions in all languages for a product"""
        descriptions = {}
        languages = [
            ('en_US', 'English'),
            ('nl_NL', 'Dutch')
        ]
        
        for lang_code, lang_name in languages:
            try:
                # Use proper context to get language-specific data
                context = {'lang': lang_code}
                product_data = self._models.execute_kw(self._db, self._uid, self._password,
                    'product.product', 'read', [[product_id]], 
                    {'fields': ['description_sale'], 'context': context})
                
                if product_data:
                    desc = product_data[0].get('description_sale', '') or ''
                    descriptions[lang_name] = desc
                else:
                    descriptions[lang_name] = 'No description'
                    
            except Exception as e:
                descriptions[lang_name] = f'Error: {e}'
        
        return descriptions

class UpdateMultilingualProductInput(BaseModel):
    product_id: int = Field(description="The unique integer ID of the product to update.")
    descriptions: Dict[str, str] = Field(description="Dictionary with language names as keys (English, Dutch, French) and descriptions as values.")

class OdooMultilingualProductUpdater(BaseTool):
    name: str = "Odoo Multilingual Product Updater"
    description: str = "Updates product descriptions in multiple languages (English, Dutch, French) using proper Odoo translation API."
    args_schema: Type[BaseModel] = UpdateMultilingualProductInput

    def __init__(self, models, db, uid, password):
        super().__init__()
        # Store connection info in a way that doesn't conflict with Pydantic
        object.__setattr__(self, '_models', models)
        object.__setattr__(self, '_db', db)
        object.__setattr__(self, '_uid', uid)
        object.__setattr__(self, '_password', password)

    def _run(self, product_id: int, descriptions: Dict[str, str]) -> str:
        print(f"\n🔄 TOOL EXECUTING: Updating product ID {product_id} with multilingual descriptions...")
        
        language_mapping = {
            'English': 'en_US',
            'Dutch': 'nl_NL'
        }
        
        results = []
        
        try:
            for lang_name, description in descriptions.items():
                if lang_name not in language_mapping:
                    results.append(f"❌ Unknown language: {lang_name}")
                    continue
                
                lang_code = language_mapping[lang_name]
                
                try:
                    # Method 1: Try direct update with language context
                    success = self._update_with_context(product_id, description, lang_code, lang_name)
                    
                    if not success:
                        # Method 2: Try translation record update
                        success = self._update_translation_record(product_id, description, lang_code, lang_name)
                    
                    if success:
                        results.append(f"✅ Successfully updated {lang_name} description")
                    else:
                        results.append(f"❌ Failed to update {lang_name} description")
                        
                except Exception as e:
                    results.append(f"❌ Error updating {lang_name}: {e}")
            
            # Verify the updates
            verification = self._verify_updates(product_id, descriptions)
            results.append(f"\n🔍 Verification Results:\n{verification}")
            
            return "\n".join(results)
            
        except Exception as e:
            return f"❌ Critical error during multilingual update: {e}"
    
    def _update_with_context(self, product_id: int, description: str, lang_code: str, lang_name: str) -> bool:
        """Try updating using language context (Method 1)"""
        try:
            context = {'lang': lang_code}
            update_values = {'description_sale': description}
            
            result = self._models.execute_kw(self._db, self._uid, self._password, 
                'product.product', 'write', [[product_id], update_values], {'context': context})
            
            print(f"  Context update for {lang_name}: {result}")
            return bool(result)
            
        except Exception as e:
            print(f"  Context update failed for {lang_name}: {e}")
            return False
    
    def _update_translation_record(self, product_id: int, description: str, lang_code: str, lang_name: str) -> bool:
        """Try updating using ir.translation records (Method 2)"""
        try:
            # Search for existing translation record
            translation_domain = [
                ('name', '=', 'product.product,description_sale'),
                ('res_id', '=', product_id),
                ('lang', '=', lang_code)
            ]
            
            existing_translations = self._models.execute_kw(self._db, self._uid, self._password,
                'ir.translation', 'search_read', [translation_domain], {'fields': ['id', 'value']})
            
            if existing_translations:
                # Update existing translation
                translation_id = existing_translations[0]['id']
                result = self._models.execute_kw(self._db, self._uid, self._password,
                    'ir.translation', 'write', [[translation_id], {'value': description}])
                print(f"  Translation record updated for {lang_name}: {result}")
                return bool(result)
            else:
                # Create new translation record
                translation_data = {
                    'name': 'product.product,description_sale',
                    'res_id': product_id,
                    'lang': lang_code,
                    'value': description,
                    'type': 'model'
                }
                
                translation_id = self._models.execute_kw(self._db, self._uid, self._password,
                    'ir.translation', 'create', [translation_data])
                print(f"  Translation record created for {lang_name}: {translation_id}")
                return bool(translation_id)
                
        except Exception as e:
            print(f"  Translation record update failed for {lang_name}: {e}")
            return False
    
    def _verify_updates(self, product_id: int, expected_descriptions: Dict[str, str]) -> str:
        """Verify that the updates actually worked"""
        verification_results = []
        language_mapping = {
            'English': 'en_US',
            'Dutch': 'nl_NL'
        }
        
        for lang_name, expected_desc in expected_descriptions.items():
            if lang_name not in language_mapping:
                continue
                
            lang_code = language_mapping[lang_name]
            
            try:
                # Check actual current value
                context = {'lang': lang_code}
                product_data = self._models.execute_kw(self._db, self._uid, self._password,
                    'product.product', 'read', [[product_id]], 
                    {'fields': ['description_sale'], 'context': context})
                
                if product_data:
                    actual_desc = product_data[0].get('description_sale', '') or ''
                    if actual_desc.strip() == expected_desc.strip():
                        verification_results.append(f"✅ {lang_name}: Update verified")
                    else:
                        verification_results.append(f"❌ {lang_name}: Update failed - Expected length {len(expected_desc)}, got length {len(actual_desc)}")
                else:
                    verification_results.append(f"❌ {lang_name}: Could not read back data")
                    
            except Exception as e:
                verification_results.append(f"❌ {lang_name}: Verification error - {e}")
        
        return "\n".join(verification_results)

class ProductContentGeneratorInput(BaseModel):
    base_info: str = Field(description="Base information about the product to generate content from.")
    content_type: str = Field(description="Type of content to generate: 'title', 'description', or 'features'.")
    languages: List[str] = Field(description="List of target languages: ['English', 'Dutch', 'French'].")

class MultilingualProductContentGenerator(BaseTool):
    name: str = "Multilingual Product Content Generator"
    description: str = "Generates compelling product content in multiple languages based on base information."
    args_schema: Type[BaseModel] = ProductContentGeneratorInput

    def _run(self, base_info: str, content_type: str, languages: List[str]) -> str:
        print(f"\n✍️ TOOL EXECUTING: Generating {content_type} in {len(languages)} languages...")
        
        # This tool provides structured output for the AI agent to enhance
        result = f"Content Generation Request:\n"
        result += f"Base Information: {base_info}\n"
        result += f"Content Type: {content_type}\n"
        result += f"Target Languages: {', '.join(languages)}\n"
        result += f"Status: Ready for AI enhancement\n\n"
        
        result += "Instructions for AI Agent:\n"
        result += f"1. Create compelling {content_type} based on: {base_info}\n"
        result += f"2. Generate content for each language: {', '.join(languages)}\n"
        result += "3. Ensure content is culturally appropriate for each language\n"
        result += "4. Focus on benefits over features\n"
        result += "5. Keep descriptions engaging and professional\n"
        
        return result
