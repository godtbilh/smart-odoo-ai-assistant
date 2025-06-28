#!/usr/bin/env python3
"""
Quick test to diagnose Google Cloud API access issues
"""
import os
import json

def test_google_cloud_access():
    print("🔍 Google Cloud API Access Diagnostic")
    print("=" * 50)
    
    # Set credentials
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./google-cloud-credentials.json"
    
    # Load project ID from credentials
    try:
        with open("./google-cloud-credentials.json", "r") as f:
            creds = json.load(f)
            project_id = creds.get("project_id")
            print(f"✅ Project ID: {project_id}")
    except Exception as e:
        print(f"❌ Error reading credentials: {e}")
        return
    
    # Test Vertex AI initialization
    try:
        import vertexai
        print("✅ vertexai library imported")
        
        # Initialize with correct project
        vertexai.init(project=project_id, location="us-central1")
        print(f"✅ Vertex AI initialized for project: {project_id}")
        
    except Exception as e:
        print(f"❌ Vertex AI initialization failed: {e}")
        return
    
    # Test model access
    try:
        from vertexai.generative_models import GenerativeModel
        print("✅ GenerativeModel imported")
        
        # Try to create Flash model
        flash_model = GenerativeModel("gemini-1.5-flash")
        print("✅ Flash model created")
        
        # Try a simple generation
        response = flash_model.generate_content("Hello, this is a test. Please respond with 'Test successful!'")
        print(f"✅ Flash model response: {response.text}")
        
    except Exception as e:
        print(f"❌ Model access failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        
        # Check if it's a 404 error
        if "404" in str(e):
            print("\n🚨 404 ERROR DETECTED!")
            print("This means the Generative Language API is not enabled.")
            print("\n🔧 SOLUTION:")
            print("1. Go to: https://console.cloud.google.com/")
            print("2. Select project: odoo-ai-assistant")
            print("3. Go to: APIs & Services → Library")
            print("4. Search: 'Generative Language API'")
            print("5. Click: Enable")
            print("6. Wait: 5-10 minutes for activation")
        
        return
    
    print("\n🎉 SUCCESS! Google Cloud setup is working correctly!")

if __name__ == "__main__":
    test_google_cloud_access()
