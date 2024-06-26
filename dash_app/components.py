import json

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import dcc, html
from dash_iconify import DashIconify


class PokemonCard:
    def __init__(
        self,
        pokemon: dict,
    ):
        self.pokemon = pokemon

    def layout(self):
        pokemon = self.pokemon
        return dmc.Card(
            children=[
                dmc.CardSection(
                    children=[
                        dmc.Center(
                            html.Img(
                                src=f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{pokemon['id']}.png",
                                height="40%",
                                width="40%",
                                style={"margin": "auto"},
                                id="hello",
                            )
                        ),
                        dmc.Center(  # Use dmc.Center for center alignment
                            dmc.Text(
                                pokemon["name"].replace("-", " ").title(),
                                weight=500,
                            ),
                        ),
                        dmc.Center(
                            dmc.Group(
                                children=[
                                    dmc.Image(
                                        src=f"/assets/{pokType}.png",
                                        width=30,
                                        alt=pokType.capitalize(),
                                    )
                                    for pokType in [pokemon["type1"], pokemon["type2"]]
                                    if pokType is not None
                                ]
                            )
                        ),
                    ],
                    withBorder=True,
                    inheritPadding=True,
                    py="xs",
                ),
                dmc.CardSection(
                    children=[
                        dmc.SimpleGrid(
                            cols=2,
                            children=[
                                dmc.Center(
                                    html.P(
                                        move["name"].replace("-", " ").title(),
                                        className="card-content",
                                    )
                                )
                                for move in pokemon["moves"]
                            ],
                        ),
                    ],
                    inheritPadding=True,
                    mt="sm",
                    pb="md",
                ),
            ],
            withBorder=True,
            shadow="sm",
            radius="md",
            className="pokemonCard",
        )


class PokemonTeam:
    def __init__(self, pokemonList):
        self.pokemonCards = [
            dmc.Col(
                PokemonCard(pokemon).layout(),
                md=4,
                span=12,
            )
            for pokemon in pokemonList
        ]

    def layout(self):
        return dmc.Grid(
            children=self.pokemonCards, className="team", justify="space-evenly"
        )


class BlankPokemonCard:
    def __init__(self, pokemonList: list, id: str):
        self.pokemonList = pokemonList
        self.id = id

    def layout(self):
        return dmc.Card(
            id=f"{self.id}-div",
            style={"overflow": "visible"},
            children=[
                dmc.CardSection(
                    children=[
                        dmc.Center(
                            html.Img(
                                id={"type": "preSelect-image", "suffix": self.id},
                                src=f"/assets/qmark.png",
                                height="40%",
                                width="40%",
                                style={"margin": "auto"},
                            )
                        ),
                        dmc.Center(  # Use dmc.Center for center alignment
                            dmc.Select(
                                id={"type": "preSelect-selector", "suffix": self.id},
                                placeholder="Select a Pokemon",
                                data=self.pokemonList,
                                searchable=True,
                                nothingFound="No pokemon found",
                                clearable=True,
                                dropdownPosition="bottom",
                            ),
                        ),
                    ],
                    withBorder=False,
                    inheritPadding=True,
                    py="xs",
                ),
                dmc.CardSection(
                    children=[
                        dmc.SimpleGrid(
                            cols=2,
                            children=[
                                dmc.Center(
                                    dmc.Select(
                                        id={
                                            "type": "preSelect-move-selector",
                                            "suffix": self.id,
                                            "move": move,
                                        },
                                        placeholder="Select a Pokemon",
                                        data=[],
                                        disabled=True,
                                        searchable=True,
                                        nothingFound="No move found",
                                        clearable=True,
                                        dropdownPosition="bottom",
                                    )
                                )
                                for move in range(4)
                            ],
                        ),
                    ],
                    inheritPadding=True,
                    mt="sm",
                    pb="md",
                ),
            ],
            withBorder=True,
            shadow="sm",
            radius="md",
            className="pokemonCard",
        )


class BlankPokemonTeam:
    def __init__(self, pokemonList):
        self.pokemonCards = [
            dmc.Col(
                BlankPokemonCard(pokemonList, f"card{i}").layout(),
                md=4,
                span=12,
            )
            for i in range(6)
        ]

    def layout(self):
        return dmc.Grid(
            children=self.pokemonCards,
            className="blank-team",
            justify="space-evenly",
        )


def filterComponents(suffix):
    games_dict = json.load(open("data/games.json", "r"))
    return [
        dmc.MultiSelect(
            label="Select Objectives",
            placeholder="",
            id={"type": "objectives-multi-select", "suffix": suffix},
            value=[1],
            data=[
                {"value": 1, "label": "Attack"},
                {"value": 2, "label": "Team Coverage"},
                # {"value": 3, "label": "Self Coverage"},
            ],
            style={"marginBottom": 10, "width": "95%"},
            required=True,
            withAsterisk=False,
        ),
        html.Br(),
        dmc.MultiSelect(
            label="Select Generations to Include",
            placeholder="Leave empty for all",
            id={"type": "gen-multi-select", "suffix": suffix},
            value=[],
            data=[
                {"value": [1, 151], "label": "Generation 1"},
                {"value": [151, 251], "label": "Generation 2"},
                {"value": [251, 386], "label": "Generation 3"},
                {"value": [387, 493], "label": "Generation 4"},
                {"value": [494, 649], "label": "Generation 5"},
                {"value": [650, 721], "label": "Generation 6"},
                {"value": [722, 809], "label": "Generation 7"},
                {"value": [810, 905], "label": "Generation 8"},
                {"value": [906, 1025], "label": "Generation 9"},
            ],
            style={"marginBottom": 10, "width": "95%"},
        ),
        html.Br(),
        dmc.MultiSelect(
            label="Select Types to Include",
            placeholder="Leave empty for all",
            id={"type": "type-multi-select", "suffix": suffix},
            value=[],
            searchable=True,
            nothingFound="No type found",
            clearable=True,
            data=[
                {"value": "normal", "label": "Normal"},
                {"value": "fire", "label": "Fire"},
                {"value": "water", "label": "Water"},
                {"value": "electric", "label": "Electric"},
                {"value": "grass", "label": "Grass"},
                {"value": "ice", "label": "Ice"},
                {"value": "fighting", "label": "Fighting"},
                {"value": "poison", "label": "Poison"},
                {"value": "ground", "label": "Ground"},
                {"value": "flying", "label": "Flying"},
                {"value": "psychic", "label": "Psychic"},
                {"value": "bug", "label": "Bug"},
                {"value": "rock", "label": "Rock"},
                {"value": "ghost", "label": "Ghost"},
                {"value": "dragon", "label": "Dragon"},
                {"value": "dark", "label": "Dark"},
                {"value": "steel", "label": "Steel"},
                {"value": "fairy", "label": "Fairy"},
            ],
            style={"marginBottom": 10, "width": "95%"},
        ),
        html.Br(),
        dmc.MultiSelect(
            label="Select Games to Include",
            placeholder="Leave empty for all",
            id={"type": "game-multi-select", "suffix": suffix},
            value=[],
            searchable=True,
            nothingFound="Game not found",
            clearable=True,
            data=[
                {
                    "value": games_dict[str(i)]["Game"],
                    "label": games_dict[str(i)]["Game"],
                }
                for i in range(len(games_dict))
            ],
            style={"marginBottom": 10, "width": "95%"},
        ),
        html.Br(),
        dmc.Switch(
            label="Only Mono-types?",
            offLabel="No",
            onLabel="Yes",
            checked=False,
            id={"type": "mono-type", "suffix": suffix},
        ),
        html.Br(),
        dmc.Switch(
            label="With Legendaries?",
            offLabel="No",
            onLabel="Yes",
            checked=False,
            id={"type": "legendaries", "suffix": suffix},
        ),
        html.Br(),
        dmc.Button(
            "Suggest Team",
            leftIcon=DashIconify(icon="ic:twotone-catching-pokemon"),
            color="indigo",
            id={"type": "suggest-team-btn", "suffix": suffix},
        ),
        html.Br(),
        html.Br(),
        dmc.Button(
            "Pre-Select",
            leftIcon=DashIconify(icon="solar:restart-bold"),
            color="indigo",
            id={"type": "reset-team-btn", "suffix": suffix},
        ),
    ]


navbarFilterComponents = filterComponents("navbar")
drawerFilterComponents = filterComponents("drawer")
