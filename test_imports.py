#!/usr/bin/env python3
"""Test script to check Streamlit app import."""

import sys
import os

# Add src to path
sys.path.insert(0, 'src')

try:
    print("Testing Streamlit app import...")
    from wjp_analyser.web.streamlit_app import main
    print("✅ Streamlit app imported successfully!")
    
    print("Testing unified web app import...")
    from wjp_analyser.web.unified_web_app import WJPUnifiedWebApp
    print("✅ Unified web app imported successfully!")
    
    print("Testing package components...")
    import wjp_analyser
    print("✅ WJP package imported successfully!")
    
    print("All imports successful!")
    
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
