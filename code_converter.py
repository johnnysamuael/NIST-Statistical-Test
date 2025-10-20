"""
Code Converter Module
Converts base-32 codes (with i, o, 0, 1 omitted) to binary sequences for NIST testing.
"""

class CodeConverter:
    """
    Converts codes to binary representation.
    Character set: Base-32 with only i, o, 0, 1 omitted
    Valid characters: 2-9, A-H, J-N, P-Z (32 characters total)
    """
    
    def __init__(self):
        # Base-32 alphabet with only i, o, 0, 1 omitted
        # Numbers: 2-9 (8 chars)
        # Letters: A-H, J-N, P-Z (24 chars) - omitting only I and O
        # Total: 32 characters
        self.alphabet = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"
        self.char_to_value = {char: idx for idx, char in enumerate(self.alphabet)}
        
    def code_to_binary(self, code):
        """
        Convert a code string to a binary sequence.
        
        Args:
            code: String code to convert
            
        Returns:
            String of binary digits (0s and 1s)
        """
        code = code.upper().strip()
        
        # Validate all characters
        for char in code:
            if char not in self.char_to_value:
                raise ValueError(f"Invalid character '{char}' in code. Valid characters: {self.alphabet}")
        
        # Convert each character to its 5-bit binary representation (2^5 = 32)
        binary_sequence = ""
        for char in code:
            value = self.char_to_value[char]
            # Convert to 5-bit binary (since we have 32 characters)
            binary = format(value, '05b')
            binary_sequence += binary
        
        return binary_sequence
    
    def binary_to_code(self, binary_sequence):
        """
        Convert a binary sequence back to a code string.
        
        Args:
            binary_sequence: String of binary digits
            
        Returns:
            Code string
        """
        if len(binary_sequence) % 5 != 0:
            raise ValueError("Binary sequence length must be a multiple of 5")
        
        code = ""
        for i in range(0, len(binary_sequence), 5):
            chunk = binary_sequence[i:i+5]
            value = int(chunk, 2)
            if value >= len(self.alphabet):
                raise ValueError(f"Invalid binary value: {value}")
            code += self.alphabet[value]
        
        return code
    
    def validate_code(self, code):
        """
        Validate if a code contains only valid characters.
        
        Args:
            code: String code to validate
            
        Returns:
            Boolean indicating if code is valid
        """
        code = code.upper().strip()
        return all(char in self.char_to_value for char in code)

