# Merge Instructions for RAG PDF Functionality

This document provides instructions for merging the `feature/rag-pdf-functionality` branch back to the main branch.

## Changes Made

This feature branch implements RAG (Retrieval Augmented Generation) functionality with PDF upload and chat capabilities:

- **Backend (API)**: Added PDF upload endpoint, RAG chat endpoint, and aimakerspace library integration
- **Frontend**: Added RAG mode toggle, PDF upload UI, and RAG chat functionality
- **Dependencies**: Added PyPDF2 and numpy for PDF processing
- **Configuration**: Added global Cursor rule for branch development

## Merge Instructions

### Option 1: GitHub Pull Request (Recommended)

1. Push the feature branch to your remote repository:
   ```bash
   git push origin feature/rag-pdf-functionality
   ```

2. Go to your GitHub repository in a web browser

3. Click "Compare & pull request" when the banner appears, or go to "Pull requests" → "New pull request"

4. Set the base branch to `main` and compare branch to `feature/rag-pdf-functionality`

5. Add a descriptive title: "Add RAG functionality with PDF upload and chat"

6. Add a description explaining the changes:
   ```
   This PR adds RAG functionality to the AI Engineer Challenge application:
   
   - PDF upload and processing using PyPDF2
   - RAG chat with context retrieval using aimakerspace library
   - Frontend UI for RAG mode toggle and PDF upload
   - Backend API endpoints for PDF processing and RAG chat
   - Error handling and status checking
   ```

7. Click "Create pull request"

8. Review the changes and click "Merge pull request" → "Confirm merge"

9. Delete the feature branch after merging

### Option 2: GitHub CLI

1. Push the feature branch to your remote repository:
   ```bash
   git push origin feature/rag-pdf-functionality
   ```

2. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Add RAG functionality with PDF upload and chat" --body "This PR adds RAG functionality to the AI Engineer Challenge application with PDF upload, processing, and chat capabilities."
   ```

3. Review the pull request in your browser or using:
   ```bash
   gh pr view
   ```

4. Merge the pull request:
   ```bash
   gh pr merge --merge
   ```

5. Delete the feature branch:
   ```bash
   git checkout main
   git pull origin main
   git branch -d feature/rag-pdf-functionality
   git push origin --delete feature/rag-pdf-functionality
   ```

### Option 3: Direct Merge (Not Recommended for Production)

If you prefer to merge directly without a pull request:

1. Switch to main branch:
   ```bash
   git checkout main
   ```

2. Pull latest changes:
   ```bash
   git pull origin main
   ```

3. Merge the feature branch:
   ```bash
   git merge feature/rag-pdf-functionality
   ```

4. Push to remote:
   ```bash
   git push origin main
   ```

5. Delete the feature branch:
   ```bash
   git branch -d feature/rag-pdf-functionality
   ```

## Post-Merge Steps

After merging, you should:

1. Test the RAG functionality locally
2. Deploy the updated application to Vercel
3. Verify that PDF upload and RAG chat work correctly
4. Update any documentation if needed

## Files Modified

- `api/app.py` - Added RAG endpoints and PDF processing
- `api/requirements.txt` - Added PyPDF2 and numpy dependencies
- `frontend/pages/index.tsx` - Added RAG UI components
- `aimakerspace/` - Added aimakerspace library (new directory)
- `.cursor/rules/branch-development.mdc` - Added global Cursor rule (new file)

## Testing

Before merging, ensure:
- [ ] PDF upload works correctly
- [ ] RAG chat retrieves relevant context
- [ ] Regular chat still works
- [ ] Error handling works for invalid PDFs
- [ ] UI properly toggles between modes
