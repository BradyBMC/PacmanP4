"""
Analysis question.
Change these default values to obtain the specified policies through value iteration.
If any question is not possible, return just the constant NOT_POSSIBLE:
```
return NOT_POSSIBLE
```
"""

NOT_POSSIBLE = None

def question2():
    """
    [Enter a description of what you did here.]
    I reduced the the noise to zero so there isn't a chance
    of the ai moving the wrong direction
    """

    answerDiscount = 0.9
    answerNoise = 0

    return answerDiscount, answerNoise

def question3a():
    """
    [Enter a description of what you did here.]
    With noise at zero, will always take the
    shortest route bc no risk
    """

    answerDiscount = 0.2
    answerNoise = 0
    answerLivingReward = 0.4

    return answerDiscount, answerNoise, answerLivingReward

def question3b():
    """
    [Enter a description of what you did here.]
    Reduced the reward enough to the point the
    closer exit was worth more
    """

    answerDiscount = 0.2
    answerNoise = 0.2
    answerLivingReward = 0.1

    return answerDiscount, answerNoise, answerLivingReward

def question3c():
    """
    [Enter a description of what you did here.]
    Chaned noise to zero, so there is no
    risk to take the shortest path
    """

    answerDiscount = 0.9
    answerNoise = 0
    answerLivingReward = 0.0

    return answerDiscount, answerNoise, answerLivingReward

def question3d():
    """
    [Enter a description of what you did here.]
    Didn't change anything
    """

    answerDiscount = 0.9
    answerNoise = 0.2
    answerLivingReward = 0.0

    return answerDiscount, answerNoise, answerLivingReward

def question3e():
    """
    [Enter a description of what you did here.]
    Didn't change anything
    """

    answerDiscount = 0.9
    answerNoise = 0.2
    answerLivingReward = 0.0

    return answerDiscount, answerNoise, answerLivingReward

def question6():
    """
    [Enter a description of what you did here.]
    I tried epsilon at 0 and minimizing the learning rate
    but there will never be enough utiltiy to traverse
    across the bridge. The only time it will try to travers
    is if it randomly makes it across which won't happen 
    enough times in 50 iterations to be consistent.
    """

    return NOT_POSSIBLE

if __name__ == '__main__':
    questions = [
        question2,
        question3a,
        question3b,
        question3c,
        question3d,
        question3e,
        question6,
    ]

    print('Answers to analysis questions:')
    for question in questions:
        response = question()
        print('    Question %-10s:\t%s' % (question.__name__, str(response)))
