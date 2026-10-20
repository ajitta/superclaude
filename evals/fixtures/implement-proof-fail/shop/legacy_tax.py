# Owned by the billing team; frozen until their Q4 rewrite.
RATE = 0.11


def tax(amount):
    return round(amount * RATE, 2)
