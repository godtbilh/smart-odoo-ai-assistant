# 🚀 Quick Start: Google Cloud API Setup

**Goal**: Upgrade from free Google AI Studio to production-ready Google Cloud API with 1000+ requests/minute rate limits.

## ⚡ Quick Setup (15 minutes)

### **Step 1: Google Cloud Console Setup**
1. Go to [console.cloud.google.com](https://console.cloud.google.com/)
2. Create new project: `odoo-ai-assistant`
3. **Enable billing** (required - but very affordable: ~$2-5/month)

### **Step 2: Enable API**
1. Go to **APIs & Services** → **Library**
2. Search "Vertex AI API" → **Enable**

### **Step 3: Create Service Account**
1. **APIs & Services** → **Credentials** → **Create Credentials** → **Service Account**
2. Name: `odoo-ai-assistant`
3. **Grant roles**:
   - `Vertex AI User`
   - `AI Platform Developer`

### **Step 4: Download Credentials**
1. Click on your service account
2. **Keys** tab → **Add Key** → **Create new key** → **JSON**
3. **Save as**: `google-cloud-credentials.json` in your project folder

### **Step 5: Install Libraries**
```bash
pip install google-cloud-aiplatform vertexai
```

### **Step 6: Test Setup**
```bash
python test_google_cloud_setup.py
```

## 🎯 What You Get

### **Before (Google AI Studio Free):**
- ❌ 15 requests/minute (Flash)
- ❌ 2 requests/minute (Pro)
- ❌ Frequent rate limit errors

### **After (Google Cloud):**
- ✅ 1000+ requests/minute (Flash)
- ✅ 300+ requests/minute (Pro)
- ✅ Production-ready reliability
- ✅ Only ~$2-5/month cost

## 💰 Cost Breakdown

### **Typical Usage:**
- **100 requests/month**: ~$2.50
- **500 requests/month**: ~$12.50
- **1000 requests/month**: ~$25.00

### **Cost per Request:**
- **Flash**: ~$0.005 per request
- **Pro**: ~$0.025 per request

## 🔧 After Setup

Once Google Cloud is working, your cost-optimized assistant will:
- ✅ Use Flash LLM for simple tasks (70% cheaper)
- ✅ Use Pro LLM for complex tasks (same quality)
- ✅ No more rate limit errors
- ✅ Production-ready performance

## 📞 Need Help?

1. **Detailed guide**: See `GOOGLE_CLOUD_API_SETUP.md`
2. **Test script**: Run `python test_google_cloud_setup.py`
3. **Google Cloud Console**: [console.cloud.google.com](https://console.cloud.google.com/)

---

**Result**: Professional AI assistant with 1000+ requests/minute and 60-70% cost savings! 🎉
