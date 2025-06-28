#!/usr/bin/env python3
"""
Vertex AI specific diagnostic for Google Cloud
Based on user feedback: Generative Language API doesn't exist in Google Cloud
"""
import os
import json

def test_vertex_ai_access():
    print("🔍 Vertex AI Specific Diagnostic")
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
    
    # Test different regions
    regions = ["us-central1", "us-east1", "europe-west1", "asia-southeast1"]
    
    for region in regions:
        print(f"\n🌍 Testing region: {region}")
        try:
            import vertexai
            from vertexai.generative_models import GenerativeModel
            
            # Initialize with specific region
            vertexai.init(project=project_id, location=region)
            print(f"✅ Vertex AI initialized for {region}")
            
            # Try to create model
            model = GenerativeModel("gemini-1.5-flash")
            print(f"✅ Model created in {region}")
            
            # Try a simple generation
            response = model.generate_content("Test")
            print(f"✅ SUCCESS in {region}! Response: {response.text[:50]}...")
            return region
            
        except Exception as e:
            print(f"❌ Failed in {region}: {e}")
            if "404" in str(e):
                print(f"   → 404 error in {region}")
            elif "403" in str(e):
                print(f"   → Permission denied in {region}")
            elif "quota" in str(e).lower():
                print(f"   → Quota exceeded in {region}")
    
    print("\n🚨 All regions failed. Let's check service account permissions...")
    
    # Check service account details
    try:
        service_account_email = creds.get("client_email")
        print(f"📧 Service Account: {service_account_email}")
        
        # Check if it's the right type
        if "iam.gserviceaccount.com" in service_account_email:
            print("✅ Valid service account format")
        else:
            print("❌ Invalid service account format")
            
    except Exception as e:
        print(f"❌ Error checking service account: {e}")
    
    print("\n🔧 TROUBLESHOOTING STEPS:")
    print("1. Check Vertex AI API is enabled (not Generative Language API)")
    print("2. Verify service account has 'Vertex AI User' role")
    print("3. Check billing is enabled and active")
    print("4. Try different regions")
    print("5. Check API quotas in Google Cloud Console")

if __name__ == "__main__":
    test_vertex_ai_access()
