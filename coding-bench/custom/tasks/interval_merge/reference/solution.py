def merge_intervals(intervals):
    normalized = []
    for start, end in intervals:
        if start > end:
            raise ValueError("interval start must be <= end")
        normalized.append((start, end))
    merged = []
    for start, end in sorted(normalized):
        if not merged or start > merged[-1][1]:
            merged.append((start, end))
        else:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
    return merged
