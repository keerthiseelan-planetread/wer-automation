
def levenshtein_words(ref_words, hyp_words):
    """
    Word-level Levenshtein distance calculation
    (edit distance between word arrays)
    """
    m = len(ref_words)
    n = len(hyp_words)

    # Create DP matrix
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # Initialize first column (deletions)
    for i in range(m + 1):
        dp[i][0] = i

    # Initialize first row (insertions)
    for j in range(n + 1):
        dp[0][j] = j

    # Fill the matrix
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if ref_words[i - 1] == hyp_words[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]  # No operation needed
            else:
                dp[i][j] = min(
                    dp[i - 1][j] + 1,      # Deletion
                    dp[i][j - 1] + 1,      # Insertion
                    dp[i - 1][j - 1] + 1   # Substitution
                )

    return dp[m][n]


def calculate_wer(reference, hypothesis):
    """
    WER calculation using the same logic as your React code
    """

    # Same word splitting logic
    ref_words = [w for w in reference.strip().split() if len(w) > 0]
    hyp_words = [w for w in hypothesis.strip().split() if len(w) > 0]

    distance = levenshtein_words(ref_words, hyp_words)

    # Same formula: distance / reference word count
    wer = distance / len(ref_words) if len(ref_words) > 0 else 0

    return {
        "wer": wer * 100,   # percentage (same as your code)
        # "refWordCount": len(ref_words),
        # "hypWordCount": len(hyp_words),
        # "distance": distance
    }
