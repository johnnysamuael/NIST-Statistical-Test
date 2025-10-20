#!/usr/bin/env python3
"""
Installation Verification Script
Checks that all components are properly installed and working.
"""

import sys
import importlib


def check_python_version():
    """Check Python version."""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"  ✗ Python {version.major}.{version.minor}.{version.micro} (Need 3.8+)")
        return False


def check_dependencies():
    """Check required dependencies."""
    print("\nChecking dependencies...")
    
    dependencies = [
        ('streamlit', '1.29.0'),
        ('pandas', '2.1.4'),
        ('numpy', '1.26.2'),
        ('scipy', '1.11.4')
    ]
    
    all_ok = True
    for package, expected_version in dependencies:
        try:
            module = importlib.import_module(package)
            version = getattr(module, '__version__', 'unknown')
            print(f"  ✓ {package:15} {version:12} (expected: {expected_version})")
        except ImportError:
            print(f"  ✗ {package:15} NOT FOUND (need version {expected_version})")
            all_ok = False
    
    return all_ok


def check_modules():
    """Check custom modules."""
    print("\nChecking custom modules...")
    
    modules = [
        'code_converter',
        'nist_tests',
        'app',
        'batch_analysis',
        'generate_test_data',
        'test_converter'
    ]
    
    all_ok = True
    for module_name in modules:
        try:
            importlib.import_module(module_name)
            print(f"  ✓ {module_name}.py")
        except ImportError as e:
            print(f"  ✗ {module_name}.py - Error: {e}")
            all_ok = False
        except Exception as e:
            print(f"  ⚠ {module_name}.py - Warning: {e}")
    
    return all_ok


def check_files():
    """Check required files."""
    print("\nChecking required files...")
    
    import os
    
    files = [
        'app.py',
        'code_converter.py',
        'nist_tests.py',
        'batch_analysis.py',
        'generate_test_data.py',
        'test_converter.py',
        'requirements.txt',
        'README.md',
        'QUICKSTART.md',
        'USAGE_EXAMPLES.md',
        'sample_codes.csv'
    ]
    
    all_ok = True
    for filename in files:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"  ✓ {filename:25} ({size:,} bytes)")
        else:
            print(f"  ✗ {filename:25} NOT FOUND")
            all_ok = False
    
    return all_ok


def test_functionality():
    """Test basic functionality."""
    print("\nTesting functionality...")
    
    try:
        from code_converter import CodeConverter
        from nist_tests import NistTests
        import numpy as np
        
        # Test code converter
        print("  Testing code converter...")
        converter = CodeConverter()
        test_code = "ABCDEF2345"
        binary = converter.code_to_binary(test_code)
        back = converter.binary_to_code(binary)
        
        if back == test_code:
            print(f"    ✓ Conversion: {test_code} → {binary[:20]}... → {back}")
        else:
            print(f"    ✗ Conversion failed: {test_code} != {back}")
            return False
        
        # Test NIST tests
        print("  Testing NIST tests...")
        nist = NistTests()
        bits = np.array([int(b) for b in binary])
        
        p_value, passed = nist.frequency_test(bits)
        print(f"    ✓ Frequency test: p={p_value:.6f}, passed={passed}")
        
        p_value, passed = nist.runs_test(bits)
        print(f"    ✓ Runs test: p={p_value:.6f}, passed={passed}")
        
        print("  ✓ All functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"  ✗ Functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all checks."""
    print("=" * 60)
    print("NIST Statistical Tests - Installation Verification")
    print("=" * 60)
    
    results = {
        'Python Version': check_python_version(),
        'Dependencies': check_dependencies(),
        'Modules': check_modules(),
        'Files': check_files(),
        'Functionality': test_functionality()
    }
    
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for check, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{check:20} {status}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✓ All checks passed! The application is ready to use.")
        print("\nNext steps:")
        print("  1. Run: streamlit run app.py")
        print("  2. Or: python3 batch_analysis.py sample_codes.csv")
        print("  3. See QUICKSTART.md for more information")
    else:
        print("\n✗ Some checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  - Install dependencies: pip install -r requirements.txt")
        print("  - Check Python version: python3 --version")
        print("  - Ensure all files are in the same directory")
    
    print()
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())

