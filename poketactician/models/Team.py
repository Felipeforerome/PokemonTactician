class Team:
    def __init__(self):
        self.pokemons = []

    def addPokemon(self, pokemon):
        self.pokemons += [pokemon]

    def serialize(self):
        return [pokemon.serialize_instance() for pokemon in self.pokemons]
