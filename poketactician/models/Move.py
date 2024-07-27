from dataclasses import dataclass, field
from enum import Enum

from .Types import PokemonType


class DamageClass(Enum):
    PHYSICAL = "physical"
    SPECIAL = "special"
    STATUS = "status"


@dataclass
class Move:
    """
    Represents a move in the game.

    Attributes:
        id (str): The unique identifier of the move.
        name (str): The name of the move.
        type (PokemonType): The type of the move.
        damageClass (str): The damage class of the move.
        power (int): The power of the move.
        accuracy (int): The accuracy of the move.
        pp (int): The power points of the move.
        priority (int): The priority of the move.
    """

    id: str
    name: str
    type: PokemonType
    damageClass: str
    power: int = field(default=0)
    accuracy: int = field(default=1)
    pp: int
    priority: int

    def post_init(self):
        self.power = self.power if self.power is not None else 0
        self.accuracy = self.accuracy if self.accuracy is not None else 1

    @property
    def expected_power(self):
        return self.power * self.accuracy

    @classmethod
    def from_json(cls, moveJSON):
        return cls(
            moveJSON["id"],
            moveJSON["name"],
            PokemonType(moveJSON["type"]),
            DamageClass(moveJSON["damageClass"]),
            moveJSON["power"],
            moveJSON["accuracy"],
            moveJSON["pp"],
            moveJSON["priority"],
        )

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "damageClass": self.damageClass.value,
            "power": self.power,
            "accuracy": self.accuracy,
            "pp": self.pp,
            "priority": self.priority,
        }
