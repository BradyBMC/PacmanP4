import random
from pacai.util import util
from pacai.util import reflection
from pacai.agents.capture.capture import CaptureAgent
from pacai.core import distanceCalculator
from pacai.core.distance import manhattan

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

    def getSuccessor(self, gameState, action):
        successor = gameState.generateSuccessor(self.index, action)
        pos = successor.getAgentState(self.index).getPosition()
        if (pos != util.nearestPoint(pos)):
            # Only half a grid position was covered.
            return successor.generateSuccessor(self.index, action)
        else:
            return successor   

    def chooseAction(self, gameState):
        actions = gameState.getLegalActions(self.index)
        values = [self.evaluate(gameState, a) for a in actions]
        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]
        return random.choice(bestActions)

    def evaluate(self, gameState, action):
        """
        Computes a linear combination of features and feature weights.
        """
        features = self.getFeatures(gameState, action)
        weights = self.getWeights(gameState, action)
        stateEval = sum(features[feature] * weights[feature] for feature in features)
        return stateEval

    def isSafe(self, myPos, ePos, fPos):
        """
        Takes in current position, nearest enemy position and nearest food position
        Returns a bool if the enemy is further than the nearest food
        """
        safe = self.getMazeDistance(myPos, ePos) - self.getMazeDistance(myPos, fPos) * 2
        return safe > 0

    def getAlly(self):
        for index in self.getTeam():
            if self.index == index:
                return index

    def getFeatures(self, gameState, action):
        """
        Returns a dict of features for the state.
        The keys match up with the return from `ReflexCaptureAgent.getWeights`.
        """
        features = {}
        successor = self.getSuccessor(gameState, action)

        # successor score feature
        features['successorScore'] = self.getScore(successor)
        myPos = successor.getAgentState(self.index).getPosition()

        # distance to food feature
        foodList = self.getFood(gameState).asList()
        if (len(foodList) > 0):
            minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
            features['distanceToFood'] = minDistance
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        enemyPos = [a.getPosition() for a in enemies if a.isPacman() and a.getPosition() is not None]
        # enemyPos = self.getEnemyPosition(successor)
        if (len(enemyPos) > 0):
            minenemy = min([self.getMazeDistance(myPos, epos) for epos in enemyPos])

        return features

    def getWeights(self, gameState, action):
        """
        Returns a dict of weights for the state.
        The keys match up with the return from `ReflexCaptureAgent.getFeatures`.
        """
        return {
            'numInvaders': -1000,
            'onDefense': 100,
            'successorScore': 1.0,
            'distanceToFood': -1
        }

class atkAgent(MasterAgent):
    def __init__(self, index, **kwargs):
        super().__init__(index, **kwargs)

    def evaluate(self, gameState, action):
        """
        Computes a linear combination of features and feature weights.
        """
        features = self.atkFeatures(gameState, action)
        weights = self.getWeights(gameState, action)
        stateEval = sum(features[feature] * weights[feature] for feature in features)
        return stateEval

    def atkFeatures(self, gameState, action):
        """
        Ooga booga, goes forwards and gets food
        """
        features = {}
        successor = self.getSuccessor(gameState, action)

        # score feature
        features['successorScore'] = self.getScore(successor)
        myPos = successor.getAgentState(self.index).getPosition()

        # food feature
        futureFoodCnt = successor.getFood().count()
        foodList = self.getFood(gameState).asList()
        if (len(foodList) > 0):
            minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
            features['distanceToFood'] = minDistance

        # dist to enemy feature
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        enemyPos = [a.getPosition() for a in enemies if a.isGhost() and a.getPosition() is not None and a.isBraveGhost() is True]
        if (len(enemyPos) > 0):
            minenemy = min([self.getMazeDistance(myPos, epos) for epos in enemyPos])
            features['enemyDist'] = 1.0 / minenemy
        else:
            minenemy = 0.0
            features['enemyDist'] = minenemy

        closestFood = 999999
        foodCnt = self.getFood(gameState).count()
        futFoodCnt = successor.getFood().count()
        if minenemy >= 3:
            if foodCnt == futFoodCnt:
                closestFood = features['distanceToFood']
            closestFood = 1.0 / closestFood if closestFood != 0 else 0.0  # reciprocal
            features['enemyDist'] = closestFood
        # ally = successor.getAgentState(self.getAlly())
        # allyPos = successor.getAgentState(ally).getPosition()
        # allyDist = self.getMazeDistance(myPos, allyPos)
        # features['allyDist'] = 1/allyDist
        return features

    def getWeights(self, gameState, action):
        """
        Returns a dict of weights for the state.
        The keys match up with the return from `ReflexCaptureAgent.getFeatures`.
        """
        return {
            'enemyDist': -200,
            'allyDist': -100,
            'successorScore': 1.0,
            'distanceToFood': -100
        }

def createTeam(firstIndex, secondIndex, isRed,
        first = 'pacai.agents.capture.dummy.DummyAgent',
        second = 'pacai.agents.capture.dummy.DummyAgent'):
    """
    This function should return a list of two agents that will form the capture team,
    initialized using firstIndex and secondIndex as their agent indexed.
    isRed is True if the red team is being created,
    and will be False if the blue team is being created.
    """

    return [
        atkAgent(firstIndex),
        MasterAgent(secondIndex)
    ]
