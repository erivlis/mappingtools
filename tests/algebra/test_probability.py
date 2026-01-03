import math

import pytest

from mappingtools.algebra.probability import (
    bayes_update,
    cross_entropy,
    entropy,
    kl_divergence,
    marginalize,
    markov_steady_state,
    markov_step,
    mutual_information,
    normalize,
)


def test_normalize():
    d = {"a": 2, "b": 8}
    n = normalize(d)
    assert n["a"] == pytest.approx(0.2)
    assert n["b"] == pytest.approx(0.8)


def test_normalize_zero_raises():
    with pytest.raises(ValueError):
        normalize({"a": 0})


def test_marginalize():
    # P(X, Y)
    # X=0: Y=0(0.1), Y=1(0.2) -> Sum=0.3
    # X=1: Y=0(0.3), Y=1(0.4) -> Sum=0.7
    joint = {0: {0: 0.1, 1: 0.2}, 1: {0: 0.3, 1: 0.4}}

    # Axis 1 (sum columns -> P(X))
    px = marginalize(joint, axis=1)
    assert px[0] == pytest.approx(0.3)
    assert px[1] == pytest.approx(0.7)

    # Axis 0 (sum rows -> P(Y))
    py = marginalize(joint, axis=0)
    assert py[0] == pytest.approx(0.4)
    assert py[1] == pytest.approx(0.6)


def test_marginalize_invalid_axis():
    with pytest.raises(ValueError):
        marginalize({}, axis=2)


def test_bayes_update():
    prior = {"H1": 0.5, "H2": 0.5}
    likelihood = {"H1": 0.8, "H2": 0.1}  # P(E|H)

    # P(E) = 0.5*0.8 + 0.5*0.1 = 0.45
    # P(H1|E) = 0.4 / 0.45 = 8/9 approx 0.888
    # P(H2|E) = 0.05 / 0.45 = 1/9 approx 0.111

    post = bayes_update(prior, likelihood)
    assert post["H1"] == pytest.approx(8 / 9)
    assert post["H2"] == pytest.approx(1 / 9)


def test_bayes_update_empty():
    assert bayes_update({}, {}) == {}


def test_bayes_update_with_evidence():
    prior = {"H1": 0.5}
    likelihood = {"H1": 0.8}
    # Unnormalized = 0.4. Evidence = 0.4. Result = 1.0
    post = bayes_update(prior, likelihood, evidence=0.4)
    assert post["H1"] == pytest.approx(1.0)


def test_entropy():
    # Uniform: -log2(0.5) = 1 bit
    d = {"a": 0.5, "b": 0.5}
    assert entropy(d) == pytest.approx(1.0)

    # Certainty: 0 bits
    d2 = {"a": 1.0, "b": 0.0}
    assert entropy(d2) == pytest.approx(0.0)


def test_cross_entropy():
    p = {"a": 0.5, "b": 0.5}
    q = {"a": 0.5, "b": 0.5}
    assert cross_entropy(p, q) == pytest.approx(1.0)

    # Infinite
    p2 = {"a": 1.0}
    q2 = {"a": 0.0}  # log(0)
    assert cross_entropy(p2, q2) == float("inf")


def test_cross_entropy_inf():
    p = {0: 0.5}
    q = {0: 0.0}  # q(x) is 0 where p(x) > 0
    assert cross_entropy(p, q) == float("inf")


def test_kl_divergence():
    p = {"a": 0.5, "b": 0.5}
    q = {"a": 0.25, "b": 0.75}
    # 0.5 * log2(0.5/0.25) + 0.5 * log2(0.5/0.75)
    # 0.5 * 1 + 0.5 * log2(2/3)
    # 0.5 + 0.5 * (1 - 1.58) = 0.5 - 0.29 = 0.2075
    val = 0.5 * math.log2(2) + 0.5 * math.log2(2 / 3)
    assert kl_divergence(p, q) == pytest.approx(val)


def test_kl_divergence_infinite():
    p = {"a": 0.5}
    q = {"a": 0.0}
    assert kl_divergence(p, q) == float("inf")


def test_kl_divergence_inf_coverage():
    # Duplicate of above but ensures explicit coverage if slightly different paths exist
    p = {0: 0.5}
    q = {0: 0.0}
    assert kl_divergence(p, q) == float("inf")


def test_mutual_information():
    # Independent X, Y -> MI = 0
    # P(X) = 0.5, 0.5. P(Y) = 0.5, 0.5
    # P(X,Y) = 0.25 for all
    joint = {0: {0: 0.25, 1: 0.25}, 1: {0: 0.25, 1: 0.25}}
    assert mutual_information(joint) == pytest.approx(0.0)

    # Perfectly dependent X=Y
    # P(0,0)=0.5, P(1,1)=0.5
    joint_dep = {0: {0: 0.5}, 1: {1: 0.5}}
    # H(X)=1, H(Y)=1, H(X,Y)=1. MI = 1+1-1 = 1.
    assert mutual_information(joint_dep) == pytest.approx(1.0)


def test_markov():
    # 0 -> 1 (1.0)
    # 1 -> 0 (1.0)
    transition = {0: {1: 1.0}, 1: {0: 1.0}}
    state = {0: 1.0}

    # Step 1: {1: 1.0}
    s1 = markov_step(state, transition, 1)
    assert s1[1] == pytest.approx(1.0)

    # Steady state: {0: 0.5, 1: 0.5}
    ss = markov_steady_state(transition)
    assert ss[0] == pytest.approx(0.5)
    assert ss[1] == pytest.approx(0.5)


def test_markov_steady_state_convergence():
    # Simple case that converges quickly
    # 0 -> 1, 1 -> 0
    P = {0: {1: 1.0}, 1: {0: 1.0}}  # noqa: N806
    # Steady state is 0.5, 0.5
    # This should hit the tolerance break
    steady = markov_steady_state(P, iterations=100, tolerance=1e-5)
    assert steady[0] == pytest.approx(0.5)
    assert steady[1] == pytest.approx(0.5)


def test_markov_steady_state_empty():
    assert markov_steady_state({}) == {}
