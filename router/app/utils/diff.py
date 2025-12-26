def simple_similarity(a: str, b: str) -> float:
    """
    Cheap similarity score to detect 'reproducer got the same idea'.
    Replace later with real diff/AST/pytest-based checks.
    """
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    aset = set(a.split())
    bset = set(b.split())
    inter = len(aset & bset)
    union = len(aset | bset)
    return inter / max(union, 1)
