import random
from pacai.util import util
from pacai.util import reflection
from pacai.agents.capture.capture import CaptureAgent
from pacai.core import distanceCalculator
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
    
    def CornerFood(self, foodList):
        pass

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
        ghost = gameState.getAgentState(self.index).isGhost()
        if ghost:
            features = self.defFeatures(gameState, action)
            weights = self.getdefWeights(gameState, action)
        else:
            features = self.atkFeatures(gameState, action)
            weights = self.getatkWeights(gameState, action)
        stateEval = sum(features[feature] * weights[feature] for feature in features)
        return stateEval

    def isSafe(self, myPos, ePos, fPos):
        """
        Takes in current position, nearest enemy position and nearest food position
        Returns a bool if the enemy is further than the nearest food
        """
        safe = self.getMazeDistance(myPos, ePos) - self.getMazeDistance(myPos, fPos) * 2
        return safe > 0

    def getAlly(self, gameState):
        for index in self.getTeam(gameState):
            if self.index == index:
                return index
    def atkFeatures(self, gameState, action):
        """
        Ooga booga, goes forwards and gets food
        """
        features = {}
        successor = self.getSuccessor(gameState, action)
        features['successorScore'] = self.getScore(successor)
        myPos = successor.getAgentState(self.index).getPosition()
        foodList = self.getFood(gameState).asList()

        newfoodList = self.getFood(successor).asList()
        if len(foodList) < len(newfoodList):
            features['eat'] = 1
        else:
            features['eat'] = 0

        if (len(foodList) > 0):
            minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
            features['distanceToFood'] = minDistance
            if self.getFood(successor).asList() != foodList:
                features['distanceToFood'] *= -1

        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        enemyPos = [a.getPosition() for a in enemies if a.isGhost() and a.getPosition() is not None]

        ally = self.getAlly(successor)
        allyPos = successor.getAgentState(ally).getPosition()
        allyDist = self.getMazeDistance(myPos, allyPos)
        allyDist = .5 if allyDist == 0 else allyDist
        features['allyDist'] = 1/allyDist

        # cornerDist = self.getMazeDistance(self.CornerFood(foodList), myPos)
        # features['cornerFood'] = 1/(1 if cornerDist == 0 else cornerDist)

        # dist to enemy feature
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        enemyPos = [a.getPosition() for a in enemies if a.isGhost() and a.getPosition() is not None]
        enemyPositions = []
        
        if len(enemyPos) > 0:
            for enemy in enemies:
                if enemy.isGhost() and enemy.getPosition() is not None:
                    if enemy.isBraveGhost():
                        minenemy = -999999
                        enemyPositions.append(-999999)
                    else:
                        minenemy = self.getMazeDistance(myPos, enemy.getPosition())
                        enemyPositions.append(minenemy)
                else:
                    minenemy = 999999
            features['enemyDist'] = 1.0 / min(enemyPositions) if len(enemyPositions) != 0 else 0.0
        else:
            features['enemyDist'] = 0.0

        closestFood = 999999
        foodCnt = self.getFood(gameState).count()
        futFoodCnt = successor.getFood().count()

        if minenemy < 3:
            if len(gameState.getLegalActions(self.index)) == 2:
                features['deadend'] = -1
            else:
                features['deadend'] = 0

        if minenemy >= 3:
            if foodCnt == futFoodCnt:
                closestFood = minDistance
            closestFood = 1.0 / closestFood if closestFood != 0 else 0.0  # reciprocal
            features['enemyDist'] = closestFood
        return features

    def getatkWeights(self, gameState, action):
        """
        Returns a dict of weights for the state.
        The keys match up with the return from `ReflexCaptureAgent.getFeatures`.
        """
        return {
            'deadend': -999999.0,
            'eat': 100,
            # 'cornerFood': 900.0,
            'enemyDist': -1000.0,
            'allyDist': -10000.0,
            'successorScore': 1.0,
            'distanceToFood': -1.0
        }

    def defFeatures(self, gameState, action):
        features = {}
        successor = self.getSuccessor(gameState, action)
        myPos = successor.getAgentState(self.index).getPosition()
        foodList = self.getFood(gameState).asList()
        cornerDist = self.getMazeDistance(self.CornerFood(foodList), myPos)
        features['cornerFood'] = 1/(1 if cornerDist == 0 else cornerDist)
        return features

    def getdefWeights(self, gameState, action):
        return {
            'cornerFood': 900.0
        }

class topAgent(MasterAgent):
    def __init__(self, index, **kwargs):
        super().__init__(index, **kwargs)

    def CornerFood(self, foodList):
        """
        Gets the top right corner food location
        """
        food = foodList[0]
        for dot in foodList:
            if dot[0] > food[0] and dot[1] > food[1]:
                food = dot
        return food

class botAgent(MasterAgent):
    def __init__(self, index, **kwargs):
        super().__init__(index, **kwargs)

    def CornerFood(self, foodList):
        """
        Gets the top right corner food location
        """
        food = foodList[0]
        for dot in foodList:
            if dot[0] > food[0] and dot[1] < food[1]:
                food = dot
        return food

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
        topAgent(firstIndex),
        botAgent(secondIndex)
    ]
