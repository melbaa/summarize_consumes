from __future__ import annotations
from typing import Any, Type, TypeVar, ItemsView, overload
from typing import NewType
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
    def from_string(cls, class_string: str) -> PlayerClass:
        # lowercase is the only extra processing. everything else should be an error
        return cls(class_string.lower())


CanonicalName = NewType("CanonicalName", str)


class Component:
    pass


C = TypeVar("C", bound=Component)
C1 = TypeVar("C1", bound=Component)
C2 = TypeVar("C2", bound=Component)
C3 = TypeVar("C3", bound=Component)
C4 = TypeVar("C4", bound=Component)


class ComponentRegistry:
    def __init__(self):
        self.store: dict[Type[Component], dict[Entity, Any]] = collections.defaultdict(dict)

    def get(self, component_class: Type[C]) -> dict[Entity, C]:
        return self.store[component_class]

    def set(self, component_class: Type[C], entity: Entity, component: C):
        self.store[component_class][entity] = component


COMPONENT_REGISTRY = ComponentRegistry()


class Entity:
    def __init__(self, name: str, components: list[Component]):
        name = CanonicalName(name)
        entity_unique_register(name, self)
        self.name = name  # The canonical name (what shows in the report output)
        self._components: list[Component] = list(components)
        for component in self._components:
            COMPONENT_REGISTRY.set(type(component), self, component)

    def add_component(self, component: Component):
        self._components.append(component)
        COMPONENT_REGISTRY.set(type(component), self, component)

    def get_components(self, component_type: Type[C]) -> list[C]:
        """Get all components of a given type."""
        return [c for c in self._components if isinstance(c, component_type)]

    def has_component(self, component_type: Type[Component]) -> bool:
        return self in COMPONENT_REGISTRY.get(component_type)

    def __repr__(self):
        return f"Entity(name={self.name!r}, components={self._components!r})"


ENTITY_REGISTRY: dict[CanonicalName, Entity] = {}


def entity_unique_register(name: CanonicalName, entity: Entity):
    if name in ENTITY_REGISTRY:
        raise ValueError(f"Duplicate entity name: {name}")
    ENTITY_REGISTRY[name] = entity


def get_entity_by_name(name: str) -> Entity:
    return ENTITY_REGISTRY[CanonicalName(name)]


def get_entities_with_component(component_type: Type[C]) -> ItemsView[Entity, C]:
    """Get all entities that have a component of the given type, and the component itself."""
    return COMPONENT_REGISTRY.get(component_type).items()


@overload
def get_entities_with_components(c1: Type[C1], /) -> list[tuple[Entity, tuple[C1]]]: ...


@overload
def get_entities_with_components(
    c1: Type[C1], c2: Type[C2], /
) -> list[tuple[Entity, tuple[C1, C2]]]: ...


@overload
def get_entities_with_components(
    c1: Type[C1], c2: Type[C2], c3: Type[C3], /
) -> list[tuple[Entity, tuple[C1, C2, C3]]]: ...


@overload
def get_entities_with_components(
    c1: Type[C1], c2: Type[C2], c3: Type[C3], c4: Type[C4], /
) -> list[tuple[Entity, tuple[C1, C2, C3, C4]]]: ...


def get_entities_with_components(
    *component_types: Type[Component],
) -> list[Any]:
    if not component_types:
        return []

    # intersecting a small set against a large one is much faster than vice versa.
    sorted_types = sorted(component_types, key=lambda t: len(COMPONENT_REGISTRY.get(t)))

    candidates = COMPONENT_REGISTRY.get(sorted_types[0]).keys()

    # dict_keys supports &
    for c_type in sorted_types[1:]:
        candidates &= COMPONENT_REGISTRY.get(c_type).keys()

    results: list[tuple[Entity, list[Component]]] = []
    for entity in candidates:
        comps = [COMPONENT_REGISTRY.get(t)[entity] for t in component_types]
        results.append((entity, comps))

    return results


@dataclass
class TrinketComponent(Component):
    triggered_by_spells: list[str] = field(default_factory=list)


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

    player_classes: list[PlayerClass]


@dataclass
class ReceiveBuffSpellComponent(Component):
    pass


SPELL_ALIAS_UNIQUE_CONSTRAINT: set[tuple[TreeType, str]] = set()


def spell_alias_unique_constraint(alias: tuple[TreeType, str]):
    if alias in SPELL_ALIAS_UNIQUE_CONSTRAINT:
        raise ValueError(f"Duplicate spell alias: {alias}")
    SPELL_ALIAS_UNIQUE_CONSTRAINT.add(alias)


@dataclass
class SpellAliasComponent(Component):
    # the aliases are used to map log names to this instance
    # used to rename from log names to the canonical name
    spell_aliases: list[tuple[TreeType, str]] = field(default_factory=list)

    def __post_init__(self):
        for alias in self.spell_aliases:
            if alias in SPELL_ALIAS_UNIQUE_CONSTRAINT:
                spell_alias_unique_constraint(alias)


@dataclass
class TrackSpellCastComponent(Component):
    pass


@dataclass
class TrackProcComponent(Component):
    pass


@dataclass
class ClassDetectionComponent(Component):
    player_class: PlayerClass
    triggered_by: list[tuple[TreeType, str]] = field(default_factory=list)
