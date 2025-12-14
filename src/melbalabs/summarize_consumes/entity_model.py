from typing import Tuple, Type, TypeVar, List, Set, Dict, ItemsView
from enum import Enum
from dataclasses import dataclass, field
import collections

from melbalabs.summarize_consumes.parser import TreeType


class PlayerClass(Enum):
    DRUID = "druid"
    HUNTER = "hunter"
    MAGE = "mage"
    PALADIN = "paladin"
    PRIEST = "priest"
    ROGUE = "rogue"
    SHAMAN = "shaman"
    WARLOCK = "warlock"
    WARRIOR = "warrior"
    UNKNOWN = "unknown"

    @classmethod
    def from_string(cls, class_string: str) -> "PlayerClass":
        # lowercase is the only extra processing. everything else should be an error
        return cls(class_string.lower())


class Component:
    pass


C = TypeVar("C", bound=Component)


COMPONENT_REGISTRY: Dict[Type[C], Dict["Entity", C]] = collections.defaultdict(dict)

ENTITY_UNIQUE_CONSTRAINT: Set[str] = set()


def entity_unique_constraint(name: str):
    if name in ENTITY_UNIQUE_CONSTRAINT:
        raise ValueError(f"Duplicate entity name: {name}")
    ENTITY_UNIQUE_CONSTRAINT.add(name)


class Entity:
    def __init__(self, name: str, components: List[Component]):
        entity_unique_constraint(name)
        self.name = name  # The canonical name (what shows in the report output)
        self._components: List[Component] = list(components)
        for component in self._components:
            COMPONENT_REGISTRY[type(component)][self] = component

    def add_component(self, component: Component):
        self._components.append(component)
        COMPONENT_REGISTRY[type(component)][self] = component

    def get_components(self, component_type: Type[C]) -> List[C]:
        """Get all components of a given type."""
        return [c for c in self._components if isinstance(c, component_type)]

    def has_component(self, component_type: Type[Component]) -> bool:
        return self in COMPONENT_REGISTRY[component_type]

    def __repr__(self):
        return f"Entity(name={self.name!r}, components={self._components!r})"


def get_entities_with_component(component_type: Type[C]) -> ItemsView[Entity, C]:
    """Get all entities that have a component of the given type, and the component itself."""
    return COMPONENT_REGISTRY[component_type].items()


def get_entities_with_components(
    *component_types: Type[Component],
) -> List[Tuple[Entity, List[Component]]]:
    if not component_types:
        return []

    # intersecting a small set against a large one is much faster than vice versa.
    sorted_types = sorted(component_types, key=lambda t: len(COMPONENT_REGISTRY[t]))

    candidates = COMPONENT_REGISTRY[sorted_types[0]].keys()

    # dict_keys supports &
    for c_type in sorted_types[1:]:
        candidates &= COMPONENT_REGISTRY[c_type].keys()

    results = []
    for entity in candidates:
        comps = [COMPONENT_REGISTRY[t][entity] for t in component_types]
        results.append((entity, comps))

    return results


@dataclass
class TrinketComponent(Component):
    pass


@dataclass
class InterruptSpellComponent(Component):
    pass


@dataclass
class RacialSpellComponent(Component):
    pass


@dataclass
class BuffSpellComponent(Component):
    pass


@dataclass
class ClassCooldownComponent(Component):
    """For CDSPELL_CLASS lists - class spells with cooldowns."""

    player_classes: List[PlayerClass]


@dataclass
class ReceiveBuffSpellComponent(Component):
    pass


SPELL_ALIAS_UNIQUE_CONSTRAINT: Set[Tuple[TreeType, str]] = set()


def spell_alias_unique_constraint(alias: Tuple[TreeType, str]):
    if alias in SPELL_ALIAS_UNIQUE_CONSTRAINT:
        raise ValueError(f"Duplicate spell alias: {alias}")
    SPELL_ALIAS_UNIQUE_CONSTRAINT.add(alias)


@dataclass
class SpellAliasComponent(Component):
    # the aliases are used to map log names to this instance
    # used to rename from log names to the canonical name
    spell_aliases: List[Tuple[TreeType, str]] = field(default_factory=list)

    def __post_init__(self):
        for alias in self.spell_aliases:
            if alias in SPELL_ALIAS_UNIQUE_CONSTRAINT:
                spell_alias_unique_constraint(alias)
