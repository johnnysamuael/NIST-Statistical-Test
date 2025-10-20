# Usage Examples

This document provides practical examples of using the NIST Statistical Tests application.

## Table of Contents

1. [Web Interface (Streamlit)](#web-interface-streamlit)
2. [Command Line Batch Processing](#command-line-batch-processing)
3. [Programmatic Usage](#programmatic-usage)
4. [Generating Test Data](#generating-test-data)
5. [Advanced Configurations](#advanced-configurations)

---

## Web Interface (Streamlit)

### Basic Usage

1. **Start the application:**
   ```bash
   streamlit run app.py
   ```

2. **Open in browser:**
   - Usually auto-opens at `http://localhost:8501`

3. **Upload and analyze:**
   - Upload your CSV file
   - Set code length
   - Click "Analyze"
   - Download results

### Example Session

```bash
# Start the app
cd /Users/johnnysamuael/Documents/NISt
streamlit run app.py

# In browser:
# 1. Upload sample_codes.csv
# 2. Set code length: 10
# 3. Click "🔍 Analyze Codes"
# 4. Review results
# 5. Download CSV if needed
```

---

## Command Line Batch Processing

### Basic Batch Analysis

```bash
# Analyze codes and print summary
python3 batch_analysis.py sample_codes.csv

# Save results to file
python3 batch_analysis.py sample_codes.csv -o results.txt

# Generate CSV output
python3 batch_analysis.py sample_codes.csv -f csv -o results.csv

# Generate JSON output
python3 batch_analysis.py sample_codes.csv -f json -o results.json
```

### Large Dataset Processing

```bash
# For large files (millions of codes)
python3 batch_analysis.py large_dataset.csv -f summary -o summary.txt

# CSV output for further analysis in Excel/Python
python3 batch_analysis.py large_dataset.csv -f csv -o detailed_results.csv
```

---

## Programmatic Usage

### Basic Code Conversion

```python
from code_converter import CodeConverter

# Initialize converter
converter = CodeConverter()

# Convert code to binary
code = "ABCDEF2345"
binary = converter.code_to_binary(code)
print(f"Code: {code}")
print(f"Binary: {binary}")
print(f"Length: {len(binary)} bits")

# Convert back
original = converter.binary_to_code(binary)
print(f"Converted back: {original}")
```

### Running NIST Tests

```python
from code_converter import CodeConverter
from nist_tests import NistTests

# Setup
converter = CodeConverter()
nist = NistTests()

# Analyze a code
code = "ABCDEF2345"
binary = converter.code_to_binary(code)
results = nist.run_all_tests(binary, code)

# Check results
print(f"Code: {code}")
print(f"Overall passed: {results['overall_passed']}")
print(f"Frequency test: {results['frequency_passed']}")
print(f"Runs test: {results['runs_passed']}")
```

### Batch Processing Multiple Codes

```python
from code_converter import CodeConverter
from nist_tests import NistTests
import csv

# Initialize
converter = CodeConverter()
nist = NistTests()

# Load codes from CSV
codes = []
with open('sample_codes.csv', 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        codes.extend([c.strip() for c in row if c.strip()])

# Process each code
results = []
for code in codes:
    try:
        binary = converter.code_to_binary(code)
        result = nist.run_all_tests(binary, code)
        results.append(result)
    except Exception as e:
        print(f"Error with {code}: {e}")

# Summary statistics
total = len(results)
passed = sum(1 for r in results if r['overall_passed'])
print(f"Total: {total}, Passed: {passed}, Rate: {100*passed/total:.1f}%")
```

### Custom Significance Level

```python
from nist_tests import NistTests

# Use stricter significance level (α = 0.001)
nist_strict = NistTests(significance_level=0.001)

# Use looser significance level (α = 0.05)
nist_loose = NistTests(significance_level=0.05)

# Run tests with custom level
binary = "010101010101010101010101"
results = nist_strict.run_all_tests(binary, "test_code")
```

### Individual Test Execution

```python
from nist_tests import NistTests
import numpy as np

nist = NistTests()

# Prepare binary sequence
bits = np.array([0,1,0,1,0,1,0,1,0,1,0,1])

# Run individual tests
p_freq, passed_freq = nist.frequency_test(bits)
print(f"Frequency test: p={p_freq:.6f}, passed={passed_freq}")

p_runs, passed_runs = nist.runs_test(bits)
print(f"Runs test: p={p_runs:.6f}, passed={passed_runs}")

p_spectral, passed_spectral = nist.spectral_test(bits)
print(f"Spectral test: p={p_spectral:.6f}, passed={passed_spectral}")
```

---

## Generating Test Data

### Small Test Dataset

```bash
# Generate 100 codes of length 10
python3 generate_test_data.py -n 100 -l 10 -o test_100.csv
```

### Large Test Dataset

```bash
# Generate 10,000 codes of length 15
python3 generate_test_data.py -n 10000 -l 15 -o test_10k.csv

# Generate 1 million codes (this will take a while)
python3 generate_test_data.py -n 1000000 -l 12 -o test_1m.csv
```

### Custom Format

```bash
# 1 code per line
python3 generate_test_data.py -n 50 -l 8 -o test.csv -p 1

# 10 codes per line
python3 generate_test_data.py -n 1000 -l 10 -o test.csv -p 10
```

### Generate and Analyze

```bash
# Generate test data
python3 generate_test_data.py -n 500 -l 12 -o test_codes.csv

# Analyze it
python3 batch_analysis.py test_codes.csv -f summary

# Or use web interface
streamlit run app.py
# Then upload test_codes.csv
```

---

## Advanced Configurations

### Performance Tuning for Large Datasets

When processing millions of codes, consider these strategies:

#### 1. Split Large Files

```bash
# Split CSV into chunks
split -l 10000 large_file.csv chunk_

# Process each chunk
for file in chunk_*; do
    python3 batch_analysis.py "$file" -f csv -o "results_$file.csv"
done
```

#### 2. Parallel Processing

```python
from multiprocessing import Pool
from code_converter import CodeConverter
from nist_tests import NistTests

def analyze_code(code):
    converter = CodeConverter()
    nist = NistTests()
    binary = converter.code_to_binary(code)
    return nist.run_all_tests(binary, code)

# Load codes
codes = [...]  # your codes here

# Process in parallel
with Pool(processes=4) as pool:
    results = pool.map(analyze_code, codes)
```

#### 3. Memory-Efficient Processing

```python
import csv

# Process codes one at a time (memory efficient)
def process_large_file(input_file, output_file):
    converter = CodeConverter()
    nist = NistTests()
    
    with open(input_file, 'r') as infile, \
         open(output_file, 'w', newline='') as outfile:
        
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        
        # Write header
        writer.writerow(['code', 'overall_passed', ...])
        
        for row in reader:
            for code in row:
                if code.strip():
                    binary = converter.code_to_binary(code.strip())
                    result = nist.run_all_tests(binary, code)
                    writer.writerow([result[k] for k in result.keys()])

# Use it
process_large_file('huge_file.csv', 'results.csv')
```

### Custom Test Parameters

Modify test parameters in `nist_tests.py`:

```python
# In nist_tests.py, modify methods:

# Custom block size for block frequency test
def block_frequency_test(self, bits, block_size=32):  # default was 20
    # ...

# Custom pattern length for overlapping patterns
def overlapping_patterns_test(self, bits, pattern_length=5):  # default was 9
    # ...
```

### Validation and Error Handling

```python
from code_converter import CodeConverter

converter = CodeConverter()

# Validate before processing
codes = ["ABCDEF2345", "INVALID0", "XYZ789"]
valid_codes = []

for code in codes:
    if converter.validate_code(code):
        valid_codes.append(code)
        print(f"✓ {code} is valid")
    else:
        print(f"✗ {code} is invalid")

# Process only valid codes
for code in valid_codes:
    binary = converter.code_to_binary(code)
    # ... process
```

### Export Results to Different Formats

```python
import json
import pandas as pd

# Collect results
results = [...]  # your results from NIST tests

# Export as JSON
with open('results.json', 'w') as f:
    json.dump(results, f, indent=2)

# Export as DataFrame (for analysis)
df = pd.DataFrame(results)

# Save to various formats
df.to_csv('results.csv', index=False)
df.to_excel('results.xlsx', index=False)
df.to_html('results.html', index=False)

# Quick statistics
print(df.describe())
print(df['overall_passed'].value_counts())
```

---

## Complete Workflow Example

Here's a complete example workflow:

```bash
# 1. Generate test data
python3 generate_test_data.py -n 1000 -l 12 -o my_codes.csv

# 2. Quick test with a few codes
head -5 my_codes.csv > sample.csv
python3 batch_analysis.py sample.csv

# 3. Full batch analysis
python3 batch_analysis.py my_codes.csv -f csv -o detailed.csv

# 4. View summary
python3 batch_analysis.py my_codes.csv -f summary

# 5. Interactive analysis (if needed)
streamlit run app.py
# Upload my_codes.csv in browser

# 6. Clean up
rm sample.csv my_codes.csv detailed.csv
```

---

## Tips and Best Practices

1. **Start Small**: Test with sample_codes.csv first
2. **Validate Input**: Ensure codes use only valid characters
3. **Monitor Memory**: For millions of codes, use batch processing
4. **Save Results**: Always save results for large analyses
5. **Check P-Values**: Lower p-values indicate potential non-randomness
6. **Significance Level**: Default α=0.01 is standard, adjust if needed
7. **Test Parameters**: Default parameters work well for most cases
8. **Performance**: Expect ~100-1000 codes/second depending on code length

---

## Troubleshooting Common Issues

### Issue: Slow Performance
```bash
# Solution: Use batch processing or parallel processing
# Process in chunks of 10,000 codes
python3 batch_analysis.py codes.csv -f csv -o results.csv
```

### Issue: Memory Error
```bash
# Solution: Process file in streaming mode
# Use the memory-efficient processing example above
```

### Issue: Invalid Characters
```python
# Solution: Pre-validate and clean codes
from code_converter import CodeConverter

converter = CodeConverter()
cleaned_codes = [c for c in codes if converter.validate_code(c)]
```

---

For more information, see [README.md](README.md) and [QUICKSTART.md](QUICKSTART.md).

