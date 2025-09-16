"""
Custom logging handlers for better encoding support.
"""

import logging
import sys
from typing import TextIO


class SafeConsoleHandler(logging.StreamHandler):
    """
    A console handler that safely handles Unicode characters by encoding them
    as ASCII-safe alternatives when the console can't display them.
    """
    
    def __init__(self, stream: TextIO = None):
        super().__init__(stream or sys.stdout)
    
    def emit(self, record):
        """
        Emit a log record, safely handling Unicode characters.
        """
        try:
            # Get the formatted message
            msg = self.format(record)
            
            # Try to encode the message safely
            try:
                # First, try to encode with the stream's encoding
                encoded_msg = msg.encode(self.stream.encoding or 'utf-8', errors='strict')
            except (UnicodeEncodeError, AttributeError):
                # If that fails, replace problematic characters with ASCII alternatives
                safe_msg = self._make_ascii_safe(msg)
                encoded_msg = safe_msg.encode('ascii', errors='ignore')
            
            # Write the encoded message
            self.stream.write(encoded_msg.decode(self.stream.encoding or 'utf-8', errors='ignore'))
            self.stream.write(self.terminator)
            self.flush()
            
        except Exception:
            # If all else fails, use the parent's error handling
            self.handleError(record)
    
    def _make_ascii_safe(self, text: str) -> str:
        """
        Replace Unicode characters with ASCII-safe alternatives.
        """
        replacements = {
            '→': '->',
            '←': '<-',
            '↑': '^',
            '↓': 'v',
            '↔': '<->',
            '∞': 'inf',
            '≠': '!=',
            '≤': '<=',
            '≥': '>=',
            '±': '+/-',
            '×': 'x',
            '÷': '/',
            '°': 'deg',
            'α': 'alpha',
            'β': 'beta',
            'γ': 'gamma',
            'δ': 'delta',
            'ε': 'epsilon',
            'π': 'pi',
            'σ': 'sigma',
            'τ': 'tau',
            'φ': 'phi',
            'ψ': 'psi',
            'ω': 'omega',
        }
        
        result = text
        for unicode_char, ascii_replacement in replacements.items():
            result = result.replace(unicode_char, ascii_replacement)
        
        return result
