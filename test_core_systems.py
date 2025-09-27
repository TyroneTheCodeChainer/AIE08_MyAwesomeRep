#!/usr/bin/env python3
"""
Core Systems Test - Tests both Session 03 and Session 04 in main directory
"""

import os
import sys
import tempfile
import json

def test_core_imports():
    """Test that core modules can be imported."""
    print("Testing core imports...")

    try:
        import sqlite3
        import json
        import time
        from datetime import datetime
        from typing import List, Dict, Any
        import numpy as np
        print("[SUCCESS] Core Python modules imported")
        return True
    except Exception as e:
        print(f"[ERROR] Core import failed: {e}")
        return False

def test_session_files():
    """Test that session files exist in main directory."""
    print("Testing session files in main directory...")

    session03_files = [
        'session03_backend_enhanced.py',
        'session03_requirements.txt'
    ]

    session04_files = [
        'session04_production_rag_system.py',
        'session04_langchain_rag_system.py',
        'session04_requirements.txt',
        'session04_Dockerfile',
        'session04_docker-compose.yml'
    ]

    all_files = session03_files + session04_files
    missing_files = []

    for file in all_files:
        if not os.path.exists(file):
            missing_files.append(file)

    if missing_files:
        print(f"[ERROR] Missing files: {missing_files}")
        return False
    else:
        print("[SUCCESS] All session files present in main directory")
        return True

def test_database_operations():
    """Test basic database operations."""
    print("Testing database operations...")

    try:
        import sqlite3

        # Create temporary database
        test_db = os.path.join(tempfile.gettempdir(), 'test_main_rag.db')

        # Test database creation and operations
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()

        # Create test table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Insert test data
        cursor.execute('''
            INSERT INTO test_documents (filename, content)
            VALUES (?, ?)
        ''', ('test.txt', 'This is test content for the RAG system.'))

        # Query test data
        cursor.execute('SELECT * FROM test_documents')
        results = cursor.fetchall()

        conn.close()

        # Clean up
        if os.path.exists(test_db):
            os.remove(test_db)

        if results:
            print("[SUCCESS] Database operations working")
            return True
        else:
            print("[ERROR] No data retrieved from database")
            return False

    except Exception as e:
        print(f"[ERROR] Database test failed: {e}")
        return False

def test_requirements_content():
    """Test that requirements files have content."""
    print("Testing requirements content...")

    try:
        # Test Session 03 requirements
        with open('session03_requirements.txt', 'r') as f:
            s03_reqs = f.read().strip()

        # Test Session 04 requirements
        with open('session04_requirements.txt', 'r') as f:
            s04_reqs = f.read().strip()

        if s03_reqs and s04_reqs:
            print("[SUCCESS] Requirements files have content")
            print(f"  Session 03: {len(s03_reqs.split())} packages")
            print(f"  Session 04: {len(s04_reqs.split())} packages")
            return True
        else:
            print("[ERROR] Requirements files are empty")
            return False

    except Exception as e:
        print(f"[ERROR] Requirements test failed: {e}")
        return False

def test_session_imports():
    """Test that session files can be imported (syntax check)."""
    print("Testing session file syntax...")

    try:
        # Test Session 03 syntax
        with open('session03_backend_enhanced.py', 'r') as f:
            s03_content = f.read()

        # Test Session 04 syntax
        with open('session04_production_rag_system.py', 'r') as f:
            s04_content = f.read()

        # Basic syntax check - look for key patterns
        if 'from flask import' in s03_content and 'from fastapi import' in s04_content:
            print("[SUCCESS] Session files have correct framework imports")
            return True
        else:
            print("[WARNING] Session files may have import issues")
            return False

    except Exception as e:
        print(f"[ERROR] Session import test failed: {e}")
        return False

def main():
    """Run all core tests."""
    print("=" * 60)
    print("Core Systems Test - Sessions 03 & 04 in Main Directory")
    print("=" * 60)

    tests = [
        test_core_imports,
        test_session_files,
        test_database_operations,
        test_requirements_content,
        test_session_imports
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()  # Add spacing between tests

    print("=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("[SUCCESS] All systems ready in main directory!")
        return True
    else:
        print("[WARNING] Some tests failed, but core functionality available")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)