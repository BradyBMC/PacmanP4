import random
from pacai.util import util
from pacai.util import reflection
from pacai.agents.capture.capture import CaptureAgent
from pacai.core import distanceCalculator, gamestate
from pacai.util import priorityQueue
from pacai.util.priorityQueue import PriorityQueue


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
            if action == 'Stop':
                actions.remove(action)

        values = [self.evaluate(gameState, a) for a in actions]
        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]
        return random.choice(bestActions)

    def evaluate(self, gameState, action):
        """
        Computes a linear combination of features and feature weights.
        """
        ghost = gameState.getAgentState(self.index).isGhost()
        enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        enemyPos = [
            a.getPosition()
            for a in enemies
            if (a.isPacman() and a.getPosition() is not None)
        ]
        if ghost and len(enemyPos) != 0:
            features = self.defFeatures(gameState, action)
            weights = self.getdefWeights(gameState, action)
        elif ghost and len(enemyPos) == 0:
            features = self.neutralFeatures(gameState, action)
            weights = self.getNeutralWeights(gameState, action)
        else:
            features = self.atkFeatures(gameState, action)
            weights = self.getatkWeights(gameState, action)
        stateEval = sum(features[feature] * weights[feature] for feature in features)
        return stateEval

    def getAlly(self, gameState):
        for index in self.getTeam(gameState):
            if self.index != index:
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
        newfoodList = self.getFood(successor).asList()

        # Pacman gathers the distance to all food
        if len(foodList) > 0:
            minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
            features["distanceToFood"] = minDistance
            if self.getFood(successor).asList() != foodList:
                features["distanceToFood"] *= -1

        # Pacman avoids being near ally
        ally = self.getAlly(successor)
        allyPos = successor.getAgentState(ally).getPosition()
        allyDist = self.getMazeDistance(myPos, allyPos)
        allyDist = 0.5 if allyDist == 0 else allyDist
        features["allyDist"] = 1 / allyDist

        # dist to enemy feature
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        """
        enemyPos = [a.getPosition() for a in enemies if (a.isGhost() and a.getPosition() is not None and a.isBraveGhost() is True)]
        if (len(enemyPos) > 0):
            minenemy = min([self.getMazeDistance(myPos, epos) for epos in enemyPos])
            features['enemyDist'] = 1.0 / minenemy
        else:
            minenemy = 99999999999999999.0
            features['enemyDist'] = minenemy
        """
        atkDefFlag = False
        minenemy = 999999.0
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
                if distToEnemy <= 3:
                    atkDefFlag == True

        features["enemyDist"] = 1.0 / minenemy if not atkDefFlag else 0.0
        features["scaredDefender"] = 999999.0 if atkDefFlag else 0.0

        closestFood = 999999
        foodCnt = self.getFood(gameState).count()
        futFoodCnt = successor.getFood().count()

        # Avoid dead ends
        if len(gameState.getLegalActions(self.index)) <= 2:
            features["deadend"] = 1.0
        else:
            features["deadend"] = 0.0

        # distance to enemy ghost
        if minenemy >= 4:
            if foodCnt == futFoodCnt:
                closestFood = features["distanceToFood"]
            closestFood = 1.0 / closestFood if closestFood != 0 else 0.0  # reciprocal
            features["enemyDist"] = -1.0 * closestFood

        # Pacman doesn't stop in enemy territory
        if oldPos == myPos:
            features["stop"] = 1
        else:
            features["stop"] = 0

        # Pacman distance to powerup pellet
        oldcapsule = gameState.getCapsules()
        capsule = successor.getCapsules()
        for cap in capsule:
            capsuleDist = self.getMazeDistance(myPos, cap)
            features["capsule"] = 1 / (1 if capsuleDist == 0 else capsuleDist)

        if oldcapsule > capsule:
            features["capsule"] = 0
            features["atecapsule"] = 1
        # If pacman powered up and ghost nearby, kill ghost

        return features

    def getatkWeights(self, gameState, action):
        """
        Returns a dict of weights for the state.
        The keys match up with the return from `ReflexCaptureAgent.getFeatures`.
        """
        return {
            "capsule": 100.0,
            "atecapsule": 60000.0,
            "deadend": -99999999.0,
            "stop": -999999.0,
            "enemyDist": -999999.0,
            "allyDist": -10000.0,
            "successorScore": 600.0,
            "distanceToFood": -100.0,
            "scaredDefender": 10000.0,
        }

    def nearestFood(self, gameState, myPos):
        low = 999999
        pos = None
        foodList = self.getFood(gameState).asList()
        for food in foodList:
            tmp = self.getMazeDistance(myPos, food)
            if low > tmp:
                low = tmp
                pos = food
        return pos

    def defFeatures(self, gameState, action):
        features = {}
        successor = self.getSuccessor(gameState, action)
        oldPos = gameState.getAgentState(self.index).getPosition()
        myPos = successor.getAgentState(self.index).getPosition()

        # Pacman avoids being near an ally
        # ally = self.getAlly(successor)
        # allyPos = successor.getAgentState(ally).getPosition()
        # allyDist = self.getMazeDistance(myPos, allyPos)
        # allyDist = 1 if allyDist == 0 else allyDist
        # features["allyDist"] = 1 / allyDist

        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        enemyPos = [
            a.getPosition()
            for a in enemies
            if (a.isPacman() and a.getPosition() is not None)
        ]

        # Number of invaders
        features["numInv"] = len(enemyPos)

        # Attack invaders
        if len(enemyPos) > 0 and not successor.getAgentState(self.index).isScared():
            minenemy = min([self.getMazeDistance(myPos, epos) for epos in enemyPos])
            features["invDist"] = 1 / (1 if minenemy == 0 else minenemy)

        # Attacks if ghost is scared and runs to nearest food
        elif len(enemyPos) > 0 and successor.getAgentState(self.index).isScared():
            foodPos = self.nearestFood(successor, myPos)
            newDist = self.getMazeDistance(myPos, foodPos)
            oldDist = self.getMazeDistance(oldPos, foodPos)
            if newDist < oldDist:
                features['runDown'] = 1
            else:
                features['runDown'] = 0
        return features

    def getdefWeights(self, gameState, action):
        return {
            "invDist": 500.0,
            "numInv": -5000.0,
            "allyDist": -500.0,
            "runDown": 100
        }

    def neutralFeatures(self, gameState, action):
        features = {}
        successor = self.getSuccessor(gameState, action)
        myPos = successor.getAgentState(self.index).getPosition()
        cornerDist = self.getMazeDistance(self.center(gameState), myPos)
        features["center"] = 1 / (1 if cornerDist == 0 else cornerDist)
        return features

    def getNeutralWeights(self, gameState, action):
        return {
            "center": 1000
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
            width += 1
        else:
            width -= 1
        last = None
        for y in range(height - 1, int(height / 3 * 2), -1):
            if not gameState.hasWall(width, y):
                last = (width, y)
        return last


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
            width += 1
        else:
            width -= 1
        last = None
        for y in range(1, int(height / 4)):
            if not gameState.hasWall(width, y):
                last = (width, y)
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
