import numpy as np
import random
from math import ceil
from collections import Counter


class Colony:
    def __init__(self, pop_sizeParam, objFuncParam, poks, alpha, beta, Q, rho):
        self.pop_size = pop_sizeParam
        # objFunParam should be a lambda function
        self.objFunc = objFuncParam

        # Filter Pokemon (now not filtering)
        self.poks = poks

        # Set Meta Params
        self.alpha = alpha
        self.beta = beta
        self.Q = Q
        self.rho = rho

        # Create Decision Space of Pokemon
        self.DS_Pok = np.arange(self.poks.__len__())

        # Create Decision Space of Attacks
        self.DS_Att = [np.arange(len(pok.knowableMoves)) for pok in self.poks]

        # Create Probability Vector for Pokemon
        self.Prob_Poks = np.ones(self.poks.__len__()) * (1 / self.poks.__len__())

        # Create Probability of Attacks
        self.Prob_Att = []
        for pok in self.poks:
            size = pok.knowableMoves.__len__()
            if size == 0:
                size = 1
            self.Prob_Att.append(np.ones(size) * (1 / size))

        # Create Pheromone Vector for Pokemon
        self.Ph_Pok = np.zeros(self.poks.__len__())

        # Create Pheromone of Attacks
        self.Ph_Atts = []
        for pok in self.poks:
            size = pok.knowableMoves.__len__()
            if size == 0:
                size = 1
            self.Ph_Atts.append(np.zeros(size))

        # Create Heuristic Value of Pokemon
        self.H_Poks = np.zeros(self.poks.__len__())
        i = 0
        for i in range(0, self.H_Poks.__len__()):
            self.H_Poks[i] = self.heuristicPokFun(self.poks, i)

        # Create Heuristic Value of Attack
        self.H_Atts = []
        for pok in self.poks:
            size = pok.knowableMoves.__len__()
            if size == 0:
                size = 1
            self.H_Atts.append(np.zeros(size))

        # Create Population
        self.Pop = np.ones([self.pop_size, 6, 5], dtype=int) * (-1)

        # Initial Run of the Meta-Heuristic
        self.ACO()

    def ACO(self):
        # Assign Population
        for ant in self.Pop:
            for pokemon in ant:
                selected_pokemon = False
                while not selected_pokemon:
                    rand_pokemon = random.random()
                    cumulative_prob = 0
                    selected_pokemon_id = 0

                    for idx, prob in enumerate(self.Prob_Poks):
                        cumulative_prob += prob
                        if rand_pokemon <= cumulative_prob:
                            selected_pokemon_id = idx
                            break

                    if selected_pokemon_id not in ant[:, 0]:
                        selected_pokemon = True
                        pokemon[0] = selected_pokemon_id

                        # Get Knowable Moves
                        prob_att_temp = self.Prob_Att[selected_pokemon_id].copy()
                        for i in range(1, 5):
                            if prob_att_temp.size - i > 0:
                                rand_att = random.random() * prob_att_temp.sum()
                                cumulative_att_prob = 0
                                selected_attack_id = 0

                                for att_id, att_prob in enumerate(prob_att_temp):
                                    cumulative_att_prob += att_prob
                                    if rand_att <= cumulative_att_prob:
                                        selected_attack_id = att_id
                                        break

                                pokemon[i] = selected_attack_id
                                prob_att_temp[selected_attack_id] = 0
                            else:
                                pokemon[i] = -1

    def updatePhCon(self, candidateSet):
        # User Defined Variables
        Q = self.Q
        rho = self.rho

        # Update Pheromone Concentration
        # Evaporate Pheromones
        self.Ph_Pok = (1 - rho) * self.Ph_Pok
        for idx, Ph_Att in enumerate(self.Ph_Atts):
            self.Ph_Atts[idx] = (1 - rho) * Ph_Att

        for ant in candidateSet:
            fitnessValue = self.fitness(ant)
            deltaConcentr = Q * fitnessValue
            for pokemon in ant:
                self.Ph_Pok[pokemon[0]] = self.Ph_Pok[pokemon[0]] + deltaConcentr
                if pokemon[1] >= 0:
                    self.Ph_Atts[pokemon[0]][pokemon[1]] = (
                        self.Ph_Atts[pokemon[0]][pokemon[1]] + deltaConcentr
                    )

                if pokemon[2] >= 0:
                    self.Ph_Atts[pokemon[0]][pokemon[2]] = (
                        self.Ph_Atts[pokemon[0]][pokemon[2]] + deltaConcentr
                    )

                if pokemon[3] >= 0:
                    self.Ph_Atts[pokemon[0]][pokemon[3]] = (
                        self.Ph_Atts[pokemon[0]][pokemon[3]] + deltaConcentr
                    )

                if pokemon[4] >= 0:
                    self.Ph_Atts[pokemon[0]][pokemon[4]] = (
                        self.Ph_Atts[pokemon[0]][pokemon[4]] + deltaConcentr
                    )

    def updatePokProb(self):
        # Update Pokemon Probabilities
        numeratorsPok = self.numeratorFun(self.Ph_Pok, self.H_Poks)
        denomPok = self.numeratorFun(self.Ph_Pok, self.H_Poks).sum()
        for i in range(0, self.Prob_Poks.__len__()):
            self.Prob_Poks[i] = numeratorsPok[i] / denomPok

        # Update Attack Probabilities
        numeratorsAtt = []
        denomAtt = []
        for Ph_Att, H_Att in zip(self.Ph_Atts, self.H_Atts):
            temp = self.numeratorFun(Ph_Att, H_Att)
            numeratorsAtt.append(temp)
            denomAtt.append(temp.sum())

        for i in range(0, numeratorsAtt.__len__()):
            for j in range(0, numeratorsAtt[i].__len__()):
                if denomAtt[i] > 0:
                    self.Prob_Att[i][j] = numeratorsAtt[i][j] / denomAtt[i]

    def fitness(self, ant):
        fitnessValue = self.objFunc(ant)
        return fitnessValue

    def heuristicPokFun(self, poks, pokIndex):
        heuristicValue = poks[pokIndex].overallStats() / 500
        return heuristicValue

    def candidateSet(self):
        popSorted = sorted(self.Pop, key=self.fitness)
        return list(popSorted[ceil(self.pop_size * 0.90) : self.pop_size])

    def numeratorFun(self, c, n):
        return (c**self.alpha) * (n**self.beta)


class ColonyGPT:
    def __init__(self, pop_sizeParam, objFuncParam, poks, alpha, beta, Q, rho):
        self.pop_size = pop_sizeParam
        # objFunParam should be a lambda function
        self.objFunc = objFuncParam

        # Filter Pokemon (now not filtering)
        self.poks = poks

        # Set Meta Params
        self.alpha = alpha
        self.beta = beta
        self.Q = Q
        self.rho = rho

        # Create Decision Space of Pokemon
        self.DS_Pok = np.arange(self.poks.__len__())

        # Create Decision Space of Attacks
        self.DS_Att = [np.arange(len(pok.knowableMoves)) for pok in self.poks]

        # Create Probability Vector for Pokemon
        self.Prob_Poks = np.ones(self.poks.__len__()) * (1 / self.poks.__len__())

        # Create Probability of Attacks
        self.Prob_Att = []
        for pok in self.poks:
            size = pok.knowableMoves.__len__()
            if size == 0:
                size = 1
            self.Prob_Att.append(np.ones(size) * (1 / size))

        # Create Pheromone Vector for Pokemon
        self.Ph_Pok = np.zeros(self.poks.__len__())

        # Create Pheromone of Attacks
        self.Ph_Atts = []
        for pok in self.poks:
            size = pok.knowableMoves.__len__()
            if size == 0:
                size = 1
            self.Ph_Atts.append(np.zeros(size))

        # Create Heuristic Value of Pokemon
        self.H_Poks = np.zeros(self.poks.__len__())
        i = 0
        for i in range(0, self.H_Poks.__len__()):
            self.H_Poks[i] = self.heuristicPokFun(self.poks, i)

        # Create Heuristic Value of Attack
        self.H_Atts = []
        for pok in self.poks:
            size = pok.knowableMoves.__len__()
            if size == 0:
                size = 1
            self.H_Atts.append(np.zeros(size))

        # Create Population
        self.Pop = np.ones([self.pop_size, 6, 5], dtype=int) * (-1)

        # Initial Run of the Meta-Heuristic
        self.ACO()

    def ACO(self):
        # Assign Population
        for ant in self.Pop:
            unique_poks = False
            while not unique_poks:
                rand_pokemon = np.random.random(size=self.Pop.shape[1])
                cumulative_probs = np.cumsum(self.Prob_Poks)
                selected_pokemon_ids = np.argmax(
                    rand_pokemon[:, np.newaxis] <= cumulative_probs, axis=1
                )
                if (
                    len(
                        [
                            item
                            for item, count in Counter(selected_pokemon_ids).items()
                            if count > 1
                        ]
                    )
                    < 1
                ):
                    unique_poks = True

            ant[:, 0] = selected_pokemon_ids

            for pokemon in ant:
                selected_pokemon_id = pokemon[0]
                # Get Knowable Moves
                prob_att_temp = self.Prob_Att[selected_pokemon_id].copy()
                for i in range(1, 5):
                    if prob_att_temp.size - i > 0:
                        rand_att = random.random() * prob_att_temp.sum()
                        cumulative_att_prob = np.cumsum(prob_att_temp)
                        selected_attack_id = np.argmax(rand_att <= cumulative_att_prob)

                        pokemon[i] = selected_attack_id
                        prob_att_temp[selected_attack_id] = 0
                    else:
                        pokemon[i] = -1

    def updatePhCon(self, candidateSet):
        # User Defined Variables
        Q = self.Q
        rho = self.rho
        # Update Pheromone Concentration
        # Evaporate Pheromones
        self.Ph_Pok = (1 - rho) * self.Ph_Pok
        for idx, Ph_Att in enumerate(self.Ph_Atts):
            self.Ph_Atts[idx] = (1 - rho) * Ph_Att

        for ant in candidateSet:
            fitnessValue = self.fitness(ant)
            deltaConcentr = Q * fitnessValue
            for pokemon in ant:
                self.Ph_Pok[pokemon[0]] = self.Ph_Pok[pokemon[0]] + deltaConcentr
                if pokemon[1] >= 0:
                    self.Ph_Atts[pokemon[0]][pokemon[1]] = (
                        self.Ph_Atts[pokemon[0]][pokemon[1]] + deltaConcentr
                    )

                if pokemon[2] >= 0:
                    self.Ph_Atts[pokemon[0]][pokemon[2]] = (
                        self.Ph_Atts[pokemon[0]][pokemon[2]] + deltaConcentr
                    )

                if pokemon[3] >= 0:
                    self.Ph_Atts[pokemon[0]][pokemon[3]] = (
                        self.Ph_Atts[pokemon[0]][pokemon[3]] + deltaConcentr
                    )

                if pokemon[4] >= 0:
                    self.Ph_Atts[pokemon[0]][pokemon[4]] = (
                        self.Ph_Atts[pokemon[0]][pokemon[4]] + deltaConcentr
                    )

    def updatePokProb(self):
        # Update Pokemon Probabilities
        numeratorsPok = self.numeratorFun(self.Ph_Pok, self.H_Poks)
        denomPok = self.numeratorFun(self.Ph_Pok, self.H_Poks).sum()
        if denomPok == 0:
            denomPok = 1
        for i in range(0, self.Prob_Poks.__len__()):
            self.Prob_Poks[i] = numeratorsPok[i] / denomPok

        # Update Attack Probabilities
        numeratorsAtt = []
        denomAtt = []
        for Ph_Att, H_Att in zip(self.Ph_Atts, self.H_Atts):
            temp = self.numeratorFun(Ph_Att, H_Att)
            numeratorsAtt.append(temp)
            denomAttTemp = temp.sum()
            if denomAttTemp == 0:
                denomAttTemp = 1
            denomAtt.append(denomAttTemp)

        for i in range(0, numeratorsAtt.__len__()):
            for j in range(0, numeratorsAtt[i].__len__()):
                if denomAtt[i] > 0:
                    self.Prob_Att[i][j] = numeratorsAtt[i][j] / denomAtt[i]

    def fitness(self, ant):
        fitnessValue = self.objFunc(ant)
        return fitnessValue

    def heuristicPokFun(self, poks, pokIndex):
        heuristicValue = poks[pokIndex].overallStats() / 500
        return heuristicValue

    def candidateSet(self):
        popSorted = sorted(self.Pop, key=self.fitness)
        return list(popSorted[ceil(self.pop_size * 0.90) : self.pop_size])

    def numeratorFun(self, c, n):
        return (c**self.alpha) * (n**self.beta)