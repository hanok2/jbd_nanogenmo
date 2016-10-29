import os, sys
import random

def randomChoiceWeighted( itemDict ):
    """
    Takes dictionary of { 'item' : weight }
    """
    total = 0.0
    for w in itemDict.values():
        total += w

    rr = random.uniform( 0.0, total )
    kk = itemDict.keys()
    random.shuffle(kk)

    rtot = 0.0
    for k in kk:
        if (rtot >= rr):
            return k

        rtot += itemDict[k]

    # safeguard, shouldn't happen
    return kk[-1]