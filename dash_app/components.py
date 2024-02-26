from dash import html, dcc
import dash_mantine_components as dmc

from dash_iconify import DashIconify


class PokemonCard:
    def __init__(self, title, content):
        self.title = title
        self.content = content

    def layout(self):
        return html.Div(
            children=[
                html.H4(self.title, className="card-title"),
                html.P(self.content, className="card-content"),
            ],
            className="card",
        )


class PokemonTeam:
    def __init__(self, pokemonList):
        self.pokemonCards = [
            dmc.Col(
                PokemonCard(
                    pokemon["name"].capitalize(),
                    f"{pokemon['type1'].capitalize()}{"" if pokemon['type2'] is None else "/"+pokemon['type2'].capitalize()}",
                ).layout(),
                span=4,
            )
            for pokemon in pokemonList
        ]

    def layout(self):
        return dmc.Grid(children=self.pokemonCards, className="team")
