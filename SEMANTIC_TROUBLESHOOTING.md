# Semantic Bit Theory Troubleshooting Guide

## Issue: Colors Not Showing in Semantic View (Windows/Edge)

If the semantic bit theory colors aren't displaying in Microsoft Edge or other browsers, follow these steps:

### 1. Verify spaCy Installation

The most common issue is that the spaCy language model isn't installed. 

**On Windows:**
```batch
# Open Command Prompt or PowerShell
cd path\to\newdreamflow
.venv\Scripts\activate
python -m spacy download en_core_web_sm
```

**On Mac/Linux:**
```bash
cd path/to/newdreamflow
source .venv/bin/activate
python -m spacy download en_core_web_sm
```

### 2. Test spaCy Installation

After installation, verify it works:
```python
python
>>> import spacy
>>> nlp = spacy.load("en_core_web_sm")
>>> print("spaCy loaded successfully!")
>>> exit()
```

### 3. Restart the Django Server

After installing spaCy, you must restart the Django development server:
```batch
# Windows
.venv\Scripts\activate
python manage.py runserver

# Mac/Linux
source .venv/bin/activate
python manage.py runserver
```

### 4. Browser-Specific Issues

#### Microsoft Edge
- Clear browser cache: `Ctrl + Shift + Delete`
- Disable any ad blockers or privacy extensions that might strip inline styles
- Try opening Developer Tools (`F12`) and check the Console for errors

#### Testing in Other Browsers
Try viewing the semantic analysis in:
- Chrome
- Firefox
- Safari (Mac)

### 5. Verify Semantic Analysis is Working

1. Create or edit a Thing with descriptive text
2. View the Thing detail page
3. Check if the "Show Semantic View" button appears
4. If the button doesn't appear, semantic analysis isn't running

### 6. Check Server Logs

When viewing a Thing, check the server console for any error messages:
- Look for "Warning: spaCy model not loaded"
- Check for any Python errors related to semantic_service

### 7. Manual Color Test

To verify if it's a browser issue, inspect the HTML:
1. Open Developer Tools (`F12`)
2. Click "Show Semantic View"
3. Inspect the text elements
4. Look for `<span>` tags with inline styles like:
   - `style="color: #3B82F6 !important;"` (blue for verbs)
   - `style="color: #10B981 !important;"` (green for nouns)
   - `style="color: #8B5CF6 !important;"` (purple for adjectives)

### 8. Complete Reinstall (Last Resort)

If nothing else works:
```batch
# Windows
rmdir /s .venv
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python manage.py migrate
python manage.py runserver
```

## Expected Behavior

When semantic analysis is working correctly:
- **Verbs** appear in blue (#3B82F6)
- **Nouns** appear in green (#10B981)  
- **Adjectives** appear in purple (#8B5CF6)
- A toggle button switches between normal and colored view
- Statistics show counts of each word type

## Need More Help?

If colors still aren't showing after these steps:
1. Check if the text has any verbs/nouns (try "I walked to the store")
2. Report the issue with:
   - Browser version
   - Windows version
   - Python version (`python --version`)
   - Any error messages from the console