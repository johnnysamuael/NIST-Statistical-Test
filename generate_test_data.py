"""
Generate Test Data
Creates CSV files with random codes for testing the NIST application.
"""

import random
import csv
import argparse


class TestDataGenerator:
    """Generates random codes for testing."""
    
    def __init__(self):
        # Base-32 alphabet (without i, o, 0, 1)
        self.alphabet = "23456789ABCDEFGHJKMNPQRSTUVWXYZ"
    
    def generate_code(self, length):
        """Generate a random code of specified length."""
        return ''.join(random.choice(self.alphabet) for _ in range(length))
    
    def generate_codes(self, count, length):
        """Generate multiple unique codes."""
        codes = set()
        
        while len(codes) < count:
            code = self.generate_code(length)
            codes.add(code)
        
        return list(codes)
    
    def save_to_csv(self, codes, filename, codes_per_line=5):
        """Save codes to CSV file."""
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write codes in rows with specified number per line
            for i in range(0, len(codes), codes_per_line):
                row = codes[i:i + codes_per_line]
                writer.writerow(row)
        
        print(f"✓ Generated {len(codes)} codes and saved to {filename}")


def main():
    parser = argparse.ArgumentParser(
        description='Generate random test codes for NIST testing'
    )
    parser.add_argument(
        '-n', '--count',
        type=int,
        default=100,
        help='Number of codes to generate (default: 100)'
    )
    parser.add_argument(
        '-l', '--length',
        type=int,
        default=10,
        help='Length of each code (default: 10)'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='test_codes.csv',
        help='Output filename (default: test_codes.csv)'
    )
    parser.add_argument(
        '-p', '--per-line',
        type=int,
        default=5,
        help='Codes per line in CSV (default: 5)'
    )
    
    args = parser.parse_args()
    
    print(f"\nGenerating Test Data...")
    print(f"  Count: {args.count:,} codes")
    print(f"  Length: {args.length} characters per code")
    print(f"  Output: {args.output}")
    print()
    
    generator = TestDataGenerator()
    
    # Generate codes
    print("Generating codes...")
    codes = generator.generate_codes(args.count, args.length)
    
    # Save to file
    print("Saving to file...")
    generator.save_to_csv(codes, args.output, args.per_line)
    
    # Display sample
    print(f"\nSample codes (first 10):")
    for i, code in enumerate(codes[:10], 1):
        print(f"  {i:2d}. {code}")
    
    if len(codes) > 10:
        print(f"  ... and {len(codes) - 10:,} more")
    
    print(f"\n✓ Complete! You can now upload {args.output} to the application.\n")


if __name__ == '__main__':
    main()

