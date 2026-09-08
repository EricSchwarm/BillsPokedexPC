"""Data models for the Pokedex."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Pokemon:
    number: int
    name: str
    generation: int
    height: int  # decimeters, per PokeAPI
    weight: int  # hectograms, per PokeAPI
    genus: str  # e.g. "Seed Pokemon"
    types: list[str]
