# NIST Statistical Tests Application

A comprehensive Python application for performing NIST statistical tests on unique codes from CSV files. This tool analyzes the randomness properties of codes using industry-standard statistical tests.

## Features

- **CSV File Upload**: Upload files containing millions of comma-separated codes
- **Base-32 Encoding**: Supports codes with a 32-character set (i, o, 0, and 1 omitted)
- **Comprehensive NIST Tests**: Implements 9 different statistical tests
- **Batch Processing**: Efficiently handles large datasets with millions of codes
- **Visual Results**: Interactive dashboard with test summaries and downloadable results
- **Real-time Progress**: Track analysis progress for large datasets

## NIST Statistical Tests Implemented

1. **Frequency (Monobit) Test**: Tests the proportion of zeros and ones in the sequence
2. **Block Frequency Test**: Tests the proportion of ones within M-bit blocks
3. **Runs Test**: Tests the total number of runs (uninterrupted sequences)
4. **Longest Run of Ones Test**: Tests the longest run of ones within blocks
5. **Serial Test (Autocorrelation)**: Tests the frequency of overlapping m-bit patterns
6. **Approximate Entropy Test**: Tests the frequency of all possible overlapping patterns
7. **Spectral (DFT) Test**: Tests peak heights in the Discrete Fourier Transform
8. **Poker Test (Chi-Square)**: Tests the distribution of m-bit patterns
9. **Overlapping Patterns Test**: Tests occurrences of specific patterns

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone or download this repository
2. Navigate to the project directory:
   ```bash
   cd /Users/johnnysamuael/Documents/NISt
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the Application

1. Start the Streamlit application:
   ```bash
   streamlit run app.py
   ```

2. Open your web browser (should open automatically) to the URL shown in terminal (typically `http://localhost:8501`)

### Using the Application

1. **Upload CSV File**: 
   - Click "Upload CSV File" in the sidebar
   - Select your CSV file containing codes
   
2. **Configure Code Length**:
   - Enter the number of digits per code
   - Default is 10, adjust based on your codes
   
3. **Analyze**:
   - Click the "🔍 Analyze Codes" button
   - Wait for processing to complete
   
4. **View Results**:
   - Overall statistics (total codes, pass rate)
   - Test-by-test breakdown
   - Detailed results table
   - Failed codes analysis
   
5. **Export Results**:
   - Download results as CSV for further analysis

### CSV File Format

Codes should be separated by commas and can span multiple lines:

```csv
ABC123DEF,XYZ789GHJ,MNP456QRS
KLM789TUV,WXY234ZAB,CDE567FGH
```

### Valid Character Set

The application uses a base-32 encoding scheme with the following characters:
- **Numbers**: 2-9 (0 and 1 omitted)
- **Letters**: A-H, J-N, P-Z (I and O omitted)

This gives a total of 32 valid characters (2^5), allowing each character to be represented as 5 binary bits.

**Valid characters**: `23456789ABCDEFGHJKLMNPQRSTUVWXYZ`  
**Omitted characters**: `i`, `o`, `0`, `1` (case insensitive)

## Example Codes

Valid codes:
- `ABC123DEF`
- `XYZ789GHJ`
- `2468ACEG`
- `MNPQRSTU`
- `UJTNMTUHPBGUNCZV5XL`

Invalid codes (contain omitted characters):
- `ABC012DEF` (contains 0 and 1)
- `OPQRSTUV` (contains O)
- `INVALID123` (contains I)

## Output

The application provides several outputs:

### Statistical Summary
- Total codes analyzed
- Codes that passed all tests
- Overall pass rate percentage

### Test-by-Test Results
- Individual test pass/fail counts
- Pass rate for each test
- Comparison across all tests

### Detailed Results
- Per-code test results
- P-values for each test
- Overall pass/fail status

### Export Options
- Download complete results as CSV
- Timestamped filename for organization
- Includes all test metrics and p-values

## Performance

- Handles millions of codes efficiently
- Real-time progress tracking
- Optimized binary conversion
- Batch processing for large datasets

## Technical Details

### Architecture

- **app.py**: Main Streamlit web application
- **nist_tests.py**: NIST statistical test implementations
- **code_converter.py**: Base-32 to binary conversion

### Statistical Significance

Default significance level (α) = 0.01

A code passes a test if its p-value ≥ α (0.01)

### Binary Conversion

Each character in the base-32 alphabet maps to a 5-bit binary value:
- Character '2' → 00000
- Character '3' → 00001
- ...
- Character 'Z' → 11111

## Troubleshooting

### Common Issues

1. **"Invalid character" error**: 
   - Ensure all codes use only valid characters (2-9, A-H, J-N, P-Z)
   - Check for I, O, 0, or 1 in your codes

2. **Application won't start**:
   - Verify Python version (3.8+)
   - Reinstall dependencies: `pip install -r requirements.txt`

3. **Slow processing**:
   - Normal for millions of codes
   - Progress bar shows status
   - Consider processing in smaller batches

### Support

For issues or questions, please check:
- Code validation against character set
- CSV file format
- System requirements

## License

This application is provided as-is for statistical analysis purposes.

## References

- NIST Special Publication 800-22: A Statistical Test Suite for Random and Pseudorandom Number Generators for Cryptographic Applications
- Crockford Base32 Encoding Specification

