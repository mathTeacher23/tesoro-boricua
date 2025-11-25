#!/usr/bin/env python3
"""
Test script to verify the translation backend is working correctly.
Run this to diagnose translation issues.
"""

import sys

def test_imports():
    """Test if all required packages are installed."""
    print("Testing imports...")
    try:
        import fastapi
        print("  ✓ fastapi imported")
    except ImportError as e:
        print(f"  ✗ fastapi: {e}")
        return False

    try:
        import uvicorn
        print("  ✓ uvicorn imported")
    except ImportError as e:
        print(f"  ✗ uvicorn: {e}")
        return False

    try:
        import pydantic
        print("  ✓ pydantic imported")
    except ImportError as e:
        print(f"  ✗ pydantic: {e}")
        return False

    try:
        from translate import Translator
        print("  ✓ translate imported")
    except ImportError as e:
        print(f"  ✗ translate: {e}")
        return False

    return True

def test_translation():
    """Test if translation actually works."""
    print("\nTesting translation functionality...")
    try:
        from translate import Translator

        # Test English to Spanish
        translator = Translator(to_lang='es', from_lang='en')
        result = translator.translate('hello')
        print(f"  ✓ EN→ES: 'hello' → '{result}'")

        # Test Spanish to English
        translator = Translator(to_lang='en', from_lang='es')
        result = translator.translate('hola')
        print(f"  ✓ ES→EN: 'hola' → '{result}'")

        return True
    except Exception as e:
        print(f"  ✗ Translation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api():
    """Test if the API server can be imported."""
    print("\nTesting API server...")
    try:
        from backend_server import app
        print("  ✓ Backend server imported successfully")
        return True
    except Exception as e:
        print(f"  ✗ Backend server import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("╔════════════════════════════════════════════════════════════╗")
    print("║       Translation Backend Diagnostic Test                  ║")
    print("╚════════════════════════════════════════════════════════════╝\n")

    all_pass = True

    if not test_imports():
        print("\n✗ Some packages are missing!")
        print("  Run: pip install fastapi uvicorn pydantic translate")
        all_pass = False

    if not test_translation():
        print("\n✗ Translation library is not working correctly!")
        all_pass = False

    if not test_api():
        print("\n✗ Backend server has issues!")
        all_pass = False

    print("\n" + "╔════════════════════════════════════════════════════════════╗")
    if all_pass:
        print("║  ✓ All tests passed! Backend should work.                   ║")
        print("║  Try running: make start                                     ║")
    else:
        print("║  ✗ Some tests failed. See messages above.                   ║")
        print("║  Install missing dependencies and try again.                ║")
    print("╚════════════════════════════════════════════════════════════╝\n")

    return 0 if all_pass else 1

if __name__ == '__main__':
    sys.exit(main())
