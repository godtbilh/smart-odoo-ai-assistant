# test_google_cloud_setup.py - Test Google Cloud Vertex AI Setup

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def test_google_cloud_setup():
    """Test Google Cloud Vertex AI setup and credentials"""
    
    print("🧪 Testing Google Cloud Vertex AI Setup")
    print("=" * 50)
    
    # Step 1: Check if required libraries are installed
    print("\n📦 Checking required libraries...")
    try:
        import vertexai
        from vertexai.generative_models import GenerativeModel
        print("✅ vertexai library installed")
    except ImportError as e:
        print(f"❌ Missing library: {e}")
        print("💡 Install with: pip install google-cloud-aiplatform vertexai")
        return False
    
    # Step 2: Check credentials file
    print("\n🔑 Checking credentials...")
    credentials_path = "./google-cloud-credentials.json"
    if os.path.exists(credentials_path):
        print(f"✅ Credentials file found: {credentials_path}")
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
    else:
        print(f"❌ Credentials file not found: {credentials_path}")
        print("💡 Download your service account JSON key and save it as 'google-cloud-credentials.json'")
        return False
    
    # Step 3: Check project ID
    print("\n🏗️ Checking project configuration...")
    project_id = input("Enter your Google Cloud Project ID: ").strip()
    if not project_id:
        print("❌ Project ID is required")
        return False
    
    # Step 4: Test connection
    print(f"\n🚀 Testing connection to project: {project_id}")
    try:
        # Initialize Vertex AI
        vertexai.init(project=project_id, location="us-central1")
        print("✅ Vertex AI initialized successfully")
        
        # Test Flash model
        print("\n💨 Testing Gemini Flash model...")
        flash_model = GenerativeModel("gemini-1.5-flash")
        flash_response = flash_model.generate_content("Hello! This is a test of Gemini Flash.")
        print(f"✅ Flash model response: {flash_response.text[:100]}...")
        
        # Test Pro model
        print("\n⚖️ Testing Gemini Pro model...")
        pro_model = GenerativeModel("gemini-1.5-pro")
        pro_response = pro_model.generate_content("Hello! This is a test of Gemini Pro.")
        print(f"✅ Pro model response: {pro_response.text[:100]}...")
        
        print("\n🎉 SUCCESS! Google Cloud setup is working correctly!")
        print("\n📋 Configuration Summary:")
        print(f"   Project ID: {project_id}")
        print(f"   Location: us-central1")
        print(f"   Credentials: {credentials_path}")
        print(f"   Flash Model: ✅ Working")
        print(f"   Pro Model: ✅ Working")
        
        # Save configuration for future use
        print(f"\n💾 Saving configuration to .env file...")
        with open('.env', 'a') as f:
            f.write(f"\n# Google Cloud Configuration\n")
            f.write(f"GOOGLE_CLOUD_PROJECT_ID={project_id}\n")
            f.write(f"GOOGLE_APPLICATION_CREDENTIALS=./google-cloud-credentials.json\n")
        
        print("✅ Configuration saved to .env file")
        return True
        
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Verify your project ID is correct")
        print("2. Ensure billing is enabled in Google Cloud Console")
        print("3. Check that Vertex AI API is enabled")
        print("4. Verify service account has 'Vertex AI User' role")
        print("5. Make sure credentials JSON file is valid")
        return False

def test_crewai_integration():
    """Test CrewAI integration with Google Cloud"""
    
    print("\n🤖 Testing CrewAI Integration with Google Cloud")
    print("=" * 50)
    
    try:
        from crewai import LLM
        print("✅ CrewAI library available")
        
        # Load project ID from .env
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID')
        if not project_id:
            print("❌ Project ID not found in .env file")
            return False
        
        print(f"\n🔧 Configuring CrewAI with project: {project_id}")
        
        # Configure LLMs for CrewAI
        flash_llm = LLM(
            model="vertex_ai/gemini-1.5-flash",
            project_id=project_id,
            location="us-central1"
        )
        
        pro_llm = LLM(
            model="vertex_ai/gemini-1.5-pro",
            project_id=project_id,
            location="us-central1"
        )
        
        print("✅ CrewAI LLMs configured successfully")
        print("✅ Ready for production use with higher rate limits!")
        
        return True
        
    except ImportError:
        print("❌ CrewAI not installed")
        print("💡 Install with: pip install crewai")
        return False
    except Exception as e:
        print(f"❌ CrewAI configuration failed: {e}")
        return False

def main():
    """Main test function"""
    
    print("🚀 Google Cloud Vertex AI Setup Test")
    print("This script will help you verify your Google Cloud configuration")
    print("=" * 60)
    
    # Test basic setup
    if not test_google_cloud_setup():
        print("\n❌ Basic setup failed. Please fix the issues above and try again.")
        return
    
    # Test CrewAI integration
    if not test_crewai_integration():
        print("\n⚠️ CrewAI integration failed, but basic Google Cloud setup is working.")
        print("You can still use Google Cloud directly, just not with CrewAI yet.")
        return
    
    print("\n🎉 COMPLETE SUCCESS!")
    print("Your Google Cloud Vertex AI setup is ready for production use!")
    print("\n🚀 Next steps:")
    print("1. Update your AI assistant to use Google Cloud credentials")
    print("2. Enjoy much higher rate limits (1000+ requests/minute)")
    print("3. Monitor usage in Google Cloud Console")
    print("4. Start saving money with cost-optimized routing!")

if __name__ == "__main__":
    main()
