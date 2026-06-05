def total_due(items, tax_rate):
    discountable = 0
    nondiscountable = 0
    for item in items:
        amount = item["price"] * item.get("quantity", 1)
        if item.get("category") == "gift_card":
            nondiscountable += amount
        else:
            discountable += amount
    if discountable + nondiscountable > 100:
        discountable *= 0.9
    return round((discountable + nondiscountable) * (1 + tax_rate), 2)
