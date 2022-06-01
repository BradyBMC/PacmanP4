import random
from pacai.util import util
# from pacai.util import reflection
from pacai.agents.capture.capture import CaptureAgent
# from pacai.core import distanceCalculator, gamestate
# from pacai.util import priorityQueue
# from pacai.util.priorityQueue import PriorityQueue


class MasterAgent(CaptureAgent):
    def __init__(self, index, **kwargs):
        super().__init__(index, **kwargs)

    def registerInitialState(self, gameState):
        """
        This method handles the initial setup of the agent and populates useful fields,
        such as the team the agent is on and the `pacai.core.distanceCalculator.Distancer`.

        IMPORTANT: If this method runs for more than 15 seconds, your agent will time out.
        """

        super().registerInitialState(gameState)

        # Your initialization code goes here, if you need any.

    def center(self, gameState):
        pass

    def getSuccessor(self, gameState, action):
        successor = gameState.generateSuccessor(self.index, action)
        pos = successor.getAgentState(self.index).getPosition()
        if pos != util.nearestPoint(pos):
            # Only half a grid position was covered.
            return successor.generateSuccessor(self.index, action)
        else:
            return successor

    def chooseAction(self, gameState):
        actions = gameState.getLegalActions(self.index)
        for action in actions:
            if action == "Stop":
                actions.remove(action)

        values = [self.evaluate(gameState, a) for a in actions]
        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]
        return random.choice(bestActions)

    def evaluate(self, gameState, action):
        """
        Computes a linear combination of features and feature weights.
        """
        ghost = gameState.getAgentState(self.index)
        enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        enemyPos = [
            a.getPosition()
            for a in enemies
            if (a.isPacman() and a.getPosition() is not None)
        ]
        if ghost.isGhost() and len(enemyPos) != 0 and ghost.isBraveGhost():
            features = self.defFeatures(gameState, action)
            weights = self.getdefWeights(gameState, action)
        elif ghost.isGhost() and len(enemyPos) == 0:
            features = self.neutralFeatures(gameState, action)
            weights = self.getNeutralWeights(gameState, action)
        else:
            features = self.atkFeatures(gameState, action)
            weights = self.getatkWeights(gameState, action)
        stateEval = sum(features[feature] * weights[feature] for feature in features)
        return stateEval

    def getAlly(self, gameState):
        for index in self.getTeam(gameState):
            if self.index == index:
                return index

    def atkFeatures(self, gameState, action):
        """
        Gets the closest food in enemy territory
        """
        features = {}
        successor = self.getSuccessor(gameState, action)
        features["successorScore"] = self.getScore(successor)
        myPos = successor.getAgentState(self.index).getPosition()
        oldPos = gameState.getAgentState(self.index).getPosition()
        foodList = self.getFood(gameState).asList()

        # Pacman avoids being near ally
        ally = self.getAlly(successor)
        allyPos = successor.getAgentState(ally).getPosition()
        allyDist = self.getMazeDistance(myPos, allyPos)
        allyDist = 0.5 if allyDist == 0 else allyDist
        features["allyDist"] = 1 / allyDist

        # Avoid dead ends
        if len(gameState.getLegalActions(self.index)) <= 2:
            features["deadend"] = 1.0
        else:
            features["deadend"] = 0.0

        # Pacman doesn't stop in enemy territory
        if oldPos == myPos:
            features["stop"] = 1
        else:
            features["stop"] = 0

        # Pacman gathers the distance to all food
        if len(foodList) > 0:
            minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
            features["distanceToFood"] = minDistance
            if self.getFood(successor).asList() != foodList:
                features["distanceToFood"] *= -1

        # dist to enemy feature
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        # enemyPos = [a.getPosition() for a in enemies if (a.isGhost() and 
        # a.getPosition() is not None and a.isBraveGhost() is True)]
        # if (len(enemyPos) > 0):
        #     minenemy = min([self.getMazeDistance(myPos, epos) for epos in enemyPos])
        #     features['enemyDist'] = 1.0 / minenemy
        # else:
        #     features['enemyDist'] = 0

        atkDefFlag = False
        minenemy = 999999.0
        minScaredEnemy = 999999.0
        for enemy in enemies:
            if (
                enemy.isGhost()
                and enemy.getPosition() is not None
                and enemy.isBraveGhost()
            ):
                distToEnemy = self.getMazeDistance(myPos, enemy.getPosition())
                if minenemy > distToEnemy:
                    minenemy = distToEnemy
            elif (
                enemy.isGhost()
                and enemy.getPosition() is not None
                and not enemy.isBraveGhost()
            ):
                distToEnemy = self.getMazeDistance(myPos, enemy.getPosition())
                if distToEnemy <= 4:
                    atkDefFlag is True
                    if distToEnemy < minScaredEnemy:
                        minScaredEnemy = distToEnemy

        features["enemyDist"] = 1.0 / minenemy if not atkDefFlag else 0.0
        features["scaredDefender"] = 1.0 / minScaredEnemy if atkDefFlag else 0.0
        features["distanceToFood"] = (
            1.0 / minScaredEnemy if atkDefFlag else features["distanceToFood"]
        )

        closestFood = 999999
        foodCnt = self.getFood(gameState).count()
        futFoodCnt = successor.getFood().count()

        # distance to enemy ghost
        if minenemy >= 4:
            if foodCnt == futFoodCnt:
                closestFood = features["distanceToFood"]
            closestFood = 1.0 / closestFood if closestFood != 0 else 0.0  # reciprocal
            features["enemyDist"] = -1.0 * closestFood

        # Pacman distance to powerup pellet
        # oldcapsule = gameState.getCapsules()
        # capsule = successor.getCapsules()
        # if len(capsule) > 0:
        #     for cap in capsule:
        #         capsuleDist = self.getMazeDistance(myPos, cap)
        #         features["capsule"] = 1 / (1 if capsuleDist == 0 else capsuleDist)
        # else:
        #     features["capsule"] = 0

        # if oldcapsule > capsule:
        #     features["capsule"] = 1
        #     features["atecapsule"] = 1

        return features

    def getatkWeights(self, gameState, action):
        """
        Returns a dict of weights for the state.
        The keys match up with the return from `ReflexCaptureAgent.getFeatures`.
        """
        return {
            "capsule": 1250.0,
            "atecapsule": 50000.0,
            "deadend": -9999999.0,
            "stop": -400.0,
            "enemyDist": -500.0,
            "allyDist": -4000.0,
            "successorScore": 800.0,
            "distanceToFood": -10.0,
            "scaredDefender": 10000.0,
        }

    def defFeatures(self, gameState, action):
        features = {}
        successor = self.getSuccessor(gameState, action)
        myPos = successor.getAgentState(self.index).getPosition()
        oldPos = gameState.getAgentState(self.index).getPosition()

        # attack invaders
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        enemyPos = [
            a.getPosition()
            for a in enemies
            if (a.isPacman() and a.getPosition() is not None)
        ]
        features["numInv"] = len(enemyPos)
        if len(enemyPos) > 0 and not successor.getAgentState(self.index).isScared():
            minenemy = min([self.getMazeDistance(myPos, epos) for epos in enemyPos])
            features["invDist"] = 1 / (1 if minenemy == 0 else minenemy)
        """
        if (
            successor.getAgentState(self.index).isGhost()
            and successor.getAgentState(self.index).isBraveGhost()
        ):
            if len(enemyPos) > 0:
                minenemy = min([self.getMazeDistance(myPos, epos) for epos in enemyPos])
                if minenemy <= 4:
                    features["invDist"] = minenemy
                else:
                    features["invDist"] = 0
            else:
                minenemy = 0
                features["invDist"] = 0
        else:
            features["invDist"] = 0
        if successor.getAgentState(self.index).isScaredGhost():
            if len(enemyPos) > 0:
                minenemy = min([self.getMazeDistance(myPos, epos) for epos in enemyPos])
                if minenemy <= 4:
                    features["scared"] = 99999.0
                else:
                    features["scared"] = 0
            else:
                features["scared"] = 0
        else:
            features["scared"] = 0
        """
        return features

    def getdefWeights(self, gameState, action):
        return {
            "invDist": 500.0,
            "numInv": -50000.0,
            "allyDist": -1000.0,
        }

    def neutralFeatures(self, gameState, action):
        features = {}
        successor = self.getSuccessor(gameState, action)
        myPos = successor.getAgentState(self.index).getPosition()
        cornerDist = self.getMazeDistance(self.center(gameState), myPos)
        features["center"] = 1 / (1 if cornerDist == 0 else cornerDist)

        # Pacman avoids being near ally
        ally = self.getAlly(successor)
        allyPos = successor.getAgentState(ally).getPosition()
        allyDist = self.getMazeDistance(myPos, allyPos)
        allyDist = 0.5 if allyDist == 0 else allyDist
        features["allyDist"] = 1 / allyDist

        # if an enemy ghost is near/camping the mid line then avoid it
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        enemyPos = [
            a.getPosition()
            for a in enemies
            if (a.isGhost() and a.getPosition() is not None)
        ]

        #if len(enemyPos) > 0 and not successor.getAgentState(self.index).isScared():
        if len(enemyPos) > 0:
            minenemy = min([self.getMazeDistance(myPos, epos) for epos in enemyPos])
            if minenemy <= 2:
                features["borderEnemy"] = 99999.0
            else:
                features["borderEnemy"] = 0.0
        return features

    def getNeutralWeights(self, gameState, action):
        return {
            "center": 1000, 
            "borderEnemy": -5000,
            "allyDist": -400
        }


class topAgent(MasterAgent):
    def __init__(self, index, **kwargs):
        super().__init__(index, **kwargs)

    def center(self, gameState):
        """
        Gets the top right corner food location
        """
        height = int(gameState.getInitialLayout().getHeight())
        width = int(gameState.getInitialLayout().getWidth() / 2)
        if self.red:
            width += 2
        else:
            width -= 2
        first = None
        for defDiv in range(int(height / 3 * 2), 1, -1):
            for y in range(height - 1, defDiv, -1):
                if not gameState.hasWall(width, y):
                    first = (width, y)
            if first != None:
                return first
        return first


class botAgent(MasterAgent):
    def __init__(self, index, **kwargs):
        super().__init__(index, **kwargs)

    def center(self, gameState):
        """
        Gets the top right corner food location
        """
        height = int(gameState.getInitialLayout().getHeight())
        width = int(gameState.getInitialLayout().getWidth() / 2)
        if self.red:
            width += 2
        else:
            width -= 2
        last = None
        for x in range(3, 1, -1):
            defDiv = x - 0.5
            for y in range(int(height / defDiv), 1, -1):
                if not gameState.hasWall(width, y):
                    last = (width, y)
            if last != None:
                return last
        return last

def createTeam(
    firstIndex,
    secondIndex,
    isRed,
    first="pacai.agents.capture.dummy.DummyAgent",
    second="pacai.agents.capture.dummy.DummyAgent",
):
    """
    This function should return a list of two agents that will form the capture team,
    initialized using firstIndex and secondIndex as their agent indexed.
    isRed is True if the red team is being created,
    and will be False if the blue team is being created.
    """

    return [topAgent(firstIndex), botAgent(secondIndex)]
