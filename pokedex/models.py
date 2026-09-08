"""Data models for the Pokedex."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Pokemon:
    number: int
    name: str
    generation: int
    height: int  # decimeters, per PokeAPI
    weight: int  # hectograms, per PokeAPI
    types: list[str]
