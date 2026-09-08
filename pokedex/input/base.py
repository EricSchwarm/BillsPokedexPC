"""Abstract interface for physical button input."""

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Callable


class Button(Enum):
    PREV = auto()
    NEXT = auto()
    VERSION = auto()
    REFRESH = auto()


class ButtonInput(ABC):
    @abstractmethod
    def on_press(self, button: Button, callback: Callable[[], None]) -> None:
        """Register a callback to run when the given button is pressed."""

    @abstractmethod
    def close(self) -> None:
        """Release GPIO resources."""
