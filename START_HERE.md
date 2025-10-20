# 🚀 START HERE - NIST Statistical Tests Application

Welcome! This guide will get you up and running in minutes.

## ⚡ Quick Start (3 Commands)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Verify installation (optional but recommended)
python3 verify_installation.py

# 3. Start the application
streamlit run app.py
```

**Or use the automated script:**
```bash
./start.sh
```

The application will open in your browser at `http://localhost:8501`

---

## 📋 What This Application Does

Analyzes codes from CSV files using **9 NIST statistical tests** to detect non-randomness:

✓ Frequency (Monobit) Test  
✓ Block Frequency Test  
✓ Runs Test  
✓ Longest Run of Ones Test  
✓ Serial Test  
✓ Approximate Entropy Test  
✓ Spectral (DFT) Test  
✓ Poker Test  
✓ Overlapping Patterns Test  

**Supports:** Millions of codes, Base-32 encoding (i, o, 0, 1 omitted)

---

## 🎯 Three Ways to Use

### 1️⃣ Web Interface (Easiest)
```bash
streamlit run app.py
```
- Upload CSV file
- Click "Analyze"
- View results
- Download report

### 2️⃣ Command Line (Automation)
```bash
# Summary report
python3 batch_analysis.py your_codes.csv

# Save as CSV
python3 batch_analysis.py your_codes.csv -f csv -o results.csv

# Save as JSON
python3 batch_analysis.py your_codes.csv -f json -o results.json
```

### 3️⃣ Python Code (Integration)
```python
from code_converter import CodeConverter
from nist_tests import NistTests

converter = CodeConverter()
nist = NistTests()

binary = converter.code_to_binary("ABCDEF2345")
results = nist.run_all_tests(binary, "ABCDEF2345")
print(results['overall_passed'])
```

---

## 📁 CSV File Format

Your CSV should contain codes separated by commas:

```csv
ABCDEF2345,XYZ789GHJK,MNPQRS6789
TUVWXY2468,PQRSTUVWXY,23456789AB
```

**Valid characters:** `2-9`, `A-H`, `J-N`, `P-Z` (32 chars, case-insensitive)  
**Omitted:** `i`, `o`, `0`, `1` (to avoid confusion)  
**Full set:** `23456789ABCDEFGHJKLMNPQRSTUVWXYZ`

---

## 🧪 Test It Out

### Option A: Use Sample Data
```bash
streamlit run app.py
# Upload: sample_codes.csv (included)
```

### Option B: Generate Test Data
```bash
# Generate 100 random codes
python3 generate_test_data.py -n 100 -l 10 -o my_test.csv

# Analyze them
python3 batch_analysis.py my_test.csv
```

---

## 📊 Understanding Results

### P-Values
- **p ≥ 0.01**: Code passes (appears random) ✅
- **p < 0.01**: Code fails (potential pattern) ❌

### Overall Pass
A code must pass **ALL 9 tests** to pass overall.

### Example Output
```
Frequency Test..................... ✓ PASSED (p=0.234567)
Runs Test.......................... ✓ PASSED (p=0.456789)
Spectral Test...................... ✗ FAILED (p=0.002345)
Overall............................ ✗ FAILED
```

---

## 🛠️ Troubleshooting

### "streamlit: command not found"
```bash
python3 -m streamlit run app.py
```

### "Invalid character" error
Check your codes use only: `2-9, A-H, J-N, P-Z`  
Remove: `i, o, 0, 1`

### Dependencies not installed
```bash
pip install -r requirements.txt
```

### Verify everything works
```bash
python3 verify_installation.py
```

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| `START_HERE.md` | **You are here** - Quick start |
| `QUICKSTART.md` | 3-step setup guide |
| `README.md` | Full documentation |
| `USAGE_EXAMPLES.md` | Detailed examples |
| `PROJECT_SUMMARY.md` | Technical overview |

---

## 🎬 Complete Example Workflow

```bash
# Step 1: Generate test data
python3 generate_test_data.py -n 1000 -l 12 -o codes.csv

# Step 2: Run quick analysis
python3 batch_analysis.py codes.csv

# Step 3: Full analysis with results
python3 batch_analysis.py codes.csv -f csv -o results.csv

# Step 4: Interactive exploration
streamlit run app.py
# Upload codes.csv, click Analyze, explore results
```

---

## ⚙️ System Requirements

- **Python**: 3.8 or higher
- **OS**: macOS, Linux, Windows
- **RAM**: 4GB minimum (8GB+ for millions of codes)
- **Disk**: ~100MB for installation

---

## 🔥 Performance

- **Speed**: ~100-1000 codes/second
- **Scalability**: Tested with millions of codes
- **Memory**: Efficient streaming support

---

## 🎯 Common Use Cases

### ✅ Validate Code Generator
Test if your code generation algorithm produces random-looking codes.

### ✅ Quality Assurance
Verify codes before deployment to customers.

### ✅ Research Analysis
Study statistical properties of different encodings.

### ✅ Compliance Testing
Ensure codes meet randomness requirements.

---

## 🚀 Next Steps

1. **Try it now**: Run `streamlit run app.py`
2. **Upload sample data**: Use `sample_codes.csv`
3. **Generate your own**: Use `generate_test_data.py`
4. **Read examples**: Check `USAGE_EXAMPLES.md`
5. **Integrate**: Use Python API in your code

---

## 📞 Need Help?

1. Run verification: `python3 verify_installation.py`
2. Check troubleshooting section above
3. Review full documentation in `README.md`
4. Examine code examples in `USAGE_EXAMPLES.md`

---

## ✨ Features at a Glance

✅ 9 NIST statistical tests  
✅ Base-32 code support  
✅ Web interface + CLI + Python API  
✅ Handles millions of codes  
✅ Real-time progress tracking  
✅ Export results (CSV/JSON)  
✅ Sample data included  
✅ Test data generator  
✅ Comprehensive documentation  
✅ Fully tested and verified  

---

**Ready? Let's go! 🎉**

```bash
streamlit run app.py
```

---

*For detailed documentation, see `README.md`*  
*For quick examples, see `QUICKSTART.md`*  
*For advanced usage, see `USAGE_EXAMPLES.md`*

