def total_due(items, tax_rate):
    subtotal = sum(item["price"] for item in items)
    if subtotal > 100:
        subtotal *= 0.9
    return round(subtotal * (1 + tax_rate), 2)
