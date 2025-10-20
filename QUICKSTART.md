# Quick Start Guide

## Getting Started in 3 Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Test Installation (Optional but Recommended)
```bash
python3 test_converter.py
```

You should see output indicating all tests passed ✓

### 3. Run the Application
```bash
streamlit run app.py
```

Or if streamlit is not in your PATH:
```bash
python3 -m streamlit run app.py
```

The application will open automatically in your browser at `http://localhost:8501`

## Using the Application

1. **Upload a CSV File**
   - Click "Upload CSV File" in the left sidebar
   - Select your CSV file containing codes
   - Try `sample_codes.csv` for a quick test

2. **Configure Code Length**
   - Enter the number of digits per code
   - Default is 10 characters

3. **Analyze**
   - Click the "🔍 Analyze Codes" button
   - Wait for processing (progress bar will show status)

4. **View Results**
   - See overall statistics
   - Check test-by-test breakdown
   - Examine detailed results
   - Download results as CSV

## Sample CSV Format

Your CSV file should contain codes separated by commas:

```csv
ABCDEF2345,XYZ789GHJK,MNPQRS6789
TUVWXY2468,ABCDEFGHJK,PQRSTUVWXY
```

## Valid Characters

The system uses base-32 encoding with these characters:
- **Numbers**: `2 3 4 5 6 7 8 9` (0 and 1 are omitted)
- **Letters**: `A B C D E F G H J K L M N P Q R S T U V W X Y Z` (I and O are omitted)

**Valid**: `23456789ABCDEFGHJKLMNPQRSTUVWXYZ`  
**Omitted**: `i`, `o`, `0`, `1` (case insensitive)

## Example Commands

### Test with sample data:
```bash
# Run the application
streamlit run app.py

# In the browser:
# 1. Upload sample_codes.csv
# 2. Set code length to 10
# 3. Click Analyze
```

### Test converter only:
```bash
python3 -c "from code_converter import CodeConverter; c = CodeConverter(); print(c.code_to_binary('ABCDEF2345'))"
```

## Troubleshooting

### Issue: "streamlit: command not found"
**Solution**: Add to PATH or use:
```bash
python3 -m streamlit run app.py
```

### Issue: "Invalid character" error
**Solution**: Ensure codes only use valid characters (2-9, A-H, J-N, P-Z). No I, O, 0, or 1.

### Issue: "Module not found"
**Solution**: Reinstall dependencies:
```bash
pip install -r requirements.txt
```

## Performance Tips

- For millions of codes, expect processing time of several seconds to minutes
- Progress bar shows real-time status
- Consider processing in batches if memory is limited
- Results are streamed, so the UI remains responsive

## Next Steps

- Review the full [README.md](README.md) for detailed documentation
- Modify NIST test parameters in `nist_tests.py` if needed
- Adjust significance level (default α=0.01) for stricter/looser testing
- Export results for further analysis in Excel, Python, or R

## Support

If you encounter issues:
1. Check that all dependencies are installed
2. Verify your CSV format matches the example
3. Ensure codes use only valid characters
4. Run `test_converter.py` to diagnose issues

## File Structure

```
NISt/
├── app.py                  # Main Streamlit application
├── nist_tests.py          # NIST statistical tests implementation
├── code_converter.py      # Base-32 to binary converter
├── test_converter.py      # Test script
├── requirements.txt       # Python dependencies
├── sample_codes.csv       # Sample data for testing
├── README.md             # Full documentation
└── QUICKSTART.md         # This file
```

---

**Ready to analyze your codes? Run `streamlit run app.py` and get started!**

