import streamlit as st
import pandas as pd
import numpy as np
from io import StringIO
import csv
from nist_tests import NistTests
from multiprocessing import Pool, cpu_count, get_context
from batch_analysis import analyze_one, _init_worker
from code_converter import CodeConverter
import time
from io import BytesIO

st.set_page_config(page_title="NIST Statistical Tests", layout="wide")

st.title("NIST Statistical Tests for Code Randomness")
st.markdown("""
This application performs comprehensive NIST statistical tests on codes from CSV files.
Upload a CSV file with unique codes (separated by commas) and analyze their randomness properties.
""")

# Sidebar for configuration
st.sidebar.header("Configuration")
uploaded_file = st.sidebar.file_uploader("Upload CSV File", type=['csv'])
code_length = st.sidebar.number_input(
    "Number of digits per code", 
    min_value=1, 
    max_value=100, 
    value=10,
    help="Specify the expected length of each code"
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
### NIST Tests Performed:
1. Frequency (Monobit) Test
2. Block Frequency Test
3. Runs Test
4. Longest Run of Ones Test
5. Serial Test
6. Approximate Entropy Test
7. Spectral (DFT) Test
8. Poker Test (Chi-Square)
9. Overlapping Patterns Test
10. Overall Randomness Assessment
""")

# Performance settings
st.sidebar.subheader("Performance")
proc_default = max(1, cpu_count() // 2)
processes = st.sidebar.number_input(
    "Processes",
    min_value=1,
    max_value=max(1, cpu_count()),
    value=proc_default,
    help="Number of parallel worker processes"
)
chunksize = st.sidebar.number_input(
    "Chunksize",
    min_value=1,
    max_value=10000,
    value=500,
    help="Work items per process chunk for scheduling"
)
limit = st.sidebar.number_input(
    "Limit (optional)",
    min_value=0,
    max_value=10000000,
    value=0,
    help="Analyze only first N codes (0 = no limit)"
)

# Main content area
if uploaded_file is not None:
    st.success(f"File uploaded: {uploaded_file.name}")
    
    # Read and parse CSV
    content = uploaded_file.read().decode('utf-8')
    
    # Parse codes from CSV (handling comma-separated values)
    codes = []
    csv_reader = csv.reader(StringIO(content))
    for row in csv_reader:
        codes.extend([code.strip() for code in row if code.strip()])
    
    st.info(f"Total codes loaded: {len(codes):,}")
    
    # Display sample codes
    with st.expander("View Sample Codes (first 20)"):
        st.write(codes[:20])
    
    # Analyze button
    if st.button("🔍 Analyze Codes", type="primary"):
        st.markdown("---")
        st.header("Analysis Results")
        
        # Initialize converter and test suite
        converter = CodeConverter()
        nist_tests = NistTests()
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Store results
        all_results = []
        
        start_time = time.time()
        total_codes = len(codes)
        
        # Apply optional limit
        if limit and limit > 0:
            codes = codes[:limit]
            total_codes = len(codes)

        # Parallel processing
        processed = 0
        update_every = max(1000, total_codes // 100) if total_codes > 1000 else 50
        status_text.text(f"Spawning {processes} workers (chunksize={chunksize})...")
        try:
            if processes > 1:
                # Use fork context on macOS for better behavior/perf in Streamlit
                try:
                    mp_ctx = get_context("fork")
                except Exception:
                    mp_ctx = None
                PoolClass = mp_ctx.Pool if mp_ctx is not None else Pool
                with PoolClass(processes=processes, initializer=_init_worker) as pool:
                    for res in pool.imap_unordered(analyze_one, codes, chunksize=chunksize):
                        all_results.append(res)
                        processed += 1
                        if processed % update_every == 0 or processed == total_codes:
                            progress_bar.progress(processed / total_codes)
                            status_text.text(f"Processed {processed:,} / {total_codes:,}")
            else:
                # Fallback sequential
                for code in codes:
                    res = analyze_one(code)
                    all_results.append(res)
                    processed += 1
                    if processed % update_every == 0 or processed == total_codes:
                        progress_bar.progress(processed / total_codes)
                        status_text.text(f"Processed {processed:,} / {total_codes:,}")
        except Exception as e:
            st.error(f"Parallel processing error: {e}")
        
        elapsed_time = time.time() - start_time
        status_text.text(f"✅ Analysis complete! Processed {len(all_results):,} codes in {elapsed_time:.2f} seconds")
        
        # Display results
        if all_results:
            st.markdown("---")
            st.subheader("Statistical Summary")
            
            # Create results dataframe
            df_results = pd.DataFrame(all_results)
            
            # Display summary statistics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Codes Analyzed", f"{len(all_results):,}")
            with col2:
                passed_codes = df_results['overall_passed'].sum()
                st.metric("Codes Passed All Tests", f"{passed_codes:,}")
            with col3:
                pass_rate = (passed_codes / len(all_results)) * 100
                st.metric("Overall Pass Rate", f"{pass_rate:.2f}%")

            # Optional: overall average monobit entropy
            if 'monobit_entropy' in df_results.columns:
                st.metric("Avg Monobit Entropy", f"{df_results['monobit_entropy'].mean():.3f}")
            
            # Test-by-test results
            st.markdown("---")
            st.subheader("Test-by-Test Results")
            
            test_columns = [col for col in df_results.columns if col.endswith('_passed')]
            test_names = [col.replace('_passed', '').replace('_', ' ').title() for col in test_columns]
            
            test_summary = []
            alpha = nist_tests.alpha
            for test_col, test_name in zip(test_columns, test_names):
                passed = df_results[test_col].sum()
                total = len(df_results)
                pass_rate = (passed / total) * 100
                base = test_col[:-7]
                pval_col = f"{base}_pvalue"
                avg_p = None
                if pval_col in df_results.columns:
                    avg_p = float(df_results[pval_col].mean())
                test_summary.append({
                    'Test Name': test_name,
                    'Passed': int(passed),
                    'Failed': int(total - passed),
                    'Pass Rate (%)': f"{pass_rate:.2f}%",
                    'Avg p-value': (f"{avg_p:.6f}" if avg_p is not None else None),
                    'Avg>=α': (avg_p is not None and avg_p >= alpha)
                })
            
            df_test_summary = pd.DataFrame(test_summary)
            st.dataframe(df_test_summary, use_container_width=True)
            
            # Detailed results table
            st.markdown("---")
            st.subheader("Detailed Results")
            
            # Show expandable detailed view
            with st.expander("View All Test Results (Click to expand)"):
                st.dataframe(df_results, use_container_width=True)
            
            # Download results
            st.markdown("---")
            st.subheader("Export Results")
            
            csv_export = df_results.to_csv(index=False)
            st.download_button(
                label="📥 Download Results as CSV",
                data=csv_export,
                file_name=f"nist_test_results_{int(time.time())}.csv",
                mime="text/csv"
            )

            # PDF summary export
            try:
                from reportlab.lib.pagesizes import A4
                from reportlab.pdfgen import canvas
                from reportlab.lib.units import cm
                from reportlab.lib import colors

                def build_summary_pdf():
                    buffer = BytesIO()
                    c = canvas.Canvas(buffer, pagesize=A4)
                    width, height = A4
                    x_margin = 2*cm
                    y = height - 2*cm

                    def line(txt, size=12, color=colors.black):
                        nonlocal y
                        c.setFont("Helvetica", size)
                        c.setFillColor(color)
                        c.drawString(x_margin, y, txt)
                        y -= 0.8*cm

                    # Header
                    line("NIST Statistical Tests - Summary", 16)
                    line("")
                    line(f"Total Codes Analyzed: {len(all_results):,}")
                    line(f"Codes Passed All Tests: {int(passed_codes):,}")
                    line(f"Overall Pass Rate: {pass_rate:.2f}%")
                    if 'monobit_entropy' in df_results.columns:
                        line(f"Avg Monobit Entropy: {df_results['monobit_entropy'].mean():.3f}")
                    line("")
                    line("Test-by-Test Results:", 14)

                    # Table-like listing
                    for row in test_summary:
                        name = row['Test Name']
                        passed = row['Passed']
                        failed = row['Failed']
                        pr = row['Pass Rate (%)']
                        avgp = row.get('Avg p-value')
                        avga = row.get('Avg>=α')
                        line(f"- {name}: Passed {passed:,} / Failed {failed:,} (Rate {pr})")
                        if avgp is not None:
                            line(f"  Avg p-value: {avgp}  Avg>=α: {avga}", 10, colors.grey)
                        if y < 3*cm:
                            c.showPage(); y = height - 2*cm

                    c.showPage()
                    c.save()
                    buffer.seek(0)
                    return buffer.getvalue()

                pdf_bytes = build_summary_pdf()
                st.download_button(
                    label="📄 Download Summary PDF",
                    data=pdf_bytes,
                    file_name=f"nist_summary_{int(time.time())}.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.info("Install reportlab to enable PDF export: pip install reportlab")
            
            # Failed codes analysis
            failed_codes = df_results[~df_results['overall_passed']]
            if len(failed_codes) > 0:
                st.markdown("---")
                st.subheader("⚠️ Failed Codes Analysis")
                st.write(f"Total codes that failed: {len(failed_codes):,}")
                
                with st.expander("View Failed Codes Details"):
                    st.dataframe(failed_codes, use_container_width=True)
        
        else:
            st.error("No codes were successfully analyzed. Please check your input file.")

else:
    st.info("👈 Please upload a CSV file to begin analysis")
    
    st.markdown("---")
    st.subheader("Sample CSV Format")
    st.code("""ABC123DEF,XYZ789GHJ,MNP456QRS
KLM789TUV,WXY234ZAB,CDE567FGH
""", language="csv")
    
    st.markdown("""
    ### Notes:
    - Codes can be on multiple lines
    - Codes should be separated by commas
    - The character set is base-32 with i, o, 0, and 1 omitted
    - Valid characters: 2-9, A-H, J-N, P-Z (case insensitive)
    """)

