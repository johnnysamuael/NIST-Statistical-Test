"""
Test script for code converter and NIST tests.
Run this to verify the installation and functionality.
"""

from code_converter import CodeConverter
from nist_tests import NistTests


def test_code_converter():
    """Test the code converter."""
    print("Testing Code Converter...")
    print("=" * 60)
    
    converter = CodeConverter()
    
    # Test valid codes
    test_codes = [
        "ABCDEF2345",
        "XYZ789GHJK",
        "2222222222",
        "ZZZZZZZZZ",
        "MNPQRSTUVW"
    ]
    
    for code in test_codes:
        try:
            binary = converter.code_to_binary(code)
            print(f"Code: {code}")
            print(f"  Binary: {binary}")
            print(f"  Length: {len(binary)} bits")
            
            # Convert back to verify
            converted_back = converter.binary_to_code(binary)
            print(f"  Converted back: {converted_back}")
            print(f"  Match: {'✓' if converted_back == code else '✗'}")
            print()
        except Exception as e:
            print(f"Error with code {code}: {e}")
            print()
    
    # Test invalid codes
    print("Testing invalid codes (should fail)...")
    invalid_codes = ["ABC0123", "INVALID", "TEST0", "CODE1"]
    for code in invalid_codes:
        try:
            binary = converter.code_to_binary(code)
            print(f"Code {code}: Unexpectedly succeeded!")
        except ValueError as e:
            print(f"Code {code}: Correctly rejected - {e}")
    
    print("\n" + "=" * 60)
    print("Code Converter Tests Complete!\n")


def test_nist_tests():
    """Test NIST statistical tests."""
    print("Testing NIST Statistical Tests...")
    print("=" * 60)
    
    converter = CodeConverter()
    nist = NistTests()
    
    # Test with a sample code
    test_code = "ABCDEF2345"
    print(f"Testing code: {test_code}")
    print()
    
    binary = converter.code_to_binary(test_code)
    print(f"Binary sequence: {binary}")
    print(f"Length: {len(binary)} bits")
    print()
    
    # Run all tests
    results = nist.run_all_tests(binary, test_code)
    
    # Display results
    print("Test Results:")
    print("-" * 60)
    
    test_names = [
        ("Frequency (Monobit)", "frequency"),
        ("Block Frequency", "block_frequency"),
        ("Runs Test", "runs"),
        ("Longest Run of Ones", "longest_run"),
        ("Serial Test", "serial"),
        ("Approximate Entropy", "approximate_entropy"),
        ("Spectral (DFT)", "spectral"),
        ("Poker Test", "poker"),
        ("Overlapping Patterns", "overlapping_patterns")
    ]
    
    for test_name, key in test_names:
        pvalue = results[f"{key}_pvalue"]
        passed = results[f"{key}_passed"]
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name:.<35} {status} (p={pvalue:.6f})")
    
    print("-" * 60)
    overall = "✓ PASSED ALL TESTS" if results['overall_passed'] else "✗ FAILED SOME TESTS"
    print(f"Overall Result: {overall}")
    
    print("\n" + "=" * 60)
    print("NIST Tests Complete!\n")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("NIST Statistical Tests - System Verification")
    print("=" * 60 + "\n")
    
    try:
        test_code_converter()
        test_nist_tests()
        
        print("=" * 60)
        print("✓ All tests completed successfully!")
        print("=" * 60)
        print("\nYou can now run the main application:")
        print("  streamlit run app.py")
        print()
        
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

