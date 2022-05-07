from tkinter import W
from pacai.agents.learning.value import ValueEstimationAgent

class ValueIterationAgent(ValueEstimationAgent):
    """
    A value iteration agent.

    Make sure to read `pacai.agents.learning` before working on this class.

    A `ValueIterationAgent` takes a `pacai.core.mdp.MarkovDecisionProcess` on initialization,
    and runs value iteration for a given number of iterations using the supplied discount factor.

    Some useful mdp methods you will use:
    `pacai.core.mdp.MarkovDecisionProcess.getStates`,
    `pacai.core.mdp.MarkovDecisionProcess.getPossibleActions`,
    `pacai.core.mdp.MarkovDecisionProcess.getTransitionStatesAndProbs`,
    `pacai.core.mdp.MarkovDecisionProcess.getReward`.

    Additional methods to implement:

    `pacai.agents.learning.value.ValueEstimationAgent.getQValue`:
    The q-value of the state action pair (after the indicated number of value iteration passes).
    Note that value iteration does not necessarily create this quantity,
    and you may have to derive it on the fly.

    `pacai.agents.learning.value.ValueEstimationAgent.getPolicy`:
    The policy is the best action in the given state
    according to the values computed by value iteration.
    You may break ties any way you see fit.
    Note that if there are no legal actions, which is the case at the terminal state,
    you should return None.
    """

    def __init__(self, index, mdp, discountRate = 0.9, iters = 100, **kwargs):
        super().__init__(index, **kwargs)

        self.mdp = mdp
        self.discountRate = discountRate
        self.iters = iters
        self.values = {}  # A dictionary which holds the q-values for each state.

        # Compute the values here.
        # raise NotImplementedError()
        for state in mdp.getStates():
            self.values[state] = self.valueIteration(state, 0)

    def valueIteration(self, state, depth):
        if self.mdp.isTerminal(state) or depth == self.iters:
            return self.mdp.getReward(state, -1, -1)

        best = -999999
        for action in self.mdp.getPossibleActions(state):
            total = 0
            for trans_prob in self.mdp.getTransitionStatesAndProbs(state, action):
                total += trans_prob[1] * (self.mdp.getReward(state, -1, -1) + self.discountRate * self.valueIteration(trans_prob[0], depth + 1))
            best = max(best, total)
        if best == -999999:
            print("arr")
        return best

    def getValue(self, state):
        """
        Return the value of the state (computed in __init__).
        """

        return self.values.get(state, 0.0)

    def getAction(self, state):
        """
        Returns the policy at the state (no exploration).
        """

        return self.getPolicy(state)
    
    def getQValue(self, state, action):
        print(action)
        return None

    def getPolicy(self, state):
        return None