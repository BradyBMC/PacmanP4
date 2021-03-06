# from tkinter import W
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

        states = mdp.getStates()
        # runs value iteration on all states
        for i in range(iters):
            # creates updatable copy
            copy = self.values.copy()
            for state in states:
                copy[state] = self.valueIteration(state)
            self.values = copy

    def valueIteration(self, state):
        vbest = -999999
        for actions in self.mdp.getPossibleActions(state):
            vnew = 0
            for sprime, prob in self.mdp.getTransitionStatesAndProbs(state, actions):
                # Set vk to zero incase terminal state
                vk = 0
                if state in self.values:
                    vk = self.values[sprime]
                # apply qvalue
                vnew += prob * (self.mdp.getReward(state, actions, sprime) + self.discountRate * vk)
            vbest = max(vbest, vnew)
        return 0 if vbest == -999999 else vbest

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
        sum = 0
        for sprime, prob in self.mdp.getTransitionStatesAndProbs(state, action):
            sum += prob * (self.mdp.getReward(state, action, sprime)
            + self.discountRate * self.values[sprime])
        return sum

    def getPolicy(self, state):
        best_action = None
        best = -999999
        # Searches through all actions and updates if a
        # better action is found
        for actions in self.mdp.getPossibleActions(state):
            sum = self.getQValue(state, actions)
            if best < sum:
                best = sum
                best_action = actions
        return best_action
