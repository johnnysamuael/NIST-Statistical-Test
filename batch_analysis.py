"""
Batch Analysis Script
Demonstrates how to use the NIST testing modules programmatically.
Useful for automation or integration into other systems.
"""

import csv
import json
import argparse
from datetime import datetime
from multiprocessing import Pool, cpu_count
from functools import partial
from itertools import islice
from code_converter import CodeConverter
from nist_tests import NistTests
from io import BytesIO

# Globals for worker reuse to avoid per-task object construction overhead
_CONVERTER = None
_NIST = None


def _init_worker():
    global _CONVERTER, _NIST
    _CONVERTER = CodeConverter()
    _NIST = NistTests()


def iter_codes_from_csv(filename):
    """Yield codes from CSV file lazily (streaming)."""
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            for code in row:
                code = code.strip()
                if code:
                    yield code


def analyze_one(code):
    """Top-level worker to enable multiprocessing pickling."""
    global _CONVERTER, _NIST
    # Fallback if not initialized (sequential mode)
    converter_local = _CONVERTER or CodeConverter()
    nist_local = _NIST or NistTests()
    try:
        binary = converter_local.code_to_binary(code)
        return nist_local.run_all_tests(binary, code)
    except Exception as e:
        return {'code': code, 'error': str(e), 'overall_passed': False}


def analyze_codes(codes, output_format='json', processes=1, progress_every=10000, chunksize=500):
    """
    Analyze a list of codes using NIST tests.
    
    Args:
        codes: List of code strings
        output_format: 'json', 'csv', or 'summary'
    
    Returns:
        Results in the specified format
    """
    results = []

    total = len(codes) if hasattr(codes, '__len__') else None
    if processes and processes > 1:
        print(f"Analyzing with {processes} processes (chunksize={chunksize})...", flush=True)
        with Pool(processes=processes, initializer=_init_worker) as pool:
            for idx, res in enumerate(pool.imap_unordered(analyze_one, codes, chunksize=chunksize), 1):
                if isinstance(res, dict):
                    results.append(res)
                if progress_every and idx % progress_every == 0:
                    if total:
                        pct = 100 * idx / total
                        print(f"  Progress: {idx:,} / {total:,} ({pct:.1f}%)", flush=True)
                    else:
                        print(f"  Progress: {idx:,} processed...", flush=True)
    else:
        print("Analyzing sequentially...", flush=True)
        for idx, code in enumerate(codes, 1):
            res = analyze_one(code)
            results.append(res)
            if progress_every and idx % progress_every == 0:
                if total:
                    pct = 100 * idx / total
                    print(f"  Progress: {idx:,} / {total:,} ({pct:.1f}%)", flush=True)
                else:
                    print(f"  Progress: {idx:,} processed...", flush=True)

    print(f"✓ Analysis complete: {len(results):,} codes processed\n", flush=True)
    return format_results(results, output_format)


def format_results(results, output_format):
    """Format results in the specified format."""
    if output_format == 'json':
        return json.dumps(results, indent=2)
    
    elif output_format == 'csv':
        if not results:
            return ""
        
        # CSV format
        output = []
        headers = list(results[0].keys())
        output.append(','.join(headers))
        
        for result in results:
            row = [str(result[key]) for key in headers]
            output.append(','.join(row))
        
        return '\n'.join(output)
    
    elif output_format == 'summary':
        if not results:
            return "No results to summarize."
        
        # Summary format
        total = len(results)
        passed_overall = sum(1 for r in results if r['overall_passed'])
        
        summary = []
        summary.append("=" * 60)
        summary.append("NIST STATISTICAL TESTS - SUMMARY REPORT")
        summary.append("=" * 60)
        summary.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary.append(f"Total Codes Analyzed: {total:,}")
        summary.append(f"Codes Passed All Tests: {passed_overall:,}")
        summary.append(f"Overall Pass Rate: {100*passed_overall/total:.2f}%")
        summary.append("")
        summary.append("Test-by-Test Results:")
        summary.append("-" * 60)
        
        # Calculate per-test statistics
        test_pass_cols = [col for col in results[0].keys() if col.endswith('_passed')]
        test_names = [col.replace('_passed', '').replace('_', ' ').title() 
                     for col in test_pass_cols]
        alpha = NistTests().alpha
        
        for test_col, test_name in zip(test_pass_cols, test_names):
            base = test_col[:-7]  # strip '_passed'
            pval_col = f"{base}_pvalue"
            passed = sum(1 for r in results if r.get(test_col))
            pass_rate = 100 * passed / total
            avg_p = None
            try:
                pvals = [float(r[pval_col]) for r in results if pval_col in r and r[pval_col] is not None]
                if pvals:
                    avg_p = sum(pvals) / len(pvals)
            except Exception:
                avg_p = None
            if avg_p is not None:
                avg_pass = avg_p >= alpha
                summary.append(f"{test_name:.<35} {passed:>6,}/{total:<6,} ({pass_rate:>6.2f}%)  avg p={avg_p:>0.6f}  avg>=α:{str(avg_pass)}")
            else:
                summary.append(f"{test_name:.<35} {passed:>6,}/{total:<6,} ({pass_rate:>6.2f}%)")
        
        summary.append("=" * 60)
        
        return '\n'.join(summary)
    
    elif output_format == 'pdf':
        # Build a PDF summary similar to the Streamlit export
        if not results:
            # Return a small one-page PDF noting empty results
            try:
                from reportlab.lib.pagesizes import A4
                from reportlab.pdfgen import canvas
                buf = BytesIO()
                c = canvas.Canvas(buf, pagesize=A4)
                c.drawString(100, 800, "NIST Statistical Tests - Summary")
                c.drawString(100, 780, "No results to summarize.")
                c.showPage(); c.save(); buf.seek(0)
                return buf.getvalue()
            except Exception:
                # If reportlab is missing, return a text message
                return b"Install reportlab to generate PDF (pip install reportlab)"
        
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            from reportlab.lib.units import cm
            from reportlab.lib import colors
        except Exception:
            return b"Install reportlab to generate PDF (pip install reportlab)"

        total = len(results)
        passed_overall = sum(1 for r in results if r.get('overall_passed'))
        alpha = NistTests().alpha
        
        test_pass_cols = [col for col in results[0].keys() if col.endswith('_passed')]
        test_names = [col.replace('_passed', '').replace('_', ' ').title() for col in test_pass_cols]
        
        # Aggregate averages
        test_rows = []
        for test_col, test_name in zip(test_pass_cols, test_names):
            base = test_col[:-7]
            pval_col = f"{base}_pvalue"
            passed = sum(1 for r in results if r.get(test_col))
            pass_rate = 100 * passed / total
            pvals = [float(r[pval_col]) for r in results if pval_col in r and r[pval_col] is not None]
            avg_p = sum(pvals) / len(pvals) if pvals else None
            test_rows.append((test_name, passed, total - passed, pass_rate, avg_p, (avg_p is not None and avg_p >= alpha)))

        # Build PDF
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

        line("NIST Statistical Tests - Summary", 16)
        line("")
        line(f"Total Codes Analyzed: {total:,}")
        line(f"Codes Passed All Tests: {passed_overall:,}")
        line(f"Overall Pass Rate: {100*passed_overall/total:.2f}%")
        
        # Monobit entropy average if present
        try:
            ent_vals = [float(r['monobit_entropy']) for r in results if 'monobit_entropy' in r]
            if ent_vals:
                line(f"Avg Monobit Entropy: {sum(ent_vals)/len(ent_vals):.3f}")
        except Exception:
            pass
        
        line("")
        line("Test-by-Test Results:", 14)
        for name, passed, failed, pr, avgp, avga in test_rows:
            line(f"- {name}: Passed {passed:,} / Failed {failed:,} (Rate {pr:.2f}%)")
            if avgp is not None:
                line(f"  Avg p-value: {avgp:.6f}  Avg>=α: {avga}", 10, colors.grey)
            if y < 3*cm:
                c.showPage(); y = height - 2*cm

        c.showPage(); c.save(); buffer.seek(0)
        return buffer.getvalue()
    
    else:
        raise ValueError(f"Unknown output format: {output_format}")


def main():
    parser = argparse.ArgumentParser(
        description='Batch analyze codes using NIST statistical tests'
    )
    parser.add_argument(
        'input_file',
        help='Input CSV file containing codes'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file (defaults to stdout)'
    )
    parser.add_argument(
        '-f', '--format',
        choices=['json', 'csv', 'summary', 'pdf'],
        default='summary',
        help='Output format (default: summary)'
    )
    parser.add_argument(
        '-p', '--processes',
        type=int,
        default=max(1, cpu_count() // 2),
        help='Number of parallel worker processes (default: half of CPUs)'
    )
    parser.add_argument(
        '-l', '--limit',
        type=int,
        help='Optional limit on number of codes to analyze'
    )
    parser.add_argument(
        '--progress-every',
        type=int,
        default=10000,
        help='Print progress every N codes (default: 10000)'
    )
    parser.add_argument(
        '--chunksize',
        type=int,
        default=500,
        help='Work chunk size per process for scheduling (default: 500)'
    )
    
    args = parser.parse_args()
    
    # Stream codes lazily to reduce memory, optionally limit
    print(f"Reading codes from {args.input_file}...", flush=True)
    code_iter = iter_codes_from_csv(args.input_file)
    if args.limit:
        codes = list(islice(code_iter, args.limit))
        print(f"✓ Loaded {len(codes):,} codes (limited)\n", flush=True)
    else:
        # For multiprocessing with known length, we load into a list once.
        # This is a trade-off: memory vs ability to show percent progress.
        codes = list(code_iter)
        print(f"✓ Loaded {len(codes):,} codes\n", flush=True)

    # Analyze codes
    output = analyze_codes(
        codes,
        output_format=args.format,
        processes=max(1, args.processes),
        progress_every=args.progress_every,
        chunksize=max(1, args.chunksize),
    )
    
    # Save or print results
    if args.format == 'pdf':
        if not args.output:
            print("Please provide -o output.pdf for PDF format", flush=True)
        else:
            if isinstance(output, bytes):
                with open(args.output, 'wb') as f:
                    f.write(output)
            else:
                # Likely an error message bytes; write anyway
                mode = 'wb' if isinstance(output, (bytes, bytearray)) else 'w'
                with open(args.output, mode) as f:
                    f.write(output)
            print(f"✓ PDF summary saved to {args.output}", flush=True)
    else:
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"✓ Results saved to {args.output}")
        else:
            print(output)


if __name__ == '__main__':
    main()

