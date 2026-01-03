import math
from collections import defaultdict
from collections.abc import Mapping
from typing import TypeVar

from mappingtools.algebra.lattice import product
from mappingtools.algebra.matrix.core import vec_mat

K = TypeVar("K")
N = TypeVar("N", int, float)

__all__ = [
    "bayes_update",
    "cross_entropy",
    "entropy",
    "kl_divergence",
    "marginalize",
    "markov_steady_state",
    "markov_step",
    "mutual_information",
    "normalize",
]


def bayes_update(
    prior: Mapping[K, float],
    likelihood: Mapping[K, float],
    evidence: float | None = None,
) -> dict[K, float]:
    """
    Perform a Bayesian update of a probability distribution.
    Posterior(H) = Likelihood(D|H) * Prior(H) / Evidence(D)

    Args:
        prior: The prior probability distribution P(H).
        likelihood: The likelihood of the data given the hypothesis P(D|H).
        evidence: The total probability of the data P(D).
                  If None, it is computed by normalizing the result.

    Returns:
        The posterior probability distribution P(H|D).
    """
    # Unnormalized posterior = Prior * Likelihood (Hadamard product)
    posterior = product(prior, likelihood)

    if not posterior:
        return {}

    if evidence is None:
        return normalize(posterior)

    return {k: v / evidence for k, v in posterior.items()}


def cross_entropy(
    p: Mapping[K, float],
    q: Mapping[K, float],
    base: float = 2.0,
) -> float:
    """
    Compute the Cross-Entropy between two probability distributions.
    H(P, Q) = - sum(P(x) * log(Q(x)))

    Args:
        p: The true distribution.
        q: The predicted distribution.
        base: Logarithm base (default 2 for bits).

    Returns:
        The cross-entropy value.
    """
    result = 0.0
    for k, prob_p in p.items():
        if prob_p > 0:
            prob_q = q.get(k, 0.0)
            if prob_q > 0:
                result -= prob_p * math.log(prob_q, base)
            else:
                return float("inf")
    return result


def entropy(
    distribution: Mapping[K, float],
    base: float = 2.0,
) -> float:
    """
    Compute the Shannon Entropy of a probability distribution.
    H(X) = - sum(P(x) * log(P(x)))

    Args:
        distribution: A mapping representing probabilities.
        base: Logarithm base (default 2 for bits).

    Returns:
        The entropy value.
    """
    result = 0.0
    for prob in distribution.values():
        if prob > 0:
            result -= prob * math.log(prob, base)
    return result


def kl_divergence(
    p: Mapping[K, float],
    q: Mapping[K, float],
    base: float = 2.0,
) -> float:
    """
    Compute the Kullback-Leibler (KL) Divergence.
    D_KL(P || Q) = sum(P(x) * log(P(x) / Q(x)))

    Args:
        p: The true distribution.
        q: The reference distribution.
        base: Logarithm base (default 2 for bits).

    Returns:
        The KL divergence value.
    """
    result = 0.0
    for k, prob_p in p.items():
        if prob_p > 0:
            prob_q = q.get(k, 0.0)
            if prob_q > 0:
                result += prob_p * math.log(prob_p / prob_q, base)
            else:
                return float("inf")
    return result


def marginalize(matrix: Mapping[K, Mapping[K, N]], axis: int = 0) -> dict[K, N]:
    """
    Marginalize a matrix by summing over an axis.

    Args:
        matrix: The input matrix.
        axis: 0 to sum over columns (produce row sums), 1 to sum over rows (produce column sums).
              Note: This follows numpy convention.
              axis=0 -> collapses rows, returns sums of columns.
              axis=1 -> collapses columns, returns sums of rows.

    Returns:
        A dictionary representing the marginal distribution.
    """
    if axis == 1:
        return {r: sum(row.values()) for r, row in matrix.items()}
    elif axis == 0:
        result = defaultdict(int)
        for row in matrix.values():
            for c, val in row.items():
                result[c] += val
        return dict(result)
    else:
        raise ValueError("Axis must be 0 or 1")


def markov_steady_state(
    transition_matrix: Mapping[K, Mapping[K, float]],
    iterations: int = 100,
    tolerance: float = 1e-6,
) -> dict[K, float]:
    """
    Compute the steady-state distribution of a Markov chain using Power Iteration.
    pi = pi * P

    Args:
        transition_matrix: Row-stochastic matrix (rows sum to 1).
                           P_ij = Prob(i -> j).
        iterations: Maximum number of iterations.
        tolerance: Convergence tolerance.

    Returns:
        The steady-state probability distribution.
    """
    # Initialize uniform distribution
    nodes = set(transition_matrix.keys()) | {k for row in transition_matrix.values() for k in row}
    n = len(nodes)
    if n == 0:
        return {}

    # Initial state vector (row vector)
    state = dict.fromkeys(nodes, 1.0 / n)

    for _ in range(iterations):
        # pi_new = pi_old * P
        new_state = vec_mat(state, transition_matrix)

        # Check convergence (L1 norm of difference)
        diff = sum(abs(new_state.get(k, 0) - state.get(k, 0)) for k in nodes)
        state = new_state

        if diff < tolerance:
            break

    return state


def markov_step(
    state: Mapping[K, float],
    transition_matrix: Mapping[K, Mapping[K, float]],
    steps: int = 1,
) -> dict[K, float]:
    """
    Advance a probability distribution by n steps in a Markov chain.
    state_new = state * P^n

    Args:
        state: Initial probability distribution (row vector).
        transition_matrix: Transition matrix P.
        steps: Number of steps to advance.

    Returns:
        The new probability distribution.
    """
    current = state
    for _ in range(steps):
        # Vector-Matrix multiplication: v_new = v * M
        current = vec_mat(current, transition_matrix)

    return current


def mutual_information(
    joint: Mapping[K, Mapping[K, float]],
    base: float = 2.0,
) -> float:
    """
    Compute the Mutual Information of a joint probability distribution.
    I(X; Y) = sum(P(x,y) * log(P(x,y) / (P(x)P(y))))
    I(X; Y) = H(X) + H(Y) - H(X, Y)

    Args:
        joint: A matrix representing the joint distribution P(X, Y).
               Rows are X, columns are Y.
        base: Logarithm base (default 2 for bits).

    Returns:
        The mutual information value.
    """
    # Compute marginals
    p_x = marginalize(joint, axis=1)
    p_y = marginalize(joint, axis=0)

    result = 0.0
    for x, row in joint.items():
        for y, p_xy in row.items():
            if p_xy > 0:
                px = p_x.get(x, 0.0)
                py = p_y.get(y, 0.0)
                if px > 0 and py > 0:
                    result += p_xy * math.log(p_xy / (px * py), base)

    return result


def normalize(mapping: Mapping[K, N]) -> dict[K, float]:
    """
    Normalize a mapping (probability distribution) so values sum to 1.

    Args:
        mapping: A mapping of keys to numeric values.

    Returns:
        A new dictionary with normalized values.

    Raises:
        ValueError: If the sum of values is zero.
    """
    total = sum(mapping.values())
    if total == 0:
        raise ValueError("Cannot normalize a mapping with zero sum.")
    return {k: v / total for k, v in mapping.items()}
