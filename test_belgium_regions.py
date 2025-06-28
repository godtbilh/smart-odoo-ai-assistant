#!/usr/bin/env python3
"""
Test Vertex AI access from Belgium with European regions
"""
import os
import json

def test_belgium_regions():
    print("🇧🇪 Testing Vertex AI Access from Belgium")
    print("=" * 50)
    
    # Set credentials
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./google-cloud-credentials.json"
    
    # Load project ID
    with open("./google-cloud-credentials.json", "r") as f:
        creds = json.load(f)
        project_id = creds.get("project_id")
    
    # Test European regions specifically
    european_regions = [
        "europe-west1",      # Belgium
        "europe-west2",      # London
        "europe-west3",      # Frankfurt
        "europe-west4",      # Netherlands
        "europe-west6",      # Zurich
        "europe-west8",      # Milan
        "europe-west9",      # Paris
        "europe-central2",   # Warsaw
        "europe-north1",     # Finland
        "europe-southwest1"  # Madrid
    ]
    
    import vertexai
    from vertexai.generative_models import GenerativeModel
    
    working_regions = []
    
    for region in european_regions:
        print(f"\n🌍 Testing region: {region}")
        try:
            # Initialize with specific region
            vertexai.init(project=project_id, location=region)
            print(f"✅ Vertex AI initialized for {region}")
            
            # Try to create Flash model
            model = GenerativeModel("gemini-1.5-flash")
            print(f"✅ Model created in {region}")
            
            # Try a simple generation
            response = model.generate_content("Hello from Belgium! Respond with just 'Bonjour!'")
            print(f"✅ SUCCESS in {region}! Response: {response.text.strip()}")
            working_regions.append(region)
            
            # If we found one working region, test Pro model too
            try:
                pro_model = GenerativeModel("gemini-1.5-pro")
                pro_response = pro_model.generate_content("Test Pro model")
                print(f"✅ Pro model also works in {region}!")
            except Exception as e:
                print(f"⚠️ Flash works but Pro failed in {region}: {str(e)[:50]}...")
            
        except Exception as e:
            print(f"❌ Failed in {region}: {str(e)[:100]}...")
            if "404" in str(e):
                print(f"   → 404: Models not available in {region}")
            elif "403" in str(e):
                print(f"   → 403: Permission denied in {region}")
            elif "quota" in str(e).lower():
                print(f"   → Quota exceeded in {region}")
            elif "region" in str(e).lower():
                print(f"   → Region not supported")
    
    print(f"\n🎉 WORKING REGIONS FOR BELGIUM: {len(working_regions)}")
    for region in working_regions:
        print(f"✅ {region}")
    
    if working_regions:
        print(f"\n🇧🇪 RECOMMENDED REGION FOR BELGIUM: {working_regions[0]}")
        print(f"Update your code to use: location='{working_regions[0]}'")
    else:
        print("\n🚨 NO WORKING REGIONS FOUND")
        print("Gemini models might not be available in European regions yet.")
        print("Try US regions as fallback:")
        print("- us-central1")
        print("- us-east1")
    
    return working_regions

if __name__ == "__main__":
    test_belgium_regions()
