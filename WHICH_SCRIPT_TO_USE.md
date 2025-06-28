# 🎯 WHICH SCRIPT TO USE - Simple Guide

## 🚀 **MAIN SCRIPT TO USE (Recommended)**

### **Simple & Reliable (BEST CHOICE):**
```bash
C:\Users\User\miniconda3\envs\odoo1\python.exe smart_assistant_simple.py
```

**Why this one?**
- ✅ **Always works** (no LLM rate limit issues)
- ✅ **Direct Odoo integration** (no AI middleman)
- ✅ **Fast & reliable** (instant results)
- ✅ **Perfect for Belgium**
- ✅ **No API costs** (direct tool usage)

### **Advanced Version (If you need AI features):**
```bash
C:\Users\User\miniconda3\envs\odoo1\python.exe smart_assistant_vertex_ai.py
```

**When to use:**
- ⚠️ If you need AI-generated content
- ⚠️ If you need email drafting
- ⚠️ May have LLM rate limit issues

## 🔧 **BACKUP SCRIPT (If Vertex AI has issues)**

### **Google AI Studio Version:**
```bash
C:\Users\User\miniconda3\envs\odoo1\python.exe smart_assistant_optimized.py
```

**When to use:**
- ⚠️ If Vertex AI is down
- ⚠️ If you have Google Cloud billing issues
- ⚠️ As a simple fallback option

**Limitations:**
- ❌ Only 15 requests/minute
- ❌ Rate limit errors possible

## 🧪 **TEST SCRIPTS (Keep for troubleshooting)**

### **Quick Vertex AI Test:**
```bash
C:\Users\User\miniconda3\envs\odoo1\python.exe test_model_versions.py
```
**Use to:** Verify your Vertex AI setup is working

### **Odoo Connection Test:**
```bash
C:\Users\User\miniconda3\envs\odoo1\python.exe test_odoo_connection.py
```
**Use to:** Test if Odoo connection and customer search is working

### **Regional Test:**
```bash
C:\Users\User\miniconda3\envs\odoo1\python.exe test_belgium_regions.py
```
**Use to:** Test different European regions

## ❌ **SCRIPTS TO DELETE (Outdated/Redundant)**

These files are no longer needed and can be safely deleted:

### **Old/Redundant Scripts:**
- `02_odoo_agent.py` - Old single agent version
- `03_crewai_research_team.py` - Research prototype
- `04_odoo_crew.py` - Early crew version
- `05_odoo_team_crew.py` - Team prototype
- `06_interactive_crew.py` - Interactive prototype
- `07_product_crew.py` - Product-only crew
- `08_update_product_tool.py` - Single tool file
- `09_product_polisher_crew.py` - Polisher prototype
- `09_product_polisher_crew_debug.py` - Debug version
- `12_multilingual_crew_final.py` - Old final version
- `simple_customer_lookup.py` - Simple lookup only
- `smart_assistant.py` - Old assistant version
- `smart_assistant_flow.py` - Flow prototype

### **Diagnostic Scripts (Can delete after setup works):**
- `test_api_access.py` - Basic diagnostic
- `test_google_cloud_setup.py` - Setup test
- `vertex_ai_diagnostic.py` - Multi-region test
- `test_cost_optimization.py` - Cost test

### **Documentation (Can delete if you don't need reference):**
- `FIX_404_ERROR.md` - 404 troubleshooting
- `VERTEX_AI_FIX.md` - Vertex AI guide
- `GOOGLE_CLOUD_TROUBLESHOOTING.md` - Troubleshooting
- `COST_OPTIMIZATION_ANALYSIS.md` - Cost analysis

## 📁 **FINAL PROJECT STRUCTURE (Recommended)**

### **Keep These Files:**
```
📁 My_first_odoo_agent/
├── 🚀 smart_assistant_vertex_ai.py          # MAIN SCRIPT
├── 🔄 smart_assistant_optimized.py          # BACKUP SCRIPT
├── 🧪 test_model_versions.py                # QUICK TEST
├── 🧪 test_belgium_regions.py               # REGIONAL TEST
├── 📖 WHICH_SCRIPT_TO_USE.md                # THIS GUIDE
├── 📖 BELGIUM_REGION_FIX.md                 # BELGIUM SETUP
├── 📖 README.md                             # PROJECT INFO
├── ⚙️ requirements.txt                      # DEPENDENCIES
├── ⚙️ .env.template                         # ENV TEMPLATE
├── 🔐 google-cloud-credentials.json         # YOUR CREDENTIALS
└── 📁 tools/                               # TOOL MODULES
    ├── odoo_connection.py
    ├── customer_tools.py
    └── multilingual_product_tools.py
```

### **Delete These Files:**
```
❌ All numbered scripts (02_, 03_, 04_, etc.)
❌ Old smart_assistant versions
❌ Most diagnostic scripts (after setup works)
❌ Extra documentation files
```

## 🎯 **SIMPLE WORKFLOW**

### **Daily Use:**
1. **Run main script:** `smart_assistant_vertex_ai.py`
2. **If issues:** Run test script: `test_model_versions.py`
3. **If still issues:** Use backup: `smart_assistant_optimized.py`

### **Setup/Troubleshooting:**
1. **Regional issues:** Run `test_belgium_regions.py`
2. **Read guides:** `BELGIUM_REGION_FIX.md`

## 🧹 **CLEANUP COMMANDS**

### **Safe Cleanup (Recommended):**
```bash
# Create backup folder first
mkdir archive_old_scripts

# Move old scripts to archive
move 02_*.py archive_old_scripts/
move 03_*.py archive_old_scripts/
move 04_*.py archive_old_scripts/
move 05_*.py archive_old_scripts/
move 06_*.py archive_old_scripts/
move 07_*.py archive_old_scripts/
move 08_*.py archive_old_scripts/
move 09_*.py archive_old_scripts/
move 12_*.py archive_old_scripts/
move simple_*.py archive_old_scripts/
move smart_assistant.py archive_old_scripts/
move smart_assistant_flow.py archive_old_scripts/
```

### **After Confirming Everything Works:**
```bash
# Delete archive folder
rmdir /s archive_old_scripts
```

---

## 🎉 **SUMMARY**

**USE THIS:** `smart_assistant_vertex_ai.py` (Main production script)
**BACKUP:** `smart_assistant_optimized.py` (If main has issues)
**TEST:** `test_model_versions.py` (Verify setup)
**CLEANUP:** Delete all numbered scripts and old versions

**Your project will be much cleaner and easier to understand!**
