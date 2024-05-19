import pytest

from melbalabs.summarize_consumes.main import Currency


def test_currency():
    c1 = Currency("1g")

    assert c1 == 10000
    assert isinstance(c1, Currency)

    c2 = c1 + 100
    assert c2 == 10100
    assert isinstance(c2, Currency)

    c3 = c2 * 2
    assert c3 == 20200
    assert isinstance(c3, Currency)

    assert c3 / 4 == 5050
    assert c3 // 3 == 6733


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (0, 0),
        (1, 1),
        (5.501, 5),
        (5.499, 5),
        (999999, 999999),
        ("0c", 0),
        ("0s", 0),
        ("0s0c", 0),
        ("0g0s1c", 1),
        ("0g1s0c", 100),
        ("1g0s0c", 10000),
        ("1g1s1c", 10101),
        ("1g 1s 1c", 10101),
        ("1g50s", 15000),
        ("10000000g99s99c", 100000009999),
        ("1g 2g 3g", 10000),
        ("123123s", 12312300),
        ("1000s100000c", 200000),
    ],
)
def test_currency_init(source, expected):
    value = Currency(source)
    assert value == expected
    assert value == Currency(expected)


@pytest.mark.parametrize(("invalid_value"), ["", "0", "x", "123kg"])
def test_currency_init_negative(invalid_value):
    with pytest.raises(ValueError):
        Currency(invalid_value)
