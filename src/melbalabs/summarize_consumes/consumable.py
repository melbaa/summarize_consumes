from dataclasses import dataclass
from typing import List
from typing import Tuple

@dataclass(frozen=True)
class ConsumableItem:
    """Models consumables"""

    # The canonical name of the consumable (what shows in the report output)
    name: str

    # base items have an empty list of components
    components: List[Tuple[str, float]]

    # Number of charges the item has (e.g. oils have 5 charges)
    charges: int = 1

    def __post_init__(self):
        if self.charges <= 0: raise ValueError('positive charges plz')


