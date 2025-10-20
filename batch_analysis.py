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
    converter_local = CodeConverter()
    nist_local = NistTests()
    try:
        binary = converter_local.code_to_binary(code)
        return nist_local.run_all_tests(binary, code)
    except Exception as e:
        return {'code': code, 'error': str(e), 'overall_passed': False}


def analyze_codes(codes, output_format='json', processes=1, progress_every=10000):
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
        print(f"Analyzing with {processes} processes...")
        with Pool(processes=processes) as pool:
            for idx, res in enumerate(pool.imap_unordered(analyze_one, codes, chunksize=100), 1):
                if isinstance(res, dict):
                    results.append(res)
                if progress_every and idx % progress_every == 0:
                    if total:
                        pct = 100 * idx / total
                        print(f"  Progress: {idx:,} / {total:,} ({pct:.1f}%)")
                    else:
                        print(f"  Progress: {idx:,} processed...")
    else:
        print("Analyzing sequentially...")
        for idx, code in enumerate(codes, 1):
            res = analyze_one(code)
            results.append(res)
            if progress_every and idx % progress_every == 0:
                if total:
                    pct = 100 * idx / total
                    print(f"  Progress: {idx:,} / {total:,} ({pct:.1f}%)")
                else:
                    print(f"  Progress: {idx:,} processed...")

    print(f"✓ Analysis complete: {len(results):,} codes processed\n")
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
        choices=['json', 'csv', 'summary'],
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
    
    args = parser.parse_args()
    
    # Stream codes lazily to reduce memory, optionally limit
    print(f"Reading codes from {args.input_file}...")
    code_iter = iter_codes_from_csv(args.input_file)
    if args.limit:
        codes = list(islice(code_iter, args.limit))
        print(f"✓ Loaded {len(codes):,} codes (limited)\n")
    else:
        # For multiprocessing with known length, we load into a list once.
        # This is a trade-off: memory vs ability to show percent progress.
        codes = list(code_iter)
        print(f"✓ Loaded {len(codes):,} codes\n")

    # Analyze codes
    output = analyze_codes(
        codes,
        output_format=args.format,
        processes=max(1, args.processes),
        progress_every=args.progress_every,
    )
    
    # Save or print results
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"✓ Results saved to {args.output}")
    else:
        print(output)


if __name__ == '__main__':
    main()

