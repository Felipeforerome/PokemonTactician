import sys

from components import BlankPokemonTeam, PokemonTeam
from dash import (
    ALL,
    MATCH,
    Input,
    Output,
    State,
    callback,
    clientside_callback,
    no_update,
)
from filters import (
    filter_games,
    filter_generations,
    filter_legendaries,
    filter_types,
    hand_removed,
    remove_battle_only,
    remove_megas,
    remove_totems,
    split_preselected,
)

sys.path.append(sys.path[0] + "/..")
import time

from utils import generate_move_list_and_selector_status

from poketactician.glob_var import Q, alpha, beta, pok_pre_filter, rho
from poketactician.MOACO import MOACO
from poketactician.models.Pokemon import Pokemon
from poketactician.objectives import ObjectiveFunctions, StrategyFunctions


def preprocess_moves(pre_selected_moves: list[int | None]) -> list[list[int]]:
    """
    Preprocess pre-selected moves into lists.
    """
    move_lists = [[] for _ in range(6)]
    for idx, move in enumerate(pre_selected_moves):
        if move is not None:
            move_lists[idx // 4].append(int(move))
    return move_lists


def filter_pokemon_list(
    pre_selected: list[int],
    included_types: list[str],
    mono_type: bool,
    generations: list[list[int]],
    include_legendaries: bool,
    games: list[str],
):
    """
    Apply filters to the Pokémon list.
    """
    pok_list = hand_removed(pok_pre_filter)
    pok_list = remove_megas(pok_list)
    pok_list = remove_battle_only(pok_list)
    pok_list = remove_totems(pok_list)
    pre_selected, pok_list = split_preselected(pok_list, pre_selected)
    pok_list = filter_types(pok_list, included_types, mono_type)
    pok_list = filter_generations(pok_list, generations)
    pok_list = filter_legendaries(pok_list, include_legendaries)
    pok_list = filter_games(pok_list, games)
    return pre_selected + pok_list


def define_objective_functions(
    obj_funcs_param: list[int], strategy: str, pok_list: list[Pokemon]
):
    """
    Define the objective functions for team optimization.
    """
    objective_funcs = []
    for objective_function in obj_funcs_param:
        objective_funcs.append(
            ObjectiveFunctions(objective_function).get_function(pok_list)
        )
    if strategy:
        objective_funcs.append(StrategyFunctions(strategy).get_function(pok_list))
    return objective_funcs


def optimize_team_selection(
    pok_list: list[Pokemon],
    pre_selected: list[int],
    pre_selected_moves_lists: list[list[int]],
    objective_funcs: list[tuple[callable, float, float]],
    roles: list[str],
):
    """
    Optimize team selection using MOACO algorithm.
    """
    m_col = MOACO(
        400,
        objective_funcs,
        pok_list,
        list(range(len(pre_selected))),
        pre_selected_moves_lists,
        alpha,
        beta,
        roles=roles,
    )

    m_col.optimize(iters=25, time_limit=None)
    return m_col.get_solution(), m_col.get_objective_value()


@callback(
    Output("time-to-calc", "children"),
    Output("team-output", "children", allow_duplicate=True),
    Output("blank-team-output", "hidden", allow_duplicate=True),
    Output("memory-output", "data"),
    Output("filter-drawer", "opened", allow_duplicate=True),
    Output("filter-button", "opened", allow_duplicate=True),
    [
        Input({"type": "suggest-team-btn", "suffix": ALL}, "n_clicks"),
        State({"type": "objectives-multi-select", "suffix": ALL}, "value"),
        State({"type": "type-multi-select", "suffix": ALL}, "value"),
        State({"type": "gen-multi-select", "suffix": ALL}, "value"),
        State({"type": "game-multi-select", "suffix": ALL}, "value"),
        State({"type": "mono-type", "suffix": ALL}, "checked"),
        State({"type": "legendaries", "suffix": ALL}, "checked"),
        State({"type": "strategy", "suffix": ALL}, "value"),
        State({"type": "roles", "suffix": ALL}, "value"),
        State({"type": "preSelect-selector", "suffix": ALL}, "value"),
        State({"type": "preSelect-move-selector", "suffix": ALL, "move": ALL}, "value"),
        State("screen-width-store", "data"),
    ],
    prevent_initial_call=True,
)
def update_output(
    n_clicks,
    obj_funcs_param,
    included_types,
    generations,
    games,
    mono_type,
    include_legendaries,
    strategy,
    roles,
    pre_selected,
    pre_selected_moves,
    screen_width,
):
    """
    Callback to update team output based on user selections and screen width.
    """
    pre_selected_moves_lists = preprocess_moves(pre_selected_moves)

    # Adjust parameters based on screen width
    if screen_width:
        idx = 0 if screen_width > 768 else 1
        n_clicks = n_clicks[idx]
        obj_funcs_param = obj_funcs_param[idx]
        included_types = included_types[idx]
        generations = generations[idx]
        games = games[idx]
        mono_type = mono_type[idx]
        include_legendaries = include_legendaries[idx]
        strategy = strategy[idx]
        roles = roles[idx]
    elif screen_width is None or n_clicks is None:
        return "", "", "", "", False

    # Check if there are objective functions selected
    if not obj_funcs_param:
        return no_update, no_update, no_update, no_update, no_update, no_update

    try:
        # Filter and process pre-selected moves
        pre_selected_moves_lists = [
            move_list
            for i, move_list in enumerate(pre_selected_moves_lists)
            if pre_selected[i]
        ]
        pre_selected = [int(p) - 1 for p in pre_selected if p is not None]

        # Apply filters to the Pokémon list
        pok_list = filter_pokemon_list(
            pre_selected,
            included_types,
            mono_type,
            generations,
            include_legendaries,
            games,
        )

        # Check if any Pokémon remain after filtering
        if not pok_list:
            raise ValueError("No Pokémon available with current filter selection")

        # Define objective functions
        objective_funcs = define_objective_functions(
            obj_funcs_param, strategy, pok_list
        )
        # Optimize team selection
        start_time = time.time()
        team, obj_value = optimize_team_selection(
            pok_list, pre_selected, pre_selected_moves_lists, objective_funcs, roles
        )
        elapsed_time = time.time() - start_time

        return (
            "",
            PokemonTeam(team.serialize()).layout(),
            True,
            [elapsed_time, obj_value],
            False,
            False,
        )
    except ValueError as ve:
        return str(ve), "", True, "", "", False
    except Exception as e:
        return str(e), "", True, "", "", False


#################### LAYOUT CALLBACKS ####################


# Callback to insert the BlankPokemonTeam dynamically upon page load
@callback(Output("blank-team-output", "children"), Input("url", "pathname"))
def display_page(_):
    pokemon_list = remove_megas(pok_pre_filter)
    pokemon_list = remove_battle_only(pokemon_list)
    pokemon_team = [
        {"value": pok.id, "label": pok.name.title()} for pok in pokemon_list
    ]
    return BlankPokemonTeam(pokemon_team).layout()


@callback(
    Output("team-output", "children", allow_duplicate=True),
    Output("blank-team-output", "hidden", allow_duplicate=True),
    Input({"type": "reset-team-btn", "suffix": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def restart_team(_):
    return [], False


# Callback to raise alert no Objective Function is selected
@callback(
    Output({"type": "objectives-multi-select", "suffix": MATCH}, "error"),
    Input({"type": "objectives-multi-select", "suffix": MATCH}, "value"),
    prevent_initial_call=True,
)
def select_value(value):
    return "Select at least 1." if len(value) < 1 else ""


# Callback to toggle the filter drawer
@callback(
    Output("filter-drawer", "opened"),
    Input("filter-button", "opened"),
    prevent_initial_call=True,
)
def open(opened):
    return opened


#################### PRESELECTED POKEMON AND MOVE CALLBACKS ####################
@callback(
    Output({"type": "preSelect-image", "suffix": MATCH}, "src"),
    Output({"type": "preSelect-move-selector", "suffix": MATCH, "move": 0}, "data"),
    Output({"type": "preSelect-move-selector", "suffix": MATCH, "move": 0}, "disabled"),
    Input({"type": "preSelect-selector", "suffix": MATCH}, "value"),
)
def preSelected_images(value):
    image = "/assets/qmark.png"
    if value:
        image = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{value}.png"
    return image, *generate_move_list_and_selector_status(value)


@callback(
    Output({"type": "preSelect-move-selector", "suffix": MATCH, "move": 1}, "data"),
    Output({"type": "preSelect-move-selector", "suffix": MATCH, "move": 1}, "disabled"),
    State({"type": "preSelect-selector", "suffix": MATCH}, "value"),
    Input({"type": "preSelect-move-selector", "suffix": MATCH, "move": 0}, "value"),
)
def preSelected_images(pok_id, move_id):
    return generate_move_list_and_selector_status(
        pok_id,
        [
            move_id,
        ],
    )


@callback(
    Output({"type": "preSelect-move-selector", "suffix": MATCH, "move": 2}, "data"),
    Output({"type": "preSelect-move-selector", "suffix": MATCH, "move": 2}, "disabled"),
    State({"type": "preSelect-selector", "suffix": MATCH}, "value"),
    State({"type": "preSelect-move-selector", "suffix": MATCH, "move": 0}, "value"),
    Input({"type": "preSelect-move-selector", "suffix": MATCH, "move": 1}, "value"),
)
def preSelected_images(
    pok_id,
    move_id_1,
    move_id_2,
):
    return generate_move_list_and_selector_status(pok_id, [move_id_1, move_id_2])


@callback(
    Output({"type": "preSelect-move-selector", "suffix": MATCH, "move": 3}, "data"),
    Output({"type": "preSelect-move-selector", "suffix": MATCH, "move": 3}, "disabled"),
    State({"type": "preSelect-selector", "suffix": MATCH}, "value"),
    State({"type": "preSelect-move-selector", "suffix": MATCH, "move": 0}, "value"),
    State({"type": "preSelect-move-selector", "suffix": MATCH, "move": 1}, "value"),
    Input({"type": "preSelect-move-selector", "suffix": MATCH, "move": 2}, "value"),
)
def preSelected_images(pok_id, move_id_1, move_id_2, move_id_3):
    return generate_move_list_and_selector_status(
        pok_id, [move_id_1, move_id_2, move_id_3]
    )


#################### CLIENTSIDE CALLBACKS ####################

# Track data
clientside_callback(
    """
    function(data){
        console.log(`Time to compute: ${data[0]} - Objective Value: ${data[1]}`);
        return ''
    }
    """,
    Output("placeholder", "children"),
    Input("memory-output", "data"),
    prevent_initial_call=True,
)

# Track screen width
clientside_callback(
    """
    function(trigger) {
        return window.innerWidth;
    }
    """,
    Output("screen-width-store", "data"),
    [Input("resize-listener", "n_clicks")],
)
