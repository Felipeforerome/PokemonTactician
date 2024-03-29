from dash import (
    Input,
    Output,
    callback,
    State,
    no_update,
    clientside_callback,
    MATCH,
    ALL,
)
import sys
from components import PokemonTeam
import logging

sys.path.append(sys.path[0] + "/..")
from poketactician.MOACO import MOACO
from poketactician.Colony import Colony, Colony
from poketactician.glob_var import pokPreFilter, alpha, beta, Q, rho
from poketactician.objectives import (
    attack_obj_fun,
    team_coverage_fun,
    self_coverage_fun,
)
import time


@callback(
    Output("time-to-calc", "children"),
    Output("team-output", "children"),
    Output("memory-output", "data"),
    Output("filter-drawer", "opened", allow_duplicate=True),
    Output("filter-button", "opened", allow_duplicate=True),
    [
        Input({"type": "suggest-team-btn", "suffix": ALL}, "n_clicks"),
        State({"type": "objectives-multi-select", "suffix": ALL}, "value"),
        State({"type": "type-multi-select", "suffix": ALL}, "value"),
        State({"type": "mono-type", "suffix": ALL}, "checked"),
        State("screen-width-store", "data"),
    ],
    prevent_initial_call=True,
)
def update_output(n, objFuncsParam, includedTypes, monoType, screenWidth):
    if screenWidth and screenWidth > 768:
        n, objFuncsParam, includedTypes, monoType, screenWidth = (
            n[0],
            objFuncsParam[0],
            includedTypes[0],
            monoType[0],
            screenWidth,
        )
    elif screenWidth and screenWidth <= 768:
        n, objFuncsParam, includedTypes, monoType, screenWidth = (
            n[1],
            objFuncsParam[1],
            includedTypes[1],
            monoType[1],
            screenWidth,
        )
    else:
        return "", "", "", "", False
    if n is None:
        return "", "", "", "", False
    else:
        if len(objFuncsParam) > 0:
            try:
                if len(includedTypes) > 0:
                    pokList = (
                        [
                            pok
                            for pok in pokPreFilter
                            if (pok.type1 in includedTypes and pok.type2 is None)
                        ]
                        if monoType
                        else [
                            pok
                            for pok in pokPreFilter
                            if (
                                pok.type1 in includedTypes or pok.type2 in includedTypes
                            )
                        ]
                    )
                else:
                    pokList = (
                        [pok for pok in pokPreFilter if (pok.type2 is None)]
                        if monoType
                        else pokPreFilter
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
                    Colony,
                    400,
                    objectiveFuncs,
                    pokList,
                    alpha,
                    beta,
                )
                mCol.optimize(iters=25, time_limit=None)
                # mCol.optimize(iters=30, time_limit=None)
                team = mCol.getSoln()
                return (
                    "",
                    PokemonTeam(team.serialize()).layout(),
                    [time.time() - start, mCol.getObjTeamValue()],
                    False,
                    False,
                )
            except Exception as e:
                return (str(e), "", "", "", False)
        else:
            return (no_update, no_update, no_update, no_update, no_update)


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
