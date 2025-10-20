"""
NIST Statistical Tests Module
Implements various NIST statistical tests for randomness testing.
"""

import numpy as np
from scipy import special as sp
from scipy import fft
from collections import Counter
import math


class NistTests:
    """
    Implements NIST Statistical Test Suite for randomness testing.
    """
    
    def __init__(self, significance_level=0.01):
        """
        Initialize NIST Tests.
        
        Args:
            significance_level: Significance level for statistical tests (default: 0.01)
        """
        self.alpha = significance_level
    
    def run_all_tests(self, binary_sequence, code):
        """
        Run all NIST tests on a binary sequence.
        
        Args:
            binary_sequence: String of 0s and 1s
            code: Original code string (for reference)
            
        Returns:
            Dictionary with test results
        """
        results = {'code': code}
        
        # Convert to numpy array for easier processing
        bits = np.array([int(b) for b in binary_sequence])
        n = len(bits)
        
        # 0. Monobit entropy (binary entropy of proportion of ones)
        results['monobit_entropy'] = self.monobit_entropy(bits)

        # 1. Frequency (Monobit) Test
        p_value, passed = self.frequency_test(bits)
        results['frequency_pvalue'] = p_value
        results['frequency_passed'] = passed
        
        # 2. Block Frequency Test
        p_value, passed = self.block_frequency_test(bits)
        results['block_frequency_pvalue'] = p_value
        results['block_frequency_passed'] = passed
        
        # 3. Runs Test
        p_value, passed = self.runs_test(bits)
        results['runs_pvalue'] = p_value
        results['runs_passed'] = passed
        
        # 4. Longest Run of Ones Test
        p_value, passed = self.longest_run_of_ones_test(bits)
        results['longest_run_pvalue'] = p_value
        results['longest_run_passed'] = passed
        
        # 5. Serial Test
        p_value, passed = self.serial_test(bits)
        results['serial_pvalue'] = p_value
        results['serial_passed'] = passed
        
        # 6. Approximate Entropy Test
        p_value, passed = self.approximate_entropy_test(bits)
        results['approximate_entropy_pvalue'] = p_value
        results['approximate_entropy_passed'] = passed
        
        # 7. Spectral (DFT) Test
        p_value, passed = self.spectral_test(bits)
        results['spectral_pvalue'] = p_value
        results['spectral_passed'] = passed
        
        # 8. Poker Test (Chi-Square)
        p_value, passed = self.poker_test(bits)
        results['poker_pvalue'] = p_value
        results['poker_passed'] = passed
        
        # 9. Overlapping Patterns Test
        p_value, passed = self.overlapping_patterns_test(bits)
        results['overlapping_patterns_pvalue'] = p_value
        results['overlapping_patterns_passed'] = passed
        
        # Overall assessment
        results['overall_passed'] = all([
            results['frequency_passed'],
            results['block_frequency_passed'],
            results['runs_passed'],
            results['longest_run_passed'],
            results['serial_passed'],
            results['approximate_entropy_passed'],
            results['spectral_passed'],
            results['poker_passed'],
            results['overlapping_patterns_passed']
        ])
        
        return results

    def monobit_entropy(self, bits):
        """
        Monobit entropy (binary entropy) per sequence.
        H = -p*log2(p) - (1-p)*log2(1-p), where p is proportion of ones.
        Returns 0 when p in {0,1} to avoid log(0).
        """
        n = len(bits)
        if n == 0:
            return 0.0
        p = np.sum(bits) / n
        # handle edge cases explicitly
        if p <= 0.0 or p >= 1.0:
            return 0.0
        return float(-(p * math.log2(p) + (1.0 - p) * math.log2(1.0 - p)))
    
    def frequency_test(self, bits):
        """
        Frequency (Monobit) Test
        Tests the proportion of zeros and ones in the entire sequence.
        """
        n = len(bits)
        
        # Calculate the sum (convert 0s to -1s, 1s stay as 1s)
        s = np.sum(2 * bits - 1)
        
        # Calculate test statistic
        s_obs = abs(s) / np.sqrt(n)
        
        # Calculate p-value
        p_value = sp.erfc(s_obs / np.sqrt(2))
        
        return p_value, p_value >= self.alpha
    
    def block_frequency_test(self, bits, block_size=None):
        """
        Frequency Test within a Block
        Tests the proportion of ones within M-bit blocks.
        """
        n = len(bits)
        
        # Use default block size if not specified
        if block_size is None:
            block_size = min(20, max(1, n // 10))
        
        # Number of blocks
        num_blocks = n // block_size
        
        if num_blocks == 0:
            return 1.0, True
        
        # Calculate proportion of ones in each block
        proportions = []
        for i in range(num_blocks):
            block = bits[i * block_size:(i + 1) * block_size]
            proportion = np.sum(block) / block_size
            proportions.append(proportion)
        
        # Calculate chi-square statistic
        chi_square = 4 * block_size * np.sum((np.array(proportions) - 0.5) ** 2)
        
        # Calculate p-value
        p_value = sp.gammaincc(num_blocks / 2, chi_square / 2)
        
        return p_value, p_value >= self.alpha
    
    def runs_test(self, bits):
        """
        Runs Test
        Tests the total number of runs (uninterrupted sequence of identical bits).
        """
        n = len(bits)
        
        # Calculate proportion of ones
        pi = np.sum(bits) / n
        
        # Pre-test: check if proportion is approximately 0.5
        tau = 2 / np.sqrt(n)
        if abs(pi - 0.5) >= tau:
            return 0.0, False
        
        # Count runs
        runs = 1
        for i in range(1, n):
            if bits[i] != bits[i - 1]:
                runs += 1
        
        # Calculate test statistic
        p_value = sp.erfc(abs(runs - 2 * n * pi * (1 - pi)) / (2 * np.sqrt(2 * n) * pi * (1 - pi)))
        
        return p_value, p_value >= self.alpha
    
    def longest_run_of_ones_test(self, bits):
        """
        Longest Run of Ones Test
        Tests the longest run of ones within M-bit blocks.
        """
        n = len(bits)
        
        # Determine parameters based on sequence length
        if n < 128:
            return 1.0, True
        elif n < 6272:
            M = 8
            K = 3
            N = n // M
            v_values = [1, 2, 3, 4]
            pi_values = [0.2148, 0.3672, 0.2305, 0.1875]
        elif n < 750000:
            M = 128
            K = 5
            N = n // M
            v_values = [4, 5, 6, 7, 8, 9]
            pi_values = [0.1174, 0.2430, 0.2493, 0.1752, 0.1027, 0.1124]
        else:
            M = 10000
            K = 6
            N = n // M
            v_values = [10, 11, 12, 13, 14, 15, 16]
            pi_values = [0.0882, 0.2092, 0.2483, 0.1933, 0.1208, 0.0675, 0.0727]
        
        # Count longest runs in each block
        frequencies = [0] * len(v_values)
        
        for i in range(N):
            block = bits[i * M:(i + 1) * M]
            
            # Find longest run of ones
            max_run = 0
            current_run = 0
            
            for bit in block:
                if bit == 1:
                    current_run += 1
                    max_run = max(max_run, current_run)
                else:
                    current_run = 0
            
            # Categorize the run
            for j, v in enumerate(v_values):
                if j == 0 and max_run <= v:
                    frequencies[j] += 1
                    break
                elif j == len(v_values) - 1 and max_run >= v:
                    frequencies[j] += 1
                    break
                elif j < len(v_values) - 1 and v_values[j] < max_run <= v_values[j + 1]:
                    frequencies[j + 1] += 1
                    break
        
        # Calculate chi-square statistic
        chi_square = np.sum((np.array(frequencies) - N * np.array(pi_values)) ** 2 / (N * np.array(pi_values)))
        
        # Calculate p-value
        p_value = sp.gammaincc(K / 2, chi_square / 2)
        
        return p_value, p_value >= self.alpha
    
    def serial_test(self, bits, m=None):
        """
        Serial Test (Autocorrelation Test)
        Tests the frequency of overlapping m-bit patterns.
        """
        n = len(bits)
        
        # Use default pattern length if not specified
        if m is None:
            m = min(5, max(2, int(np.log2(n)) - 2))
        
        if n < 2 ** m:
            return 1.0, True
        
        # Calculate psi_m values
        def calculate_psi(bits, m):
            counts = Counter()
            for i in range(len(bits)):
                pattern = tuple(bits[i:i + m])
                if len(pattern) == m:
                    counts[pattern] += 1
            
            psi = sum(count ** 2 for count in counts.values())
            psi = (psi * (2 ** m) / n) - n
            return psi
        
        psi_m = calculate_psi(bits, m)
        psi_m_1 = calculate_psi(bits, m - 1)
        psi_m_2 = calculate_psi(bits, m - 2) if m > 2 else 0
        
        # Calculate delta values
        delta1 = psi_m - psi_m_1
        delta2 = psi_m - 2 * psi_m_1 + psi_m_2
        
        # Calculate p-values
        p_value1 = sp.gammaincc(2 ** (m - 2), delta1 / 2)
        p_value2 = sp.gammaincc(2 ** (m - 3), delta2 / 2) if m > 2 else 1.0
        
        # Use the minimum p-value
        p_value = min(p_value1, p_value2)
        
        return p_value, p_value >= self.alpha
    
    def approximate_entropy_test(self, bits, m=None):
        """
        Approximate Entropy Test
        Tests the frequency of all possible overlapping m-bit patterns.
        """
        n = len(bits)
        
        # Use default pattern length if not specified
        if m is None:
            m = min(5, max(2, int(np.log2(n)) - 2))
        
        if n < 2 ** m:
            return 1.0, True
        
        # Calculate phi(m)
        def calculate_phi(bits, m):
            # Create circular sequence
            augmented_bits = np.concatenate([bits, bits[:m - 1]])
            
            # Count patterns
            counts = Counter()
            for i in range(n):
                pattern = tuple(augmented_bits[i:i + m])
                counts[pattern] += 1
            
            # Calculate phi
            phi = sum((count / n) * np.log(count / n) for count in counts.values())
            return phi
        
        phi_m = calculate_phi(bits, m)
        phi_m_1 = calculate_phi(bits, m + 1)
        
        # Calculate ApEn
        apen = phi_m - phi_m_1
        
        # Calculate chi-square statistic
        chi_square = 2 * n * (np.log(2) - apen)
        
        # Calculate p-value
        p_value = sp.gammaincc(2 ** (m - 1), chi_square / 2)
        
        return p_value, p_value >= self.alpha
    
    def spectral_test(self, bits):
        """
        Spectral (DFT) Test
        Tests the peak heights in the Discrete Fourier Transform.
        """
        n = len(bits)
        
        # Convert bits to +1/-1
        x = 2 * bits - 1
        
        # Apply DFT
        s = fft.fft(x)
        
        # Calculate modulus of first half (excluding DC component)
        modulus = np.abs(s[:n // 2])
        
        # Calculate threshold
        tau = np.sqrt(np.log(1 / 0.05) * n)
        
        # Count peaks below threshold
        n0 = 0.95 * n / 2
        n1 = np.sum(modulus < tau)
        
        # Calculate test statistic
        d = (n1 - n0) / np.sqrt(n * 0.95 * 0.05 / 4)
        
        # Calculate p-value
        p_value = sp.erfc(abs(d) / np.sqrt(2))
        
        return p_value, p_value >= self.alpha
    
    def poker_test(self, bits, m=4):
        """
        Poker Test (Chi-Square over Blocks)
        Tests the distribution of m-bit patterns.
        """
        n = len(bits)
        
        # Number of blocks
        num_blocks = n // m
        
        if num_blocks < 5 * (2 ** m):
            return 1.0, True
        
        # Count occurrences of each pattern
        counts = Counter()
        for i in range(num_blocks):
            block = tuple(bits[i * m:(i + 1) * m])
            counts[block] += 1
        
        # Expected frequency
        expected = num_blocks / (2 ** m)
        
        # Calculate chi-square statistic
        chi_square = sum((count - expected) ** 2 / expected for count in counts.values())
        
        # Degrees of freedom
        df = (2 ** m) - 1
        
        # Calculate p-value
        p_value = sp.gammaincc(df / 2, chi_square / 2)
        
        return p_value, p_value >= self.alpha
    
    def overlapping_patterns_test(self, bits, pattern_length=9):
        """
        Overlapping Patterns Test
        Tests the number of occurrences of a specific pattern.
        """
        n = len(bits)
        
        # Use a specific pattern (all ones)
        pattern = np.ones(pattern_length, dtype=int)
        
        if n < pattern_length:
            return 1.0, True
        
        # Block size
        M = max(1000, n // 100)
        N = n // M
        
        if N == 0:
            return 1.0, True
        
        # Expected values (for pattern of all ones)
        lambda_val = (M - pattern_length + 1) / (2 ** pattern_length)
        eta = lambda_val / 2
        
        # Count occurrences in each block
        frequencies = []
        for i in range(N):
            block = bits[i * M:(i + 1) * M]
            count = 0
            
            for j in range(len(block) - pattern_length + 1):
                if np.array_equal(block[j:j + pattern_length], pattern):
                    count += 1
            
            frequencies.append(count)
        
        # Calculate chi-square statistic
        chi_square = sum((freq - lambda_val) ** 2 / lambda_val for freq in frequencies)
        
        # Calculate p-value
        p_value = sp.gammaincc(N / 2, chi_square / 2)
        
        return p_value, p_value >= self.alpha

