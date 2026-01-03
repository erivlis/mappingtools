import pytest

from mappingtools.algebra.transforms import (
    box_counting_dimension,
    convolve,
    dft,
    hilbert,
    idft,
    lorentz_boost,
    z_transform,
)


def test_convolve():
    # [1, 2] * [1, 1] = [1, 3, 2]
    # 0: 1*1=1
    # 1: 1*1 + 2*1 = 3
    # 2: 2*1 = 2
    f = {0: 1, 1: 2}
    g = {0: 1, 1: 1}
    h = convolve(f, g)
    assert h == {0: 1, 1: 3, 2: 2}

def test_dft_idft():
    # Impulse [1, 0, 0, 0] -> Spectrum [1, 1, 1, 1]
    sig = {0: 1}
    spec = dft(sig, n=4)
    assert len(spec) == 4
    for k in range(4):
        assert spec[k] == 1+0j

    recon = idft(spec, n=4)
    assert recon[0].real == pytest.approx(1.0)
    assert abs(recon.get(1, 0)) < 1e-9

def test_dft_empty():
    assert dft({}) == {}
    assert idft({}) == {}

def test_hilbert():
    # Impulse -> Analytic Signal
    # sig = [1, 0, 0, 0]
    # Analytic = [1, 0.5j, 0, -0.5j] (approx)
    # Real part is original signal. Imaginary part is Hilbert transform.
    # H(delta) = 1/pi*t (discrete version is cot(pi*t/2) or similar)

    sig = {0: 1}
    h = hilbert(sig, n=4)

    # n=0: Should be 1+0j (Original signal is 1, H(0)=0)
    assert h[0] == pytest.approx(1+0j)

    # n=1: Should be 0 + 0.5j
    # Calculation: 1/4 * (1 + 2j - 1) = 0.5j
    assert h[1] == pytest.approx(0.5j)

def test_hilbert_empty():
    assert hilbert({}) == {}

def test_z_transform():
    # Unit step u[n] -> 1 / (1 - z^-1)
    # {0: 1, 1: 1, ...}
    # Let's test finite: {0: 1, 1: 2} at z=2
    # 1 + 2*(1/2) = 2
    sig = {0: 1, 1: 2}
    val = z_transform(sig, z=2)
    assert val == 2.0

def test_z_transform_negative_index():
    # x[-1] should be ignored
    signal = {-1: 1, 0: 1}
    # Z-transform of delta(n) is 1. delta(n+1) is ignored by unilateral ZT.
    assert z_transform(signal, 2) == 1

def test_lorentz():
    # Rest frame (t=1, x=0)
    # Boost beta=0.6 (gamma=1.25)
    # t' = 1.25 * (1 - 0) = 1.25
    # x' = 1.25 * (0 - 0.6*1) = -0.75
    vec = {0: 1.0, 1: 0.0}
    boosted = lorentz_boost(vec, beta=0.6)
    assert boosted[0] == 1.25
    assert boosted[1] == -0.75

def test_lorentz_invalid_beta():
    with pytest.raises(ValueError):
        lorentz_boost({}, beta=1.0)

def test_lorentz_sparse_removal():
    # If result is 0, key should be removed
    # t=0, x=0 -> t'=0, x'=0. Result should be empty.
    vec = {0: 0.0, 1: 0.0}
    boosted = lorentz_boost(vec, beta=0.5)
    assert 0 not in boosted
    assert 1 not in boosted

def test_fractal():
    # Line of 4 points: (0,), (1,), (2,), (3,)
    # Box size 1: 4 boxes
    # Box size 2: 2 boxes
    # Box size 4: 1 box
    # log(1/s): 0, -0.69, -1.38
    # log(N): 1.38, 0.69, 0
    # Slope should be exactly 1.0
    points = {(i,): 1 for i in range(4)}
    dim = box_counting_dimension(points, max_box_size=4)
    assert dim == pytest.approx(1.0, 0.1)

def test_fractal_empty():
    assert box_counting_dimension({}) == 0.0
    assert box_counting_dimension({}, min_box_size=1) == 0.0

def test_fractal_single_point():
    # 1 point -> dim 0
    points = {(0,): 1}
    dim = box_counting_dimension(points)
    assert dim == 0.0

def test_box_counting_dimension_edge_cases():
    # Not enough points
    assert box_counting_dimension({}) == 0.0
    assert box_counting_dimension({(0,): 1.0}) == 0.0

    # Not enough sizes (min_box_size > extent)
    # points: (0,), (1,) extent=1. max_box=0 (if None).
    # If we force max_box_size
    points = {(0,): 1.0, (10,): 1.0}
    # min_box_size=100, max_box_size=200 -> only one size?
    assert box_counting_dimension(points, min_box_size=100) == 0.0
