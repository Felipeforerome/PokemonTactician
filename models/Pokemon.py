class Pokemon:
    def __init__(self, name, hp, att, deff, spatt, spdeff, spe, type1, type2):
        self.name = name
        self.hp = hp
        self.att = att
        self.deff = deff
        self.spatt = spatt
        self.spdeff = spdeff
        self.spe = spe
        self.learnedMoves = []
        self.moves = []
        self.type1 = type1
        self.type2 = type2
        self.knowableMoves = []

    def addKnowableMove(self, move):
        sameType = False
        if(move.power == 0):
            return

        for knownMove in self.knowableMoves:
            if(knownMove.type != move.type):
                continue
            else:
                sameType = True
                increasedPower = knownMove.power >= move.power
                increasedAccuracy = knownMove.accuracy >= move.accuracy
                increasedPP = knownMove.pp >= move.pp

                if(increasedPower and increasedAccuracy and increasedPP):
                    self.knowableMoves.remove(knownMove)
                    self.knowableMoves += move
                    return

        if(not sameType):
            self.knowableMoves += move


    def addMove(self, move):
        self.moves += move

    def expectedMoves(self):
        moves = self.moves
        expectedAttacks = []
        for move in moves:
            moveName = move.Name
            moveType = move.type
            movePower = move.power
            moveDamageClass = move.damageClass
            moveAccuracy = move.accuracy
            stab = 1.5 if (moveType == self.type1 or moveType == self.type2) else 1
            split = self.att if (moveDamageClass == "physical") else self.spatt
            expectedPower = (stab * movePower) * split * moveAccuracy
            expectedAttacks += (moveName, expectedPower)
        return expectedAttacks

    def learnMove(self, move, place=None):
        if(place==None):
            numberMoves = self.learnedMoves.__len__()
            if(numberMoves<4):
                self.learnedMoves[place] = move
            else:
                raise Exception("Missing Place Argument, This Pokemon Already Knows 4 Moves")

    def currentPower(self):
        currentPower = 0
        if self.learnedMoves.__len__() <1:
            raise Exception("This Pokemon Needs To Learn A Move")
        else:
            for learnedMove in self.learnedMoves:
                moveType = learnedMove.type
                movePower = learnedMove.power
                moveDamageClass = learnedMove.damageClass
                moveAccuracy = learnedMove.accuracy
                stab = 1.5 if (moveType == self.type1 or moveType == self.type2) else 1
                split = self.att if (moveDamageClass == "physical") else self.spatt
                expectedPower = (stab * movePower) * split * moveAccuracy
                currentPower += expectedPower
            return currentPower