from dataclasses import dataclass

@dataclass(frozen=True)
class ConsumableItem:
    """Models consumables"""

    # The canonical name of the consumable (what shows in the report output)
    name: str

    # Number of charges the item has (e.g. oils have 5 charges)
    charges: int = 1

