from pacai.util.stack import Stack
from pacai.util.queue import Queue

"""
In this file, you will implement generic search algorithms which are called by Pacman agents.
"""

def depthFirstSearch(problem):   
    """
    Search the deepest nodes in the search tree first [p 85].

    Your search algorithm needs to return a list of actions that reaches the goal.
    Make sure to implement a graph search algorithm [Fig. 3.7].

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:
    ```
    print("Start: %s" % (str(problem.startingState())))
    print("Is the start a goal?: %s" % (problem.isGoal(problem.startingState())))
    print("Start's successors: %s" % (problem.successorStates(problem.startingState())))


    Return list a of strings, ie actions
    ```
    """
    # *** Your Code Here ***

    #print(type(problem))
    #print("What is passed to the func? %s" % problem)
    #print("Is the start a goal?: %s" % (problem.isGoal(problem.startingState())))
    #print("Start: %s" % (str(problem.startingState())))
    #print("Start's successors: %s" % (problem.successorStates(problem.startingState())))
    #temp = problem.successorStates(problem.startingState())[0]
    #print(problem.successorStates(temp[0]))

    start = problem.startingState()
    visited = []

    stack = Stack()
    stack.push((start,[]))

    while (not stack.isEmpty()):
        top = stack.pop()
        if problem.isGoal(top[0]):
            return top[1]
        if top[0] in visited:
            pass
        visited = visited + [top[0]]
        for neighbors in problem.successorStates(top[0]):
            if neighbors[0] not in visited:
                stack.push((neighbors[0],top[1] + [(neighbors[1])]))
    
    #Base Case
    return ['South']

    raise NotImplementedError()

def breadthFirstSearch(problem):
    """
    Search the shallowest nodes in the search tree first. [p 81]
    """

    # *** Your Code Here ***

    visited = []
    queue = Queue()
    queue.push((problem.startingState(),[]))
    while(not queue.isEmpty()):
        front = queue.pop()
        if problem.isGoal(front[0]):
            return front[1]
        if front[0] in visited:
           pass
        visited += [front[0]]
        for neighbors in problem.successorStates(front[0]):
            if neighbors[0] not in visited:
                queue.push((neighbors[0],front[1] + [neighbors[1]]))


    raise NotImplementedError()

def uniformCostSearch(problem):
    """
    Search the node of least total cost first.
    """

    # *** Your Code Here ***
    raise NotImplementedError()

def aStarSearch(problem, heuristic):
    """
    Search the node that has the lowest combined cost and heuristic first.
    """

    # *** Your Code Here ***
    raise NotImplementedError()
