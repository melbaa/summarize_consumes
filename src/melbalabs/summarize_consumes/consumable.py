from dataclasses import dataclass
from dataclasses import field
from typing import List
from typing import Tuple

@dataclass(frozen=True)
class ConsumableItem:
    """Models consumables"""

    # The canonical name of the consumable (what shows in the report output)
    name: str

    # self referential components. empty list by default for base components
    components: List[Tuple["ConsumableItem", float]] = field(default_factory=list)

    # Number of charges the item has (e.g. oils have 5 charges)
    charges: int = 1

    def __post_init__(self):
        if self.charges <= 0: raise ValueError('positive charges plz')


