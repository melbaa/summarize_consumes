import pytest

from melbalabs.summarize_consumes.main import ConsumablesAccumulator
from melbalabs.summarize_consumes.main import ConsumablesEntry
from melbalabs.summarize_consumes.main import ConsumableStore
from melbalabs.summarize_consumes.main import Currency
from melbalabs.summarize_consumes.main import NAME2ITEMID


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


@pytest.mark.parametrize(
    ('amount', 'price', 'expected_total'),
    [
        (0, 0, 0),
        (5, 7, 35),
    ],
)
def test_consumable_store(amount, price, expected_total):
    name = 'bla'
    obj = ConsumableStore(name, amount, Currency(price))
    assert obj.total_price == expected_total


def test_consumable_entry():
    entry = ConsumablesEntry('name123', deaths=5)

    assert entry.name == 'name123'
    assert entry.deaths == 5
    assert not entry.consumables
    assert entry.total_spent == 0

    entry.add_consumable(ConsumableStore('item1', amount=1, price=Currency(5)))
    assert len(entry.consumables) == 1
    assert entry.total_spent == 5

    entry.add_consumable(ConsumableStore('item2',
                                         amount=3,
                                         price=Currency.from_string('15g')))
    assert len(entry.consumables) == 2
    assert entry.total_spent == Currency.from_string('45g5c')


def test_consumable_accumulator(app):
    app.pricedb.data[NAME2ITEMID['Elixir of the Mongoose']] = 30_000
    app.pricedb.data[NAME2ITEMID['Flask of the Titans']] = 1_000_000
    app.player['Psykhe']['Elixir of the Mongoose'] = 3
    app.player['Psykhe']['Flask of the Titans'] = 1
    app.player['Random']['Wizard Oil'] = 5
    app.death_count['Psykhe'] = 1
    app.death_count['Random'] = 42

    accumulator = ConsumablesAccumulator(app.player, app.pricedb, app.death_count)
    assert accumulator.death_count['Psykhe'] == 1
    assert not accumulator.data

    accumulator.calculate()
    assert len(accumulator.data) == 2

    player = next(e for e in accumulator.data if e.name == 'Psykhe')
    assert player.name == 'Psykhe'
    assert player.deaths == 1
    assert len(player.consumables) == 2
    assert player.total_spent == 1_090_000
