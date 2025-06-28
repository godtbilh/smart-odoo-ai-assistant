# Google Cloud API Setup Guide for Gemini Pro/Flash

This guide will help you upgrade from the free Google AI Studio API to Google Cloud's production-ready Gemini API with higher rate limits and better reliability.

## 🎯 Why Upgrade to Google Cloud API?

### **Free Google AI Studio Limits:**
- ⚠️ Very low rate limits (15 requests per minute)
- ⚠️ Frequent rate limit errors
- ⚠️ Not suitable for production use

### **Google Cloud API Benefits:**
- ✅ Much higher rate limits (1000+ requests per minute)
- ✅ Production-grade reliability
- ✅ Pay-per-use pricing (very affordable)
- ✅ Better error handling and monitoring

## 📋 Step-by-Step Setup Process

### **Step 1: Access Google Cloud Console**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account
3. If you don't have a project, create a new one:
   - Click "Select a project" → "New Project"
   - Name: `odoo-ai-assistant` (or your preferred name)
   - Click "Create"

### **Step 2: Enable Billing (Required)**
1. In the Google Cloud Console, go to **Billing**
2. Link a payment method (credit card)
3. **Don't worry**: Gemini API is very affordable:
   - Flash: ~$0.075 per 1M input tokens
   - Pro: ~$1.25 per 1M input tokens
   - Your monthly cost will likely be under $5-10

### **Step 3: Enable the Vertex AI API**
1. Go to **APIs & Services** → **Library**
2. Search for "Vertex AI API"
3. Click on "Vertex AI API"
4. Click **"Enable"**
5. Wait for activation (may take a few minutes)

### **Step 4: Create Service Account & API Key**
1. Go to **APIs & Services** → **Credentials**
2. Click **"Create Credentials"** → **"Service Account"**
3. Fill in details:
   - **Service account name**: `odoo-ai-assistant`
   - **Service account ID**: `odoo-ai-assistant` (auto-filled)
   - **Description**: `AI assistant for Odoo integration`
4. Click **"Create and Continue"**
5. **Grant roles**:
   - Add role: **"Vertex AI User"**
   - Add role: **"AI Platform Developer"**
6. Click **"Continue"** → **"Done"**

### **Step 5: Generate JSON Key File**
1. In **Credentials**, find your service account
2. Click on the service account name
3. Go to **"Keys"** tab
4. Click **"Add Key"** → **"Create new key"**
5. Select **"JSON"** format
6. Click **"Create"**
7. **Save the downloaded JSON file** to your project directory
8. **Rename it to**: `google-cloud-credentials.json`

### **Step 6: Set Up Authentication**
1. **Option A: Environment Variable (Recommended)**
   ```bash
   # Add to your .env file
   GOOGLE_APPLICATION_CREDENTIALS=./google-cloud-credentials.json
   ```

2. **Option B: Direct Path in Code**
   ```python
   import os
   os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./google-cloud-credentials.json"
   ```

### **Step 7: Install Required Libraries**
```bash
pip install google-cloud-aiplatform
pip install vertexai
```

### **Step 8: Update Your Code**
Replace your current Gemini configuration with this Google Cloud version:

```python
import vertexai
from vertexai.generative_models import GenerativeModel

# Initialize Vertex AI
vertexai.init(project="your-project-id", location="us-central1")

# Create models
flash_model = GenerativeModel("gemini-1.5-flash")
pro_model = GenerativeModel("gemini-1.5-pro")
```

## 🔧 Configuration for CrewAI

### **Updated LLM Configuration:**
```python
from crewai import LLM
import os

# Set up Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./google-cloud-credentials.json"

# Configure LLMs for Google Cloud
flash_llm = LLM(
    model="vertex_ai/gemini-1.5-flash",
    project_id="your-project-id",
    location="us-central1"
)

pro_llm = LLM(
    model="vertex_ai/gemini-1.5-pro", 
    project_id="your-project-id",
    location="us-central1"
)
```

## 📊 Rate Limits Comparison

### **Google AI Studio (Free):**
- Flash: 15 requests/minute
- Pro: 2 requests/minute
- ❌ Frequent rate limit errors

### **Google Cloud (Paid):**
- Flash: 1000+ requests/minute
- Pro: 300+ requests/minute  
- ✅ Production-ready limits

## 💰 Cost Estimation

### **Typical Usage (100 requests/month):**
- **Flash LLM**: ~$0.50/month
- **Pro LLM**: ~$2.00/month
- **Total**: ~$2.50/month for moderate usage

### **Heavy Usage (1000 requests/month):**
- **Flash LLM**: ~$5.00/month
- **Pro LLM**: ~$20.00/month
- **Total**: ~$25.00/month for heavy usage

## 🛡️ Security Best Practices

### **Protect Your Credentials:**
1. **Never commit** `google-cloud-credentials.json` to Git
2. **Add to .gitignore**:
   ```
   google-cloud-credentials.json
   *.json
   ```
3. **Use environment variables** for production
4. **Rotate keys** periodically for security

### **Project Structure:**
```
my-first-odoo-agent/
├── .env                           # Environment variables
├── .gitignore                     # Ignore credentials
├── google-cloud-credentials.json  # Your service account key
├── smart_assistant_optimized.py   # Your AI assistant
└── requirements.txt               # Dependencies
```

## 🚀 Testing Your Setup

### **Quick Test Script:**
```python
import vertexai
from vertexai.generative_models import GenerativeModel
import os

# Set credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./google-cloud-credentials.json"

# Initialize
vertexai.init(project="your-project-id", location="us-central1")

# Test
model = GenerativeModel("gemini-1.5-flash")
response = model.generate_content("Hello, this is a test!")
print(response.text)
```

## 🔧 Troubleshooting

### **Common Issues:**

1. **"Project not found"**
   - Verify your project ID in Google Cloud Console
   - Make sure billing is enabled

2. **"API not enabled"**
   - Enable Vertex AI API in Google Cloud Console
   - Wait a few minutes for activation

3. **"Permission denied"**
   - Check service account roles
   - Ensure "Vertex AI User" role is assigned

4. **"Credentials not found"**
   - Verify JSON file path
   - Check GOOGLE_APPLICATION_CREDENTIALS environment variable

## 📞 Support

If you encounter issues:
1. Check [Google Cloud Status](https://status.cloud.google.com/)
2. Review [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
3. Check [Pricing Calculator](https://cloud.google.com/products/calculator)

## 🎉 Next Steps

Once set up:
1. **Test the connection** with the quick test script
2. **Update your AI assistant** with new credentials
3. **Monitor usage** in Google Cloud Console
4. **Enjoy production-ready AI** without rate limits!

---

**Note**: This setup will give you professional-grade API access with much higher rate limits, perfect for your cost-optimized AI assistant!
