# 🔧 Google Cloud Troubleshooting Guide

## ❌ **Error 404: Model Not Found**

### **Error Message:**
```
❌ Connection failed: 404 Publisher Model `projects/odoo-ai-assistant/locations/us-central1/publishers/google/models/gemini-1.5-flash` was not found or your project does not have access to it.
```

### **Root Cause:**
This error occurs when the **Generative Language API** is not enabled in your Google Cloud project.

## 🚀 **Solution: Enable Required APIs**

### **Step 1: Go to Google Cloud Console**
1. Open [console.cloud.google.com](https://console.cloud.google.com/)
2. Select your project: `odoo-ai-assistant`

### **Step 2: Enable All Required APIs**
Go to **APIs & Services** → **Library** and enable these APIs:

#### **✅ Vertex AI API**
- Search: "Vertex AI API"
- Click: "Vertex AI API"
- Click: **"Enable"**

#### **✅ Generative Language API (CRITICAL)**
- Search: "Generative Language API"
- Click: "Generative Language API" 
- Click: **"Enable"**

#### **✅ AI Platform API**
- Search: "AI Platform API"
- Click: "AI Platform API"
- Click: **"Enable"**

### **Step 3: Wait for Activation**
- **Important**: Wait 5-10 minutes for all APIs to fully activate
- APIs need time to propagate across Google's infrastructure

### **Step 4: Test Again**
```bash
C:\Users\User\miniconda3\envs\odoo1\python.exe test_google_cloud_setup.py
```

## 🔍 **Other Common Issues & Solutions**

### **Issue: "Permission Denied"**
**Solution**: Check service account roles
1. Go to **IAM & Admin** → **IAM**
2. Find your service account: `odoo-ai-assistant@your-project.iam.gserviceaccount.com`
3. Ensure it has these roles:
   - **Vertex AI User**
   - **AI Platform Developer**

### **Issue: "Project Not Found"**
**Solution**: Verify project ID
1. In Google Cloud Console, check the project ID in the top bar
2. Make sure you're using the exact project ID (not the project name)
3. Update your code with the correct project ID

### **Issue: "Billing Not Enabled"**
**Solution**: Enable billing
1. Go to **Billing** in Google Cloud Console
2. Link a payment method
3. Ensure billing is enabled for your project

### **Issue: "Credentials Not Found"**
**Solution**: Check credentials file
1. Verify `google-cloud-credentials.json` exists in your project folder
2. Check the file is valid JSON (not corrupted)
3. Ensure the path is correct in your code

## 📋 **Verification Checklist**

Before testing, ensure you have:

- ✅ **Project created**: `odoo-ai-assistant`
- ✅ **Billing enabled**: Credit card linked
- ✅ **Vertex AI API enabled**: ✅
- ✅ **Generative Language API enabled**: ✅ (CRITICAL)
- ✅ **AI Platform API enabled**: ✅
- ✅ **Service account created**: `odoo-ai-assistant`
- ✅ **Service account roles**: Vertex AI User + AI Platform Developer
- ✅ **JSON key downloaded**: `google-cloud-credentials.json`
- ✅ **APIs activated**: Waited 5-10 minutes

## 🧪 **Test Commands**

### **Test 1: Basic Library Check**
```bash
C:\Users\User\miniconda3\envs\odoo1\python.exe -c "import vertexai; print('✅ Libraries installed')"
```

### **Test 2: Credentials Check**
```bash
C:\Users\User\miniconda3\envs\odoo1\python.exe -c "import os; print('✅ Credentials found' if os.path.exists('./google-cloud-credentials.json') else '❌ Credentials missing')"
```

### **Test 3: Full Setup Test**
```bash
C:\Users\User\miniconda3\envs\odoo1\python.exe test_google_cloud_setup.py
```

## 🆘 **Still Having Issues?**

### **Check API Status**
1. Go to **APIs & Services** → **Enabled APIs**
2. Verify all three APIs are listed and enabled
3. Check the status shows "Enabled" (not "Enabling")

### **Check Service Account**
1. Go to **IAM & Admin** → **Service Accounts**
2. Verify your service account exists
3. Check it has the correct roles assigned

### **Check Billing**
1. Go to **Billing**
2. Verify billing account is linked and active
3. Check there are no billing alerts or issues

### **Regional Issues**
If `us-central1` doesn't work, try:
- `us-east1`
- `europe-west1`
- `asia-southeast1`

Update your code to use a different region:
```python
vertexai.init(project="your-project-id", location="us-east1")
```

## 📞 **Get Help**

If you're still stuck:
1. **Google Cloud Status**: [status.cloud.google.com](https://status.cloud.google.com/)
2. **Vertex AI Docs**: [cloud.google.com/vertex-ai/docs](https://cloud.google.com/vertex-ai/docs)
3. **Support**: [cloud.google.com/support](https://cloud.google.com/support)

## 🎯 **Success Indicators**

You'll know it's working when:
- ✅ Test script shows "SUCCESS! Google Cloud setup is working correctly!"
- ✅ Both Flash and Pro models respond with text
- ✅ No 404 or permission errors
- ✅ Your AI assistant runs without rate limits

---

**Remember**: The most common cause of the 404 error is missing the **Generative Language API**. Make sure it's enabled and wait 5-10 minutes for activation!
