"""
Description:
- Seeded sampling and shuffling of row indices. Each call uses its own random.Random(seed).
- Spec: ARCHITECTURE.md F-SMP-1 - F-SMP-3.
"""

import random


# Function to draw a seeded sample of row indices
def sample_indices(usable_indices, sample_size, seed):
    """
    Description:
    - Draw sample_size indices uniformly at random without replacement.

    Input arguments:
       usable_indices (list[int]): Indices of the usable rows; never modified.
       sample_size (int): Number of indices to draw, e.g. 2000.
       seed (int): Random seed, e.g. 42.

    Return:
        list[int]: distinct indices (raises ValueError if sample_size > len(usable_indices)).
    """
    generator = random.Random(seed)
    return generator.sample(usable_indices, sample_size)


# Function to put indices into a seeded random order
def shuffle_indices(row_indices, seed):
    """
    Description:
    - Return the same indices in a random order fixed by the seed.
    - Used once for the order shared by the input-order and repeated-values experiments.

    Input arguments:
       row_indices (list[int]): Row indices; never modified.
       seed (int): Random seed, e.g. 43.

    Return:
        list[int]: a new, shuffled list.
    """
    shuffled_indices = row_indices[:]
    generator = random.Random(seed)
    generator.shuffle(shuffled_indices)
    return shuffled_indices
