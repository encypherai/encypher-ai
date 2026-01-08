"""
Reed-Solomon Error Correction Service (TEAM_044).

Provides ECC encoding/decoding for distributed_redundant embedding strategy.
This allows recovery of embedded metadata even when portions of the text are
damaged or removed.

Patent Reference: Distributed Embedding with Redundancy/ECC
"""
import logging
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)


class ReedSolomonECC:
    """
    Reed-Solomon Error Correction Code implementation for text embeddings.
    
    This provides redundancy for distributed embeddings, allowing recovery
    even when some embedded data is lost or corrupted.
    
    The implementation uses a simplified RS approach suitable for text:
    - Data is split into k data symbols
    - n-k parity symbols are added
    - Can recover from loss of up to (n-k)/2 symbols
    """
    
    # Galois Field GF(2^8) parameters
    GF_EXP = [0] * 512  # Anti-log table
    GF_LOG = [0] * 256  # Log table
    PRIM = 0x11d  # Primitive polynomial for GF(2^8)
    
    def __init__(self, nsym: int = 10):
        """
        Initialize Reed-Solomon codec.
        
        Args:
            nsym: Number of error correction symbols (default 10).
                  Can correct up to nsym/2 errors.
        """
        self.nsym = nsym
        self._init_tables()
        self.generator = self._rs_generator_poly(nsym)
    
    def _init_tables(self):
        """Initialize Galois Field lookup tables."""
        x = 1
        for i in range(255):
            self.GF_EXP[i] = x
            self.GF_LOG[x] = i
            x <<= 1
            if x & 0x100:
                x ^= self.PRIM
        for i in range(255, 512):
            self.GF_EXP[i] = self.GF_EXP[i - 255]
    
    def _gf_mul(self, x: int, y: int) -> int:
        """Multiply two numbers in GF(2^8)."""
        if x == 0 or y == 0:
            return 0
        return self.GF_EXP[(self.GF_LOG[x] + self.GF_LOG[y]) % 255]
    
    def _gf_div(self, x: int, y: int) -> int:
        """Divide two numbers in GF(2^8)."""
        if y == 0:
            raise ZeroDivisionError()
        if x == 0:
            return 0
        return self.GF_EXP[(self.GF_LOG[x] - self.GF_LOG[y]) % 255]
    
    def _gf_poly_mul(self, p: List[int], q: List[int]) -> List[int]:
        """Multiply two polynomials in GF(2^8)."""
        r = [0] * (len(p) + len(q) - 1)
        for j, qj in enumerate(q):
            for i, pi in enumerate(p):
                r[i + j] ^= self._gf_mul(pi, qj)
        return r
    
    def _rs_generator_poly(self, nsym: int) -> List[int]:
        """Generate RS generator polynomial."""
        g = [1]
        for i in range(nsym):
            g = self._gf_poly_mul(g, [1, self.GF_EXP[i]])
        return g
    
    def encode(self, data: bytes) -> bytes:
        """
        Encode data with Reed-Solomon error correction.
        
        Args:
            data: Input data bytes
            
        Returns:
            Data with ECC parity bytes appended
        """
        if len(data) > 255 - self.nsym:
            # For longer data, encode in blocks
            return self._encode_blocks(data)
        
        # Convert to list of integers
        msg = list(data)
        
        # Pad message for polynomial division
        msg_out = msg + [0] * self.nsym
        
        # Polynomial division to get remainder (parity)
        for i in range(len(msg)):
            coef = msg_out[i]
            if coef != 0:
                for j, gj in enumerate(self.generator[1:], 1):
                    msg_out[i + j] ^= self._gf_mul(gj, coef)
        
        # Append parity to original message
        return bytes(msg + msg_out[-self.nsym:])
    
    def _encode_blocks(self, data: bytes) -> bytes:
        """Encode data in blocks for longer messages."""
        block_size = 255 - self.nsym
        result = bytearray()
        
        for i in range(0, len(data), block_size):
            block = data[i:i + block_size]
            encoded = self.encode(block)
            result.extend(encoded)
        
        return bytes(result)
    
    def decode(self, data: bytes, erasure_pos: Optional[List[int]] = None) -> Tuple[bytes, int]:
        """
        Decode Reed-Solomon encoded data.
        
        Args:
            data: Encoded data with ECC parity
            erasure_pos: Optional list of known error positions
            
        Returns:
            Tuple of (decoded data, number of errors corrected)
        """
        if len(data) > 255:
            return self._decode_blocks(data, erasure_pos)
        
        msg = list(data)
        
        # Calculate syndromes
        synd = self._calc_syndromes(msg)
        
        # Check if message is already correct
        if max(synd) == 0:
            return bytes(msg[:-self.nsym]), 0
        
        # Find error locator polynomial
        err_loc = self._find_error_locator(synd, erasure_pos)
        
        # Find error positions
        err_pos = self._find_errors(err_loc, len(msg))
        if err_pos is None:
            raise ValueError("Too many errors to correct")
        
        # Correct errors
        corrected = self._correct_errors(msg, synd, err_pos)
        
        return bytes(corrected[:-self.nsym]), len(err_pos)
    
    def _decode_blocks(self, data: bytes, erasure_pos: Optional[List[int]] = None) -> Tuple[bytes, int]:
        """Decode data in blocks."""
        block_size = 255
        result = bytearray()
        total_errors = 0
        
        for i in range(0, len(data), block_size):
            block = data[i:i + block_size]
            if len(block) < self.nsym:
                # Incomplete block, skip
                continue
            try:
                decoded, errors = self.decode(block, erasure_pos)
                result.extend(decoded)
                total_errors += errors
            except ValueError:
                # Block too corrupted, use what we have
                result.extend(block[:-self.nsym])
        
        return bytes(result), total_errors
    
    def _calc_syndromes(self, msg: List[int]) -> List[int]:
        """Calculate syndrome polynomial."""
        return [self._gf_poly_eval(msg, self.GF_EXP[i]) for i in range(self.nsym)]
    
    def _gf_poly_eval(self, poly: List[int], x: int) -> int:
        """Evaluate polynomial at x."""
        y = poly[0]
        for i in range(1, len(poly)):
            y = self._gf_mul(y, x) ^ poly[i]
        return y
    
    def _find_error_locator(self, synd: List[int], erasure_pos: Optional[List[int]] = None) -> List[int]:
        """Find error locator polynomial using Berlekamp-Massey algorithm."""
        err_loc = [1]
        old_loc = [1]
        
        synd_shift = 0
        if erasure_pos:
            for pos in erasure_pos:
                err_loc = self._gf_poly_mul(err_loc, [1, self.GF_EXP[pos]])
            synd_shift = len(erasure_pos)
        
        for i in range(self.nsym - synd_shift):
            delta = synd[i + synd_shift]
            for j in range(1, len(err_loc)):
                delta ^= self._gf_mul(err_loc[-(j + 1)], synd[i + synd_shift - j])
            
            old_loc = old_loc + [0]
            
            if delta != 0:
                if len(old_loc) > len(err_loc):
                    new_loc = [self._gf_mul(c, delta) for c in old_loc]
                    old_loc = [self._gf_div(c, delta) for c in err_loc]
                    err_loc = new_loc
                
                err_loc = [err_loc[j] ^ self._gf_mul(delta, old_loc[j]) 
                          for j in range(len(err_loc))]
        
        return err_loc
    
    def _find_errors(self, err_loc: List[int], nmess: int) -> Optional[List[int]]:
        """Find error positions using Chien search."""
        errs = len(err_loc) - 1
        err_pos = []
        
        for i in range(nmess):
            if self._gf_poly_eval(err_loc, self.GF_EXP[255 - i]) == 0:
                err_pos.append(nmess - 1 - i)
        
        if len(err_pos) != errs:
            return None
        
        return err_pos
    
    def _correct_errors(self, msg: List[int], synd: List[int], err_pos: List[int]) -> List[int]:
        """Correct errors using Forney algorithm."""
        coef_pos = [len(msg) - 1 - p for p in err_pos]
        
        # Calculate error evaluator polynomial
        err_loc = [1]
        for pos in coef_pos:
            err_loc = self._gf_poly_mul(err_loc, [1, self.GF_EXP[pos]])
        
        # Calculate error magnitudes
        msg_out = list(msg)
        for i, pos in enumerate(err_pos):
            xi = self.GF_EXP[coef_pos[i]]
            xi_inv = self.GF_EXP[255 - coef_pos[i]]
            
            # Error locator derivative
            err_loc_prime = 1
            for j, other_pos in enumerate(coef_pos):
                if j != i:
                    err_loc_prime = self._gf_mul(err_loc_prime, 
                                                  1 ^ self._gf_mul(xi_inv, self.GF_EXP[other_pos]))
            
            # Error evaluator
            y = 0
            for j, s in enumerate(synd):
                y ^= self._gf_mul(s, self.GF_EXP[(j * coef_pos[i]) % 255])
            
            # Error magnitude
            magnitude = self._gf_div(y, err_loc_prime)
            msg_out[pos] ^= magnitude
        
        return msg_out


# Global ECC instance with default parameters
ecc_service = ReedSolomonECC(nsym=10)


def encode_with_ecc(data: bytes, nsym: int = 10) -> bytes:
    """
    Encode data with Reed-Solomon ECC.
    
    Args:
        data: Input data bytes
        nsym: Number of ECC symbols (default 10)
        
    Returns:
        Data with ECC parity appended
    """
    codec = ReedSolomonECC(nsym=nsym)
    return codec.encode(data)


def decode_with_ecc(data: bytes, nsym: int = 10) -> Tuple[bytes, int]:
    """
    Decode Reed-Solomon encoded data.
    
    Args:
        data: Encoded data with ECC parity
        nsym: Number of ECC symbols used in encoding
        
    Returns:
        Tuple of (decoded data, number of errors corrected)
    """
    codec = ReedSolomonECC(nsym=nsym)
    return codec.decode(data)
