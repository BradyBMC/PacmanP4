from pacai.util.stack import Stack
from pacai.util.queue import Queue
from pacai.util.priorityQueue import PriorityQueue

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

    start = problem.startingState()
    visited = []

    stack = Stack()
    stack.push((start, []))

    while (not stack.isEmpty()):
        top = stack.pop()
        if problem.isGoal(top[0]):
            return top[1]
        if top[0] in visited:
            continue
        visited = visited + [top[0]]
        for neighbors in problem.successorStates(top[0]):
            if neighbors[0] not in visited:
                stack.push((neighbors[0], top[1] + [(neighbors[1])]))
    return ['South']

    raise NotImplementedError()

def breadthFirstSearch(problem):
    """
    Search the shallowest nodes in the search tree first. [p 81]
    """

    # *** Your Code Here ***

    visited = []
    queue = Queue()
    queue.push((problem.startingState(), []))
    while(not queue.isEmpty()):
        front = queue.pop()
        if problem.isGoal(front[0]):
            return front[1]
        if front[0] in visited:
            continue
        visited += [front[0]]
        for neighbors in problem.successorStates(front[0]):
            if neighbors[0] not in visited:
                queue.push((neighbors[0], front[1] + [neighbors[1]]))
    raise NotImplementedError()

def uniformCostSearch(problem):
    """
    Search the node of least total cost first.
    """

    # *** Your Code Here ***
    visited = []
    pq = PriorityQueue()
    best = None
    pq.push((problem.startingState(), [], 0), 0)
    while(not pq.isEmpty()):
        front = pq.pop()
        if problem.isGoal(front[0]):
            if best is None:
                best = front
            else:
                best = front if best[2] > front[2] else best
            continue
        if front[0] in visited or (best is not None and front[2] > best[2]):
            continue
        visited += [front[0]]
        for neighbors in problem.successorStates(front[0]):
            if neighbors not in visited:
                path = front[1] + [neighbors[1]]
                cost = problem.actionsCost(path)
                pq.push((neighbors[0], path, cost), cost)
    return best[1]

    raise NotImplementedError()

def aStarSearch(problem, heuristic):
    """
    Search the node that has the lowest combined cost and heuristic first.
    """

    # *** Your Code Here ***
    visited = []
    pq = PriorityQueue()
    pq.push((problem.startingState(), [], 0), 0)
    while(not pq.isEmpty()):
        front = pq.pop()
        if problem.isGoal(front[0]):
            return front[1]
        if front[0] in visited:
            continue
        visited += [front[0]]
        for neighbors in problem.successorStates(front[0]):
            if neighbors not in visited:
                path = front[1] + [neighbors[1]]
                gn = front[2] + neighbors[2]
                fn = gn + heuristic(neighbors[0], problem)
                pq.push((neighbors[0], path, gn), fn)

    raise NotImplementedError()
