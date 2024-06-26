from .utils import (
    currentPower,
    getLearnedMoves,
    getWeakness,
    dominatedCandSet,
    getMoveWeakness,
    hoyerSparseness,
)

from functools import reduce, lru_cache
from .glob_var import moves, pokPreFilter
import numpy as np
from .models.Types import typeChart, typeOrder


def attack_obj_fun(team, pokList):
    return sum(
        list(
            map(
                lambda x: currentPower(
                    pokList[x[0]],
                    getLearnedMoves(pokList, x, [x[1], x[2], x[3], x[4]]),
                ),
                team,
            )
        )
    )


# def compute_weaknesses_and_coverage(team_types, typeChart):
#     num_types = typeChart.shape[0]
#     team_weaknesses = np.ones(num_types)  # Assume all types are covered initially
#     team_resistances = np.zeros(num_types)

#     for types in team_types:
#         pokemon_resistances = np.product(
#             typeChart[:, np.array([typeOrder.index(type_) for type_ in types])], axis=1
#         )
#         team_resistances += (pokemon_resistances < 1).astype(int)
#         team_weaknesses *= (pokemon_resistances > 1).astype(int)

#     C_W = np.sum(
#         team_resistances * (1 - team_weaknesses)
#     )  # Coverage against weaknesses
#     W = np.sum(1 - team_weaknesses)  # Number of unique weaknesses
#     R = np.sum(team_resistances)  # Total resistances
#     U_R = np.sum(team_resistances > 0)  # Unique resistances

#     return W, C_W, R, U_R


@lru_cache(maxsize=324)
def defense(types):
    defense = np.product(
        typeChart[:, np.array([typeOrder.index(type_) for type_ in types])], axis=1
    )
    return defense


def bin_weakness(vector):
    return (vector > 1).astype(int)


def bin_resistance(vector):
    return (vector < 1).astype(int)


def flatten_comprehension(matrix):
    return [item for row in matrix for item in row]


def CW(team_types):
    omega = np.sum([bin_resistance(defense(types)) for types in team_types], axis=0)
    return np.sum(
        [
            bin_weakness(defense(team_type))
            * (omega - bin_resistance(defense(team_type)))
            for team_type in team_types
        ]
    )


def team_coverage_fun(team, pokList):
    team_types = [
        tuple(
            pokType
            for pokType in [pokList[pok[0]].type1, pokList[pok[0]].type2]
            if pokType is not None
        )
        for pok in team
    ]
    # W, C_W, R, U_R = compute_weaknesses_and_coverage(team_types, typeChart)

    # Assuming equal weighting for simplicity, adjust alpha and beta as needed
    # alpha = 0.5
    # beta = 0.5

    # # Compute total score (T_S)
    # T_S = alpha * (C_W / W if W else 0) + beta * (R / U_R if U_R else 0)
    # Added the +1 at the end to avoid the result to be zero because to colony.updatePhCon needs a non-zero fitness value
    T_S = CW(team_types) * len(set(flatten_comprehension(team_types))) + 1

    return T_S


# (
#         1
#         / np.power(
#             np.ones_like(
#                 reduce(
#                     np.multiply, map(lambda x: getWeakness(pokPreFilter[x[0]]), team)
#                 )
#             )
#             * 2,
#             reduce(np.multiply, map(lambda x: getWeakness(pokPreFilter[x[0]]), team)),
#         ).mean()
#     )


# def team_type_coverage_fun(team):
#     total_weaknesses = 0
#     total_resistances = 0
#     types = []
#     for pokemon in team:
#     # Loop through each unique type
#     for pokemon in team:
#         for type_ in set(pokemon.types):
#             # Find the index of the type in the typeOrder list
#             type_index = typeOrder.index(type_)

#             # Calculate weaknesses and resistances using the typeChart
#             weaknesses = sum(typeChart[type_index] > 1)
#             resistances = sum(typeChart[type_index] < 1)

#             # Update total weaknesses and resistances
#             total_weaknesses += weaknesses
#             total_resistances += resistances

#     # Calculate the overall team type coverage score
#     team_coverage_score = total_resistances - total_weaknesses

#     return team_coverage_score


# TODO This function doesn't work, if used in MOACO the teams are definetly not good
def self_coverage_fun(team):
    return np.mean(
        [
            *map(
                lambda x: 1
                / (
                    np.power(
                        np.ones(18) * 2, getMoveWeakness(x[0], x[1:5]), dtype=np.float64
                    ).mean()
                ),
                team,
            )
        ]
    )
