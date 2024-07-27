from dataclasses import dataclass, field

from .Move import Move
from .Types import PokemonType


@dataclass
class Pokemon:
    """
    Represents a Pokemon with its attributes and moves.

    Attributes:
        id (int): The ID of the Pokemon.
        name (str): The name of the Pokemon.
        hp (int): The hit points of the Pokemon.
        att (int): The attack stat of the Pokemon.
        deff (int): The defense stat of the Pokemon.
        spatt (int): The special attack stat of the Pokemon.
        spdeff (int): The special defense stat of the Pokemon.
        spe (int): The speed stat of the Pokemon.
        type1 (PokemonType): The primary type of the Pokemon.
        type2 (PokemonType): The secondary type of the Pokemon.
        knowableMoves (list): The list of moves that the Pokemon can potentially learn.
        learntMoves (list): The list of moves that the Pokemon has learned.
        mythical (bool): Indicates if the Pokemon is mythical.
        legendary (bool): Indicates if the Pokemon is legendary.
        battleOnly (bool): Indicates if the Pokemon is only available in battles.
        mega (bool): Indicates if the Pokemon has a mega evolution.
        games (list): The list of games in which the Pokemon appears.

    Methods:
        addKnowableMove(move): Adds a move to the list of knowable moves.
        from_json(data): Creates a Pokemon instance from JSON data.
        serialize(): Serializes the Pokemon instance into a dictionary.
        serialize_instance(): Serializes the Pokemon instance into a dictionary.
        teachMove(index): Adds a knowable move to the learnt moves list.
        overallStats(): Calculates the sum of stats.
        current_power(): Calculates the current power of the Pokemon based on stats, attacks, and type.
        isRole(role_checker): Checks if the Pokemon fulfills a specific role.
    """

    id: int
    name: str
    hp: int
    att: int
    deff: int
    spatt: int
    spdeff: int
    spe: int
    type1: PokemonType
    type2: PokemonType
    mythical: bool
    legendary: bool
    battleOnly: bool
    mega: bool
    games: list = field(default_factory=list)
    knowableMoves: list = field(default_factory=list)
    learntMoves: list = field(default_factory=list)

    def addKnowableMove(self, move):
        """
        TODO This should be changed once more info about the moves is added, like effects or whatever. Right now it does reduce the decision space
        Adds move to list of knowable move if it has power greater to 0, its between the best 3 moves wtht that type and class
        :param move: Move to add
        """
        sameTypeClass = False
        sameTypeClassMoves = []
        numTypeClass = 0
        if move.power == 0:
            return

        for knownMove in self.knowableMoves:
            diffType = knownMove.type != move.type
            diffClass = knownMove.damageClass != move.damageClass
            if diffType or diffClass:
                continue
            else:
                numTypeClass = numTypeClass + 1
                sameTypeClassMoves.append(knownMove)
                lenTypeClassMoves = sameTypeClassMoves.__len__()

                if lenTypeClassMoves == 3:
                    sameTypeClass = True
                    sameTypeClassMoves.sort(key=lambda x: x.power * x.accuracy)
                    for knownTypeClass in sameTypeClassMoves:
                        increasedPowerAccuracy = (
                            knownTypeClass.power * knownTypeClass.accuracy
                            <= move.power * move.accuracy
                        )
                        increasedPP = knownMove.pp * 0.75 <= move.pp

                        if increasedPowerAccuracy:
                            if increasedPP or knownTypeClass.power + 30 <= move.power:
                                self.knowableMoves.remove(knownTypeClass)
                                self.knowableMoves.append(move)
                                return
                        else:
                            return

        if not sameTypeClass:
            self.knowableMoves.append(move)

    @classmethod
    def from_json(cls, data):
        """
        Creates a Pokemon instance from JSON data.

        :param data: The JSON data representing the Pokemon.
        :return: The created Pokemon instance.
        """
        pokemon = cls(
            data["id"],
            data["name"],
            data["hp"],
            data["att"],
            data["deff"],
            data["spatt"],
            data["spdeff"],
            data["spe"],
            PokemonType(data["type1"]),
            PokemonType(data["type2"]) if data["type2"] else None,
            data["mythical"],
            data["legendary"],
            data["battleOnly"],  # Include battleOnly attribute
            data["mega"],  # Include mega attribute
            data["games"],
        )
        moves = [Move.from_json(move_data) for move_data in data["knowableMoves"]]

        for move in moves:
            pokemon.addKnowableMove(move)
        return pokemon

    def serialize(self):
        """
        Serializes the Pokemon instance into a dictionary.

        :param pokemon: The Pokemon instance to serialize.
        :return: The serialized dictionary.
        """
        serialized_moves = [move.serialize() for move in self.knowableMoves]
        # Prevent empty move list
        if serialized_moves.__len__() == 0:
            serialized_moves.append(
                Move.from_json(
                    {
                        "id": "0",
                        "name": "no-move",
                        "type": "Normal",
                        "damageClass": "physical",
                        "power": 1,
                        "accuracy": 0,
                        "pp": 0,
                        "priority": 0,
                    }
                ).serialize()
            )
        return {
            "id": self.id,
            "name": self.name,
            "hp": self.hp,
            "att": self.att,
            "deff": self.deff,
            "spatt": self.spatt,
            "spdeff": self.spdeff,
            "spe": self.spe,
            "type1": self.type1,
            "type2": self.type2,
            "mythical": self.mythical,
            "legendary": self.legendary,
            "battleOnly": self.battleOnly,  # Include battleOnly attribute
            "mega": self.mega,  # Include battleOnly attribute
            "knowableMoves": serialized_moves,
            "games": self.games,  # Include games in serialized output
        }

    def serialize_instance(self):
        """
        Serializes the Pokemon instance into a dictionary.

        :return: The serialized dictionary.
        """
        serialized_moves = [move.serialize() for move in self.learntMoves]
        return {
            "id": self.id,
            "name": self.name,
            "hp": self.hp,
            "att": self.att,
            "deff": self.deff,
            "spatt": self.spatt,
            "spdeff": self.spdeff,
            "spe": self.spe,
            "type1": self.type1,
            "type2": self.type2,
            "mythical": self.mythical,
            "legendary": self.legendary,
            "battleOnly": self.battleOnly,  # Include battleOnly attribute
            "mega": self.mega,  # Include battleOnly attribute
            "moves": serialized_moves,
            "games": self.games,
        }

    def teachMove(self, int):
        """
        Adds a knowable move to the learnt moves list.

        :param int: The index of the knowable move to teach.
        """
        if len(self.learntMoves) < 4:
            self.learntMoves += [self.knowableMoves[int]]
        else:
            raise ValueError("Can't teach more than 4 moves")

    def overallStats(self):
        """
        Calculates the sum of stats.

        :return: The sum of stats.
        """
        return self.hp + self.att + self.deff + self.spatt + self.spdeff + self.spe

    def current_power(self):
        """
        Calculates the current power of the pokemon based on Stats, Attacks, and Type
        :return: Returns total power of the learned moves
        """
        currentPower = 0
        for learnedMove in self.learntMoves:
            moveType = learnedMove.type
            movePower = learnedMove.power
            moveDamageClass = learnedMove.damageClass
            moveAccuracy = learnedMove.accuracy
            stab = 1.5 if (moveType == self.type1 or moveType == self.type2) else 1
            split = self.att if (moveDamageClass == "physical") else self.spatt
            expectedPower = (stab * movePower) * split * moveAccuracy
            currentPower += expectedPower
        return currentPower

    def isRole(self, role_checker) -> bool:
        """
        Checks if the Pokemon fulfills a specific role.

        :param role_checker: A function that takes a Pokemon and returns True if the Pokemon fulfills a role.
        :return: True if the Pokemon fulfills the role, False otherwise.
        """
        return role_checker(self)
