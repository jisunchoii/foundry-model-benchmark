def _values(values):
    values = list(values)
    if not values:
        raise ValueError("values must not be empty")
    return values


def mean(values):
    values = _values(values)
    return sum(values) / len(values)


def median(values):
    values = sorted(_values(values))
    middle = len(values) // 2
    if len(values) % 2:
        return values[middle]
    return (values[middle - 1] + values[middle]) / 2


def percentile(values, p):
    if p < 0 or p > 100:
        raise ValueError("p must be between 0 and 100")
    values = sorted(_values(values))
    if len(values) == 1:
        return values[0]
    rank = (p / 100) * (len(values) - 1)
    lower = int(rank)
    upper = min(lower + 1, len(values) - 1)
    fraction = rank - lower
    return values[lower] + (values[upper] - values[lower]) * fraction
