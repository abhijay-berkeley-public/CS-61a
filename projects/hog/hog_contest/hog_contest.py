"""
This is a minimal contest submission file. You may also submit the full
hog.py from Project 1 as your contest entry.

Only this file will be submitted. Make sure to include any helper functions
from `hog.py` that you'll need here! For example, if you have a function to
calculate Free Bacon points, you should make sure it's added to this file
as well.

Don't forget: your strategy must be deterministic and pure.
"""
import sys

from functools import lru_cache
from hog import free_bacon, roll_dice, is_swap

memoize = lru_cache(None)
from decimal import Decimal as D

PLAYER_NAME = 'Abhijay' # Change this line!
K_MAX_DICE = 10
K_DICE_SIDES = 6 #Assume six sided dice. Lacking more info.
K_FINAL_SCORE = 100
K_MAX_RECURSION_DEPTH = 10000
if sys.getrecursionlimit() < K_MAX_RECURSION_DEPTH:
    sys.setrecursionlimit(K_MAX_RECURSION_DEPTH)

#Assume 6 sided dice
#Most of this is taken directly from DeNero's extra lecture...

@memoize
def ways_to_roll_score(score, num_dice):
    #DeNero described this in lecture
    if score < 0: return 0
    elif score == 0 and num_dice == 0:
        return 1
    elif score == 0:
        return 0
    else:
        return sum([ways_to_roll_score(score-i, num_dice-1) for i in range(2, K_DICE_SIDES+1)])

@memoize
def chance_to_roll_score(score, num_dice):
    if score == 1:
        return 1.0 - (pow(K_DICE_SIDES - 1, num_dice) / pow(K_DICE_SIDES, num_dice)) #100% - prob. all not ones
    return ways_to_roll_score(score, num_dice) / pow(K_DICE_SIDES, num_dice)

@memoize
def aggegrate_winning_probabilites_for_n(score, opponent_score, n):
    #Inspired by DeNero's extra lecture.
    if n == 0:
        return winning_probability_for_score(score + free_bacon(opponent_score), opponent_score)
    else:
        def score_incremental_winning_prob(s):
            return chance_to_roll_score(s, n) * winning_probability_for_score(score + s, opponent_score)
        winning_probs = [score_incremental_winning_prob(s) for s in range(1, (K_DICE_SIDES * n) + 1)]
        return sum(winning_probs)

@memoize
def winning_probability_for_score(score, opponent_score):
    if is_swap(score, opponent_score):
        score, opponent_score = opponent_score, score
    if score >= K_FINAL_SCORE:
        return 1
    elif opponent_score >= K_FINAL_SCORE:
        return 0
    else:
        probability_of_losing = aggegrate_winning_probabilites_for_n(
                opponent_score, score, opponent_strategy(score, opponent_score))
        return 1 - probability_of_losing

@memoize
def opponent_strategy(score, opponent_score):
    #assume he plays perfectly
    return optimal_num_dice(opponent_score, score)

@memoize
def optimal_num_dice(score, opponent_score):
    probabilites_of_winning = [
        aggegrate_winning_probabilites_for_n(score, opponent_score, n)
        for n in range(0,K_MAX_DICE+1)]
    highest_probability, best_num_dice = max(
        [(value,index) for index,value in enumerate(probabilites_of_winning)])
    return best_num_dice

@memoize
def final_strategy(score, opponent_score):
    return optimal_num_dice(score, opponent_score)