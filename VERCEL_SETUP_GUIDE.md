# 🚀 Vercel Setup Guide for Dream Interpretation Assistant

## 🔑 **Setting Up OpenAI API Key in Vercel**

### **Step 1: Add Environment Variable in Vercel Dashboard**

1. **Go to your Vercel project dashboard**
   - Visit: `https://vercel.com/dashboard`
   - Find your project: `ai-vibe-project` or similar

2. **Navigate to Settings**
   - Click on your project
   - Go to the "Settings" tab
   - Click on "Environment Variables" in the left sidebar

3. **Add the OpenAI API Key**
   - **Name:** `OPENAI_API_KEY`
   - **Value:** Your actual OpenAI API key (starts with `sk-...`)
   - **Environment:** Select "Production" (and optionally "Preview" and "Development")

4. **Save and Redeploy**
   - Click "Save"
   - Go to the "Deployments" tab
   - Click "Redeploy" on the latest deployment

### **Step 2: Verify the Setup**

After redeployment, your app should work without requiring users to enter their API key!

## 🎯 **What This Fixes**

### **Before (Current Issue):**
- Users must enter their own OpenAI API key
- No PDF upload functionality visible
- Basic chat interface only

### **After (Fixed):**
- ✅ **No API key required** - Uses server-configured key
- ✅ **PDF upload visible** - Click gear icon → Enable "Dream Research Mode"
- ✅ **RAG functionality** - Upload PDFs and chat with document content
- ✅ **Dream-themed UI** - Specialized for sleep researchers

## 🔧 **Technical Details**

### **Backend Changes:**
- Added `OPENAI_API_KEY` environment variable support
- Falls back to user-provided key if environment variable not set
- All RAG endpoints now work with server key

### **Frontend Changes:**
- Made API key optional in UI
- Shows helpful message when using server key
- RAG features are now visible in settings panel

### **Vercel Configuration:**
- Added `vercel.json` with environment variable mapping
- Configured proper routing for API and frontend

## 🎬 **Updated Loom Video Script**

The video script has been updated to show:
1. **Click the gear icon** to open settings
2. **Enable "Dream Research Mode"** toggle
3. **Upload PDF** functionality appears
4. **RAG chat** with document-specific answers

## 🚨 **Troubleshooting**

### **If RAG features still don't appear:**
1. Check that the frontend was redeployed after changes
2. Clear browser cache and refresh
3. Check browser console for errors

### **If API key errors occur:**
1. Verify `OPENAI_API_KEY` is set in Vercel environment variables
2. Check that the deployment was successful
3. Look at Vercel function logs for errors

### **If PDF upload fails:**
1. Ensure the backend is using the environment API key
2. Check that PyPDF2 is installed in requirements.txt
3. Verify file size is under Vercel's limits

## 📋 **Next Steps**

1. **Set up the environment variable** in Vercel
2. **Redeploy the application**
3. **Test the RAG functionality** with a sample PDF
4. **Record the Loom video** showing the complete workflow

The application will then work exactly as intended for your Session 3 assignment! 🎉
