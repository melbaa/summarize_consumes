import enum
from enum import Enum
from dataclasses import dataclass
from dataclasses import field
from typing import List
from typing import Tuple
from typing import Union

"""
types of consumables by availability in combat log
* not in combat log at all. they are base components for pricing other consumables
* in native log
* in superwow log [1]
* in both native and superwow log

[1] types of consumables in the superwow log
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


A design goal is to avoid having classes with optional attributes.
"""



@dataclass(frozen=True)
class NoPrice:
    pass


class ChargeValidation:
    def __post_init__(self):
        if self.charges <= 0: raise ValueError('positive charges plz')

@dataclass(frozen=True, kw_only=True)
class DirectPrice(ChargeValidation):

    itemid: int

    # Number of charges the item has (e.g. oils have 5 charges)
    charges: int = 1

    def __post_init__(self):
        super().__post_init__()
        if self.itemid is None: raise ValueError('itemid must be int')


@dataclass(frozen=True, kw_only=True)
class PriceFromComponents(ChargeValidation):

    charges: int = 1

    components: List[Tuple['Consumable', float]] = field(default_factory=list)



@dataclass(frozen=True, kw_only=True)
class Consumable:
    """Models consumables"""

    # The canonical name of the consumable (what shows in the report output)
    name: str

    price: Union[NoPrice, DirectPrice, PriceFromComponents]


    # maps line_type, spellname to the consumable
    spell_aliases: List[Tuple[str, str]] = field(default_factory=list)



class MergeStrategy(Enum):
    IGNORE = enum.auto()
    ENHANCE = enum.auto()
    OVERWRITE = enum.auto()

@dataclass(frozen=True, kw_only=True)
class SuperwowConsumable(Consumable):
    # the merge strategy used to reconcile with the native log counts
    strategy: MergeStrategy



