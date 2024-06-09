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
    filterGames,
    filterGenerations,
    filterLegendaries,
    filterTypes,
    removeBattleOnly,
    removeMegas,
    splitPreSelected,
)

sys.path.append(sys.path[0] + "/..")
import time

from poketactician.glob_var import Q, alpha, beta, pokPreFilter, rho
from poketactician.MOACO import MOACO
from poketactician.objectives import (
    attack_obj_fun,
    self_coverage_fun,
    team_coverage_fun,
)


@callback(
    Output("time-to-calc", "children"),
    Output("team-output", "children", allow_duplicate=True),
    Output("blank-team-output", "hidden"),
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
        State({"type": "preSelect-selector", "suffix": ALL}, "value"),
        State("screen-width-store", "data"),
    ],
    prevent_initial_call=True,
)
def update_output(
    n,
    objFuncsParam,
    includedTypes,
    gens,
    games,
    monoType,
    legendaries,
    preSelected,
    screenWidth,
):
    if screenWidth and screenWidth > 768:
        (
            n,
            objFuncsParam,
            includedTypes,
            gens,
            games,
            monoType,
            legendaries,
            screenWidth,
        ) = (
            n[0],
            objFuncsParam[0],
            includedTypes[0],
            gens[0],
            games[0],
            monoType[0],
            legendaries[0],
            screenWidth,
        )
    elif screenWidth and screenWidth <= 768:
        (
            n,
            objFuncsParam,
            includedTypes,
            gens,
            games,
            monoType,
            legendaries,
            screenWidth,
        ) = (
            n[1],
            objFuncsParam[1],
            includedTypes[1],
            gens[1],
            games[1],
            monoType[1],
            legendaries[1],
            screenWidth,
        )
    else:
        return "", "", "", "", False
    if n is None:
        return "", "", "", "", False
    else:
        if len(objFuncsParam) > 0:
            try:
                preSelected = [int(p) - 1 for p in preSelected if p is not None]
                pokList = removeMegas(pokPreFilter)
                pokList = removeBattleOnly(pokList)
                preSelected, pokList = splitPreSelected(
                    pokList,
                    preSelected,
                )
                pokList = filterTypes(pokList, includedTypes, monoType)
                pokList = filterGenerations(pokList, gens)
                pokList = filterLegendaries(pokList, legendaries)
                pokList = filterGames(pokList, games)
                pokList = preSelected + pokList

                if len(pokList) == 0:
                    raise Exception(
                        "No pokemon available with current filter selection"
                    )
                start = time.time()
                objectiveFuncs = []
                attackObjFun = lambda team: attack_obj_fun(team, pokList)
                teamCoverageFun = lambda team: team_coverage_fun(team, pokList)
                selfCoverageFun = lambda team: self_coverage_fun(team, pokList)
                if 1 in objFuncsParam:
                    objectiveFuncs.append((attackObjFun, Q, 0.1))
                if 2 in objFuncsParam:
                    objectiveFuncs.append((teamCoverageFun, Q, 0.1))
                if 3 in objFuncsParam:
                    objectiveFuncs.append((selfCoverageFun, Q, rho))
                mCol = MOACO(
                    400,
                    objectiveFuncs,
                    pokList,
                    list(range(len(preSelected))),
                    alpha,
                    beta,
                )
                mCol.optimize(iters=25, time_limit=None)
                # mCol.optimize(iters=30, time_limit=None)
                team = mCol.getSoln()
                return (
                    "",
                    PokemonTeam(team.serialize()).layout(),
                    True,
                    [time.time() - start, mCol.getObjTeamValue()],
                    False,
                    False,
                )
            except Exception as e:
                return (str(e), "", True, "", "", False)
        else:
            return (no_update, no_update, no_update, no_update, no_update, no_update)


# Callback to insert the BlankPokemonTeam dynamically upon page load
@callback(Output("blank-team-output", "children"), Input("url", "pathname"))
def display_page(_):
    pokemon_list = [
        {"value": pok.id, "label": pok.name.title()} for pok in pokPreFilter
    ]
    return BlankPokemonTeam(pokemon_list).layout()


@callback(
    Output({"type": "objectives-multi-select", "suffix": MATCH}, "error"),
    Input({"type": "objectives-multi-select", "suffix": MATCH}, "value"),
    prevent_initial_call=True,
)
def select_value(value):
    return "Select at least 1." if len(value) < 1 else ""


@callback(
    Output("filter-drawer", "opened"),
    Input("filter-button", "opened"),
    prevent_initial_call=True,
)
def open(opened):
    return opened


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


clientside_callback(
    """
    function(trigger) {
        return window.innerWidth;
    }
    """,
    Output("screen-width-store", "data"),
    [
        Input("resize-listener", "n_clicks")
    ],  # This input is just a trigger; you might use dcc.Interval or dcc.Location if you want periodic or navigation-based triggers.
)
