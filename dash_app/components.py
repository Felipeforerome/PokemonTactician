from dash import html, dcc
import dash_mantine_components as dmc

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
                                height="50%",
                                width="50%",
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
                                html.P(
                                    move["name"].replace("-", " ").title(),
                                    className="card-content",
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


def filterComponents(suffix):
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
            label="Select Types to Include",
            placeholder="Leave empty for all",
            id={"type": "type-multi-select", "suffix": suffix},
            value=[],
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
        dmc.Switch(
            label="Only Mono-types?",
            offLabel="No",
            onLabel="Yes",
            checked=False,
            id={"type": "mono-type", "suffix": suffix},
        ),
        html.Br(),
        dmc.Button(
            "Suggest Team",
            leftIcon=DashIconify(icon="ic:twotone-catching-pokemon"),
            color="indigo",
            id={"type": "suggest-team-btn", "suffix": suffix},
        ),
    ]


navbarFilterComponents = filterComponents("navbar")
drawerFilterComponents = filterComponents("drawer")
