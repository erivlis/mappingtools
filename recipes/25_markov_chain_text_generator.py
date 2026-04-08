"""
Recipe 25: Markov Chain Text Generation (MappingCollector + Aggregation.COUNT)

Before Large Language Models (LLMs) like GPT, there were Markov Chains.
A Markov Chain generates text by predicting the next word based purely on the
current word, using probabilities derived from a training corpus.

Mathematically, a Markov transition matrix is just a dictionary mapping a
State -> Counter(Next States). This recipe demonstrates how `MappingCollector`
with `Aggregation.COUNT` effortlessly builds this matrix from a stream of bigrams,
allowing us to generate completely new, algorithmically hallucinated sentences!
"""

import random

from mappingtools.aggregation import Aggregation
from mappingtools.collectors import MappingCollector


def main():
    # 1. A small training corpus (A mix of sci-fi and philosophy)
    corpus = (
        "the quick brown fox jumps over the lazy dog. "
        "the fox is very quick and very smart. "
        "the dog is lazy but the dog is happy. "
        "a smart fox jumps high. "
        "a happy dog sleeps all day."
    )

    # 2. Tokenize the corpus into a flat list of words
    words = corpus.replace(".", " .").split()

    # 3. Create a stream of Bigrams (Current Word -> Next Word)
    # E.g., [("the", "quick"), ("quick", "brown"), ...]
    bigrams = [(words[i], words[i+1]) for i in range(len(words)-1)]

    # 4. Build the Markov Transition Matrix!
    # We use Aggregation.COUNT to count how many times "Word B" follows "Word A".
    # This automatically builds: { "the": Counter({"quick": 1, "fox": 1, "lazy": 1...}) }
    markov_model = MappingCollector(aggregation=Aggregation.COUNT)

    for current_word, next_word in bigrams:
        markov_model.add(current_word, next_word)

    print("--- 1. The Markov Transition Matrix (Partial) ---")
    print(f"What follows 'the'? -> {markov_model.mapping['the']}")
    print(f"What follows 'is'?  -> {markov_model.mapping['is']}")

    # 5. Generate new text using the model!
    def generate_sentence(start_word="the", max_words=15):
        sentence = [start_word]
        current = start_word

        for _ in range(max_words):
            # Get the Counter of possible next words
            next_word_counts = markov_model.mapping.get(current)

            if not next_word_counts or current == ".":
                break # Reached the end of a chain or a period

            # Extract words and their frequencies (weights)
            population = list(next_word_counts.keys())
            weights = list(next_word_counts.values())

            # Choose the next word randomly, weighted by its historical frequency
            next_word = random.choices(population, weights=weights, k=1)[0]

            if next_word != ".":
                sentence.append(next_word)
            current = next_word

        return " ".join(sentence) + "."

    print("\n--- 2. Hallucinated Sentences ---")
    # Because there is randomness weighted by the counters,
    # we get different, grammatically valid (within the corpus) sentences!
    for i in range(10):
        print(f"Thought {i+1}: {generate_sentence(start_word='the')}")


if __name__ == "__main__":
    main()
