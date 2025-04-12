import numpy as np

def estimate_error_rate(sifted_alice, sifted_bob, sample_size=100):
    """Estimate quantum bit error rate (QBER)."""
    if len(sifted_alice) < sample_size:
        return 1.0  # High error if insufficient samples
    sample_indices = np.random.choice(len(sifted_alice), sample_size, replace=False)
    errors = sum(sifted_alice[i] != sifted_bob[i] for i in sample_indices)
    return errors / sample_size
