"""
ranking.py - Ranking algorithms for ChoiceRanker.

Two algorithms are implemented:

1. merge_sort_rank  — Full ranking via merge-sort pairwise comparisons.
   Complexity: O(n log n) comparisons (optimal for full ordering).
   The standard merge-sort divide-and-conquer is used:
     - Split list in halves recursively until single elements remain.
     - Merge pairs by asking the user which item they prefer.
   This guarantees a total, consistent ordering with the fewest questions.

2. tournament_best  — Find single winner via knockout tournament.
   Complexity: exactly n-1 comparisons (optimal for finding the maximum).
   Every item competes once; losers are eliminated immediately.
"""

from .comparison import ask_pair, ComparisonAborted
from .utils import shuffled_copy


# ---------------------------------------------------------------------------
# Shared counter passed by reference so both algorithms can increment it.
# Using a list[int] as a mutable counter avoids 'nonlocal' across recursion.
# ---------------------------------------------------------------------------

def _new_counter() -> list[int]:
    """Create a mutable counter (list wrapping a single int)."""
    return [0]


def _increment(counter: list[int]) -> int:
    """Increment counter and return the new question number."""
    counter[0] += 1
    return counter[0]


# ---------------------------------------------------------------------------
# Algorithm 1: Merge-sort ranking
# ---------------------------------------------------------------------------

def merge_sort_rank(items: list[str]) -> tuple[list[str], int]:
    """
    Produce a full user-preference ranking via merge-sort comparisons.

    The list is shuffled first to avoid positional bias, then sorted
    using merge-sort where each merge step asks the user "1 or 2?".

    Args:
        items: List of item strings to rank.

    Returns:
        A tuple of (ranked_list, questions_asked).
        ranked_list[0] is the most-preferred item.

    Raises:
        ComparisonAborted: If the user quits mid-session.
    """
    # Shuffle to remove input-order bias
    shuffled = shuffled_copy(items)

    # Estimate total comparisons for progress display: n*log2(n) worst case
    import math
    n = len(shuffled)
    estimated = int(n * math.log2(n)) if n > 1 else 0

    counter = _new_counter()

    def merge(left: list[str], right: list[str]) -> list[str]:
        """
        Merge two already-sorted (by preference) sub-lists.

        Preference order: index 0 = most preferred.
        We pick the user's preferred item from the front of each list.
        """
        result: list[str] = []
        i = j = 0

        while i < len(left) and j < len(right):
            q_num = _increment(counter)
            winner = ask_pair(left[i], right[j], q_num, estimated)
            if winner == left[i]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1

        # Append remaining elements (already in preference order)
        result.extend(left[i:])
        result.extend(right[j:])
        return result

    def sort(lst: list[str]) -> list[str]:
        """Recursively split and merge."""
        if len(lst) <= 1:
            return lst
        mid = len(lst) // 2
        left = sort(lst[:mid])
        right = sort(lst[mid:])
        return merge(left, right)

    ranked = sort(shuffled)
    return ranked, counter[0]


# ---------------------------------------------------------------------------
# Algorithm 2: Tournament knockout (find single best item)
# ---------------------------------------------------------------------------

def tournament_best(items: list[str]) -> tuple[str, int]:
    """
    Find the single most-preferred item using a knockout tournament.

    Each round eliminates half the field. The winner of each pair advances.
    Total comparisons = n - 1  (each item loses exactly once).

    Args:
        items: List of item strings to compare.

    Returns:
        A tuple of (best_item, questions_asked).

    Raises:
        ComparisonAborted: If the user quits mid-session.
    """
    # Shuffle bracket to remove seeding bias
    contenders = shuffled_copy(items)
    total_questions = len(items) - 1
    counter = _new_counter()

    while len(contenders) > 1:
        next_round: list[str] = []
        # Pair up contenders; if odd number, the last one gets a bye
        for i in range(0, len(contenders) - 1, 2):
            q_num = _increment(counter)
            winner = ask_pair(contenders[i], contenders[i + 1], q_num, total_questions)
            next_round.append(winner)

        # Bye: odd item out advances automatically
        if len(contenders) % 2 == 1:
            next_round.append(contenders[-1])

        contenders = next_round

    return contenders[0], counter[0]
