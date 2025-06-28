#!/usr/bin/env python3
"""
Test different Gemini model versions to find working ones
"""
import os
import json

def test_model_versions():
    print("🧪 Testing Different Gemini Model Versions")
    print("=" * 50)
    
    # Set credentials
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./google-cloud-credentials.json"
    
    # Load project ID
    with open("./google-cloud-credentials.json", "r") as f:
        creds = json.load(f)
        project_id = creds.get("project_id")
    
    # Initialize Vertex AI
    import vertexai
    from vertexai.generative_models import GenerativeModel
    
    vertexai.init(project=project_id, location="us-central1")
    print(f"✅ Vertex AI initialized for project: {project_id}")
    
    # Test different model names
    model_names = [
        "gemini-1.5-flash",
        "gemini-1.5-flash-001",
        "gemini-1.5-flash-002", 
        "gemini-1.5-pro",
        "gemini-1.5-pro-001",
        "gemini-1.5-pro-002",
        "gemini-pro",
        "gemini-pro-001",
        "gemini-pro-vision",
        "text-bison",
        "text-bison-001",
        "chat-bison",
        "chat-bison-001"
    ]
    
    working_models = []
    
    for model_name in model_names:
        try:
            print(f"\n🔍 Testing model: {model_name}")
            model = GenerativeModel(model_name)
            response = model.generate_content("Hello, respond with just 'OK'")
            print(f"✅ SUCCESS with {model_name}: {response.text.strip()}")
            working_models.append(model_name)
            
        except Exception as e:
            print(f"❌ Failed with {model_name}: {str(e)[:100]}...")
            if "404" in str(e):
                print(f"   → 404: Model not found")
            elif "403" in str(e):
                print(f"   → 403: Permission denied")
            elif "quota" in str(e).lower():
                print(f"   → Quota exceeded")
    
    print(f"\n🎉 WORKING MODELS FOUND: {len(working_models)}")
    for model in working_models:
        print(f"✅ {model}")
    
    if not working_models:
        print("\n🚨 NO WORKING MODELS FOUND")
        print("This confirms the Vertex AI Generative AI API is not enabled.")
        print("\n🔧 SOLUTION:")
        print("1. Go to Google Cloud Console")
        print("2. Enable 'Vertex AI Generative AI API'")
        print("3. Wait 5-10 minutes")
        print("4. Run this test again")
    
    return working_models

if __name__ == "__main__":
    test_model_versions()
