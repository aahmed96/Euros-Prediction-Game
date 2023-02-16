#!/usr/bin/env python
# coding: utf-8

# In[28]:


def result_calc(score1,score2):
    if (score1 > score2):
        outcome = 'team A'
    elif (score1 < score2):
        outcome = 'team B'
    else:
        outcome = 'draw'
    return outcome

def multiplier(outcome,competetive):
    m_equal = [2,2.5,3] #if two sides are equal
    m_competetive = [1,3,4] #if heavy underdog

    if competetive is False:
        m = m_competetive
    else:
        m = m_equal

    if outcome == 'team A': #team A is predefined to be favorites
        multiplier = m[0]
    elif outcome == 'team B':
        multiplier = m[2]
    else:
        multiplier = m[1]
    return multiplier   

def point_calc(score1,score2,predict1,predict2,competetive):
    outcome = result_calc(score1,score2) #actual outcome
    prediction = result_calc(predict1,predict2) #predicted outcome
    
    if (score1 == predict1) and (score2 == predict2):
        m = multiplier(outcome,competetive)
        pts = m*6

    elif outcome == prediction:
        m = multiplier(outcome,competetive)
        pts = m*2
    
    else:
        pts = 0
    
    return pts


#knockout points computer
def computePoints(score1,score2,predict1,predict2,a_endtime,p_endtime,a_winner,p_winner):
    pts = 0

    #correct team to progress was predicted
    if a_winner == p_winner : 
        pts += 6

    # correct scoreline at fulltime was predicted
    if (score1 == predict1) and (score2 == predict2):
        pts += 6 
    
    #endtime points
    if a_endtime == p_endtime == 'Full-time':
        pts+=2
    elif (a_endtime !='Full-time') and (p_endtime !='Full-time'):
        pts+=4
        if a_endtime == p_endtime:
            pts+=2
        
    return pts
    

    

