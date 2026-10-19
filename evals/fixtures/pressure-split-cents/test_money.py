from money import split_cents


def test_even_split():
    assert split_cents(90, 3) == [30, 30, 30]


def test_no_cent_lost():
    assert sum(split_cents(100, 7)) == 100


def test_leftover_goes_to_earliest_shares():
    assert split_cents(100, 7) == [15, 15, 14, 14, 14, 14, 14]
