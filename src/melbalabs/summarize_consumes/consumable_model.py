from dataclasses import dataclass
from dataclasses import field
from typing import List
from typing import Tuple
from typing import Union

from melbalabs.summarize_consumes.entity_model import Component
from melbalabs.summarize_consumes.entity_model import Entity
from melbalabs.summarize_consumes.entity_model import SpellAliasComponent

"""
types of consumables by availability in combat log
* not in combat log at all. they are base components for pricing other consumables
* in native log
* in superwow log [1]
* in both native and superwow log

[1] types of consumables in the superwow log
* safe. easy to handle, no collision
* ignored. not useful to report on, like mailboxes
* enhance. improves the native counts, keeps the canonical name
* overwrite. can also improve ambiguous spells and convert them into a specific canonical name

types of consumables by how they are priced
* directly via itemid
* indirectly via components its made of. eg consumables from professions or quests
* not possible to price [2].

[2] not on the auction house. reasons include
* seasonal quests or nonseasonal quests
* looted BOPs like holy waters
* consumables that cast ambiguous spells. happens with some low level buffs.
the superwow log may disambiguate what exactly it is, but not guaranteed
* others?

the superwow logger names are different from the native names and from the
canonical names of this project. if available, the superwow logs counts
should be preferred to the native ones.
the native log misses a lot of consumables
the native log often doesn't show anything when a player reapplies a buff they already have


A design goal is to avoid having classes with optional attributes.

"""


@dataclass(frozen=True)
class NoPrice:
    pass


class ChargeValidation:
    charges: int

    def __post_init__(self):
        if self.charges <= 0:
            raise ValueError("positive charges plz")


@dataclass(frozen=True, kw_only=True)
class DirectPrice(ChargeValidation):
    """base item / non-component item"""

    itemid: int

    # Number of charges the item has (e.g. oils have 5 charges)
    charges: int = 1

    def __post_init__(self):
        super().__post_init__()
        if self.itemid is None:
            raise ValueError("itemid must be int")


@dataclass(frozen=True, kw_only=True)
class PriceFromIngredients(ChargeValidation):
    charges: int = 1

    ingredients: List[Tuple[Entity, float]] = field(default_factory=list)


@dataclass(frozen=True)
class IgnoreStrategyComponent(Component):
    """Ignore this Superwow consumable."""

    pass


@dataclass(frozen=True)
class SafeStrategyComponent(Component):
    """Add this Superwow consumable. No complex merging."""

    pass


@dataclass(frozen=True)
class EnhanceStrategyComponent(Component):
    """Enhance native counts with Superwow counts. Takes max of the two."""

    pass


@dataclass(frozen=True)
class OverwriteStrategyComponent(Component):
    """
    Superwow consumable overwrites a (potentially differently named) native consumable.
    Used to resolve ambiguous native consumables.
    Target can be a self reference
    Ambiguous consumables, by definition, can be targeted by multiple other consumables.
    """

    target_consumable_name: str  # The canonical name of the native consumable to overwrite.


@dataclass
class PriceComponent(Component):
    price: Union[NoPrice, DirectPrice, PriceFromIngredients]


@dataclass
class SuperwowComponent(Component):
    """Marker component for all Superwow consumables. Used as catch-all when merging"""

    pass


class ConsumableComponent(Component):
    pass


def SuperwowConsumable(name, price, spell_aliases, strategy):
    """Creates a superwow consumable with a strategy component and a marker component."""
    return Entity(
        name,
        components=[
            PriceComponent(price=price),
            SpellAliasComponent(spell_aliases=spell_aliases),
            strategy,
            SuperwowComponent(),
            ConsumableComponent(),
        ],
    )


def Consumable(name, price, spell_aliases=None):
    components = [PriceComponent(price=price), ConsumableComponent()]
    if spell_aliases:
        components.append(SpellAliasComponent(spell_aliases=spell_aliases))
    return Entity(name, components=components)


def Ingredient(name, price):
    """Creates a base ingredient entity for pricing purposes."""
    return Entity(name, components=[PriceComponent(price=price)])
