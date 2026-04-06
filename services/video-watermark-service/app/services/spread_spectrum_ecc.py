"""Concatenated ECC for spread-spectrum watermarking.

Implements a two-layer concatenated coding scheme:
  - Outer code: Reed-Solomon RS(32, 8) over GF(2^8)
  - Inner code: Rate-1/3 convolutional code, constraint length K=7

The soft-decision Viterbi decoder feeds per-bit confidence scores into an
erasure bridge that marks low-confidence RS symbols as erasures, doubling
the outer code's correction capacity for those positions.
"""

from __future__ import annotations

import numpy as np
import reedsolo

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

K = 7  # Constraint length
NUM_STATES = 1 << (K - 1)  # 64
TAIL_BITS = K - 1  # 6
RS_DATA_BYTES = 8
RS_PARITY_BYTES = 24
RS_TOTAL_BYTES = RS_DATA_BYTES + RS_PARITY_BYTES  # 32
DATA_BITS = RS_TOTAL_BYTES * 8  # 256
INPUT_BITS = DATA_BITS + TAIL_BITS  # 262
CODED_BITS = INPUT_BITS * 3  # 786

# Generator polynomials (octal) -> binary tap masks
# 171_oct = 0o171 = 0b01111001
# 133_oct = 0o133 = 0b01011011
# 165_oct = 0o165 = 0b01110101
GENERATORS = (0o171, 0o133, 0o165)
RATE_INV = len(GENERATORS)  # 3

# Precompute output bits for every (state, input_bit) pair.
# _output_table[state][input_bit] is a tuple of RATE_INV bits (uint8).
_output_table: list[list[tuple[int, ...]]] = []
# _next_state[state][input_bit] -> next state
_next_state: list[list[int]] = []

for _state in range(NUM_STATES):
    _out_for_state: list[tuple[int, ...]] = []
    _nxt_for_state: list[int] = []
    for _inp in (0, 1):
        # The shift register is (K-1) bits of state plus the new input bit at the MSB.
        _reg = (_inp << (K - 1)) | _state
        _bits: list[int] = []
        for _g in GENERATORS:
            # XOR the register with the generator, count parity (mod 2)
            _bits.append(bin(_reg & _g).count("1") % 2)
        _out_for_state.append(tuple(_bits))
        _nxt_for_state.append(_reg >> 1)
    _output_table.append(_out_for_state)
    _next_state.append(_nxt_for_state)

# Convert to numpy arrays for vectorized Viterbi inner loop.
# _np_output[state, input_bit, :] = output bits (3,)
_np_output = np.array(_output_table, dtype=np.int8)  # (64, 2, 3)
# _np_next_state[state, input_bit] = next_state
_np_next_state = np.array(_next_state, dtype=np.int32)  # (64, 2)

# Precomputed expected sign for branch metric computation: -1 or +1
_expected_sign = 2.0 * _np_output.astype(np.float64) - 1.0  # (64, 2, 3)

# Reverse trellis mapping for vectorized ACS (Add-Compare-Select).
# Each next_state has exactly 2 predecessors. The input bit is determined
# solely by the MSB of the next_state: 0 for states 0..31, 1 for 32..63.
_prev_pairs = np.zeros((NUM_STATES, 2), dtype=np.int32)
_inp_for_state = np.zeros(NUM_STATES, dtype=np.int32)
for _ns in range(NUM_STATES):
    _inp_for_state[_ns] = _ns >> (K - 2)
    _base = _ns & ((1 << (K - 2)) - 1)
    _prev_pairs[_ns, 0] = _base << 1
    _prev_pairs[_ns, 1] = (_base << 1) | 1

# RS codec (24 parity symbols -> corrects 12 errors or 24 erasures)
_rs_codec = reedsolo.RSCodec(RS_PARITY_BYTES)


# ---------------------------------------------------------------------------
# Reed-Solomon layer
# ---------------------------------------------------------------------------


def _rs_encode(data: bytes) -> bytes:
    """RS(32,8) encode: 8 data bytes -> 32 bytes."""
    encoded = _rs_codec.encode(data)
    return bytes(encoded)


def _rs_decode(data: bytes, erasure_pos: list[int] | None = None) -> bytes | None:
    """RS(32,8) decode with optional erasure positions. Returns 8 data bytes or None."""
    try:
        if erasure_pos:
            erase_pos_int = [int(p) for p in erasure_pos]
            decoded = _rs_codec.decode(data, erase_pos=erase_pos_int)
        else:
            decoded = _rs_codec.decode(data)
        return bytes(decoded[0])
    except reedsolo.ReedSolomonError:
        return None


# ---------------------------------------------------------------------------
# Convolutional encoder
# ---------------------------------------------------------------------------


def _conv_encode(bits: np.ndarray) -> np.ndarray:
    """Rate-1/3 K=7 convolutional encode.

    Args:
        bits: Array of 0/1 uint8 values. Caller must append K-1 tail bits.

    Returns:
        Array of 0/1 uint8 values, length = len(bits) * 3.
    """
    n = len(bits)
    output = np.empty(n * RATE_INV, dtype=np.uint8)
    state = 0
    for i in range(n):
        inp = int(bits[i])
        out_bits = _output_table[state][inp]
        idx = i * RATE_INV
        output[idx] = out_bits[0]
        output[idx + 1] = out_bits[1]
        output[idx + 2] = out_bits[2]
        state = _next_state[state][inp]
    return output


# ---------------------------------------------------------------------------
# Soft-decision Viterbi decoder
# ---------------------------------------------------------------------------


def _viterbi_decode(soft_values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Soft-decision Viterbi decode with vectorized ACS.

    Uses precomputed reverse trellis mapping to replace the O(NUM_STATES)
    inner Python loop with numpy fancy indexing. Saves per-step metric
    deltas during the single forward pass, eliminating the redundant
    second pass previously used for confidence computation.

    Args:
        soft_values: Array of float64 soft values, length must be a multiple of 3.
            Sign indicates bit decision (+ve=1, -ve=0), magnitude is confidence.

    Returns:
        (decoded_bits, per_bit_confidence).
        decoded_bits: uint8 array of 0/1 for the data + tail bits.
        per_bit_confidence: float64 array of the same length.
    """
    num_steps = len(soft_values) // RATE_INV

    NEG_INF = -1e18
    path_metrics = np.full(NUM_STATES, NEG_INF, dtype=np.float64)
    path_metrics[0] = 0.0

    survivor = np.zeros((num_steps, NUM_STATES), dtype=np.int32)
    # Save per-step best and second-best metrics for confidence extraction
    best_metrics_all = np.zeros((num_steps, NUM_STATES), dtype=np.float64)
    second_best_all = np.full((num_steps, NUM_STATES), NEG_INF, dtype=np.float64)

    for step in range(num_steps):
        idx = step * RATE_INV
        sv = soft_values[idx : idx + RATE_INV]  # shape (3,)

        # Branch metric for every (state, input_bit)
        branch_metrics = np.einsum("sij,j->si", _expected_sign, sv)  # (64, 2)

        # Candidate metrics: path_metrics[prev_state] + branch_metrics[prev_state, inp]
        candidate_metrics = path_metrics[:, np.newaxis] + branch_metrics  # (64, 2)

        # Vectorized ACS: each next_state has exactly 2 predecessors from
        # _prev_pairs, both arriving with the same input bit _inp_for_state.
        cand0 = candidate_metrics[_prev_pairs[:, 0], _inp_for_state]  # (64,)
        cand1 = candidate_metrics[_prev_pairs[:, 1], _inp_for_state]  # (64,)

        better_is_1 = cand1 > cand0
        path_metrics = np.where(better_is_1, cand1, cand0)
        survivor[step] = np.where(better_is_1, _prev_pairs[:, 1], _prev_pairs[:, 0])
        best_metrics_all[step] = path_metrics
        second_best_all[step] = np.where(better_is_1, cand0, cand1)

    # Traceback from state 0 (trellis terminated with tail bits).
    # The input bit for each state equals its MSB: state >> (K-2).
    decoded_bits = np.zeros(num_steps, dtype=np.uint8)
    per_bit_confidence = np.zeros(num_steps, dtype=np.float64)
    state = 0
    for step in range(num_steps - 1, -1, -1):
        decoded_bits[step] = state >> (K - 2)
        delta = best_metrics_all[step, state] - second_best_all[step, state]
        per_bit_confidence[step] = max(0.0, delta)
        state = survivor[step, state]

    return decoded_bits, per_bit_confidence


# ---------------------------------------------------------------------------
# Erasure bridge
# ---------------------------------------------------------------------------


def _erasure_bridge(
    decoded_bits: np.ndarray,
    bit_confidence: np.ndarray,
    threshold: float,
) -> tuple[bytes, list[int]]:
    """Convert Viterbi output to RS symbols + erasure positions.

    Groups the 256 decoded bits into 32 eight-bit RS symbols. For each symbol,
    if the minimum bit confidence within that symbol falls below *threshold*,
    the symbol index is added to the erasure list.

    Returns:
        (32 bytes for RS decoder, list of erasure position indices).
    """
    assert len(decoded_bits) >= DATA_BITS
    data_bits = decoded_bits[:DATA_BITS]
    conf_bits = bit_confidence[:DATA_BITS]

    symbols = bytearray(RS_TOTAL_BYTES)
    erasures: list[int] = []

    for sym_idx in range(RS_TOTAL_BYTES):
        start = sym_idx * 8
        end = start + 8
        byte_val = 0
        for bit_offset in range(8):
            byte_val = (byte_val << 1) | int(data_bits[start + bit_offset])
        symbols[sym_idx] = byte_val

        min_conf = float(conf_bits[start:end].min())
        if min_conf < threshold:
            erasures.append(sym_idx)

    return bytes(symbols), erasures


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def ecc_encode(payload: bytes) -> np.ndarray:
    """Encode 8-byte payload through RS + convolutional code.

    Args:
        payload: Exactly 8 bytes (64-bit watermark payload).

    Returns:
        np.ndarray of shape (786,) with dtype uint8, values 0 or 1.

    Raises:
        ValueError: If payload is not exactly 8 bytes.
    """
    if len(payload) != RS_DATA_BYTES:
        raise ValueError(f"Payload must be exactly 8 bytes, got {len(payload)}")

    # Outer code: RS(32, 8)
    rs_encoded = _rs_encode(payload)

    # Convert 32 bytes to 256 bits (MSB first)
    bits = np.unpackbits(np.frombuffer(rs_encoded, dtype=np.uint8))

    # Append K-1 = 6 tail bits for trellis termination
    bits_with_tail = np.concatenate([bits, np.zeros(TAIL_BITS, dtype=np.uint8)])

    # Inner code: rate-1/3 convolutional
    coded = _conv_encode(bits_with_tail)
    assert len(coded) == CODED_BITS
    return coded


def ecc_decode(soft_values: np.ndarray, erasure_threshold: float = 0.1) -> tuple[bytes | None, int]:
    """Decode soft correlation values through Viterbi + RS.

    Args:
        soft_values: Array of shape (786,) with float64 values.
            Sign = bit decision (+ve=1, -ve=0), magnitude = confidence.
        erasure_threshold: Min per-bit confidence for a symbol to be trusted.

    Returns:
        Tuple of (payload_bytes_or_None, corrected_symbol_count).
        None if decoding fails (too many errors).
    """
    soft_values = np.asarray(soft_values, dtype=np.float64)
    if len(soft_values) != CODED_BITS:
        raise ValueError(f"Expected {CODED_BITS} soft values, got {len(soft_values)}")

    # Inner decode: soft Viterbi
    decoded_bits, bit_confidence = _viterbi_decode(soft_values)

    # Erasure bridge: map low-confidence bits to RS erasure positions
    rs_input, erasure_pos = _erasure_bridge(decoded_bits, bit_confidence, erasure_threshold)

    # Outer decode: RS with erasures
    recovered = _rs_decode(rs_input, erasure_pos=erasure_pos if erasure_pos else None)
    if recovered is None:
        # Retry without erasures (pure error correction mode)
        recovered = _rs_decode(rs_input)
        if recovered is None:
            return None, 0

    # Count corrected symbols by comparing RS input to re-encoded output
    re_encoded = _rs_encode(recovered)
    corrected = sum(1 for a, b in zip(rs_input, re_encoded) if a != b)

    return recovered, corrected
