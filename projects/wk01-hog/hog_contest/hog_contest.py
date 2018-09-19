"""
This is a minimal contest submission file. You may also submit the full
hog.py from Project 1 as your contest entry.

Only this file will be submitted. Make sure to include any helper functions
from `hog.py` that you'll need here! For example, if you have a function to
calculate Free Bacon points, you should make sure it's added to this file
as well.

Don't forget: your strategy must be deterministic and pure.
"""

from functools import lru_cache
from hog import free_bacon, roll_dice, is_swap

memoize = lru_cache(None)
from decimal import Decimal as D

PLAYER_NAME = 'Abhijay' # Change this line!
K_MAX_DICE = 10
K_DICE_SIDES = 6 #Assume six sided dice. Lacking more info.

#Assume 6 sided dice
#Most of this is taken directly from DeNero's extra lecture...

@memoize
def optimal_num_dice(score, opponent_score):
    probabilites_of_winning = [
        aggegrate_winning_probabilites_for_n(score, opponent_score, n)
        for n in range(1,K_MAX_DICE+1)]
    highest_probability, best_num_dice = max(
        [(value,index + 1) for index,value in enumerate(probabilites_of_winning)])
    return best_num_dice

@memoize
def aggegrate_winning_probabilites_for_n(score, opponent_score, n):
    #Inspired by DeNero's extra lecture.

    probability_of_winning = 0
    if n == 0:
        probability_of_winning = winning_probability_for_score(score + free_bacon(opponent_score), opponent_score)
    else:
        def winning_probability_of_score(s):
            return probability_of_scoring(s, n) * winning_probability_for_score(score + s, opponent_score)
        winning_probs = [winning_probability_of_score(s) for s in range(1, (K_DICE_SIDES * n) + 1)]
        probability_of_winning = sum(winning_probs)
    return probability_of_winning

def number_of_ways_to_score(score, n):
    #DeNero basically described this in lecture
    if score < 0: return 0
    else if score == 0 and n == 0:
        return 1
    else if score == 0:
        return 0
    else:
        return sum([number_of_ways_to_score(score-i, n-1) for i in range(2, K_DICE_SIDES+1)])

def probability_of_scoring(k, n, s):
    if k == 1:
        return 1.0 - (pow(s - 1, n) / pow(s, n))
    return number_of_ways_to_score(k, n, s) / pow(s, n)

def probability_of_winning_with_turn_end_scores(score, opponent_score):
    if should_apply_swap(score, opponent_score):
        score, opponent_score = opponent_score, score
    if score >= GOAL_SCORE:
        return 1
    elif opponent_score >= GOAL_SCORE:
        return 0
    opponent_num_rolls = best_num_dice_to_roll(opponent_score, score)
    probability_of_opponent_winning = probability_of_winning_by_rolling_n(
            opponent_score, score, opponent_num_rolls)
    return 1 - probability_of_opponent_winning


def final_strategy(score, opponent_score):
    return optimal_num_dice(score, opponent_score)