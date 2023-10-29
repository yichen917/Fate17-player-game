"""
This module implements a fate17 player related to the course
    Computer Programming, S18
by J.-L. Huang
May 2018

v0  20180511
    A random player.
v1  20180522
    Still a random player. Documentation added.
v2 20180524
    Cards are graded to assist decision making.
    Also fix the bug that the host didn't give back replacement cards.
v2.1 20180527
    Get opponent's cards before getting the game result.
"""



import random


name = 'Marcus' # make decisions according to "S"core
ANTE = 5

def analyzeHand(cards):
    """
    20180524
    Grade the a fate17 game hand.
    The score can be used to decide the winning hand; its value doesn't reflect its rareness.

    cards: a list or set of five cards.
        The 17 possible cards are 'J' and {'S','H','D','C'} x {'A','K','Q','J'}.
    
    Returns:
        This function returns a tuple (score, category).
        The ranges of possible categories are as follows.
        90000: five card
        80000: royal straight flush
        >= 70000: four card
        >= 60000: full house
        >= 50000: straight
        >= 40000: three card
        >= 30000: two pair
        >= 20000: one pair
    """
    rankWeight = {'A': 8, 'K': 6, 'Q': 4, 'J': 2}
    hasJoker = False
    rankToCount = dict()
    suitToCount = dict() # needed to tell straight from royal straight flush
    score = 0
    category = None
    ### pre-processing
    for card in cards:
        if len(card) == 1: # joker
            hasJoker = True
        else:
            rankToCount[card[1]] = rankToCount.get(card[1],0) + 1
            suitToCount[card[0]] = suitToCount.get(card[0],0) + 1
    countToRank = dict()
    for k in rankToCount:
        countToRank.setdefault(rankToCount[k],list()).append(k)
    ### 
    if hasJoker and 4 in countToRank: # five card
        category = 'five card'
        score = 90000
    elif hasJoker and len(rankToCount) == 4: # straight
        if len(suitToCount) == 1: # same suit: royal straight flush
            category = 'royal straight flush'
            score = 80000
        else: # straight
            category = 'straight'
            score = 50000
    elif not hasJoker and 4 in countToRank: # four card w/o joker
        category = 'four card'
        score = 70000
        score += rankWeight[countToRank[4][0]] * 1000
        score += rankWeight[countToRank[1][0]] * 100
    elif hasJoker and 3 in countToRank: # four card w/ joker
        category = 'four card'
        score = 70000 + rankWeight[countToRank[3][0]] * 1000 + rankWeight[countToRank[1][0]] * 100
    elif 3 in countToRank and 2 in countToRank: # full house w/o joker
        category = 'full house'
        score = 60000 + rankWeight[countToRank[3][0]] * 1000 + rankWeight[countToRank[2][0]] * 100
    elif hasJoker and 2 in countToRank and len(countToRank[2]) == 2: # full house w/ joker
        category = 'full house'
        r1 = countToRank[2][0]
        r2 = countToRank[2][1]
        score = 60000 + max(rankWeight[r1] * 1000 + rankWeight[r2] * 100,
                                rankWeight[r2] * 1000 + rankWeight[r1] * 100)
    elif not hasJoker and 3 in countToRank and 2 not in countToRank: # 3 card w/o joker
        category = 'three card'
        r1 = countToRank[1][0]
        r2 = countToRank[1][1]
        score = 40000 + rankWeight[countToRank[3][0]] * 1000 + \
                    max(rankWeight[r1] * 100 + rankWeight[r2] * 10, rankWeight[r2] * 100 + rankWeight[r1] * 10)
    elif hasJoker and 2 in countToRank and 1 in countToRank: # 3 card w/ joker
        category = 'three card'
        r1 = countToRank[1][0]
        r2 = countToRank[1][1]
        score = 40000 + rankWeight[countToRank[2][0]] * 1000 + \
                    max(rankWeight[r1] * 100 + rankWeight[r2] * 10, rankWeight[r2] * 100 + rankWeight[r1] * 10)
    elif not hasJoker and 2 in countToRank and len(countToRank[2]) == 2: # 2 pair (must be w/o joker)
        category = 'two pair'
        p1 = countToRank[2][0]
        p2 = countToRank[2][1]
        score = 30000 +  \
                    max(rankWeight[p1] * 1000 + rankWeight[p2] * 100,
                        rankWeight[p2] * 1000 + rankWeight[p1] * 100) + \
                    rankWeight[countToRank[1][0]] * 10
    elif not hasJoker and len(rankToCount) == 4: # 1 pair (must be w/o joker)
        category = 'one pair'
        p = countToRank[2][0]
        score = 20000 + rankWeight[p] * 1000
        if p == 'A':
            score += rankWeight['K'] * 100 + rankWeight['Q'] * 10 + rankWeight['J']
        elif p == 'K':
            score += rankWeight['A'] * 100 + rankWeight['Q'] * 10 + rankWeight['J']
        elif p == 'Q':
            score += rankWeight['A'] * 100 + rankWeight['K'] * 10 + rankWeight['J']
        else: # p = 'J'
            score += rankWeight['A'] * 100 + rankWeight['K'] * 10 + rankWeight['Q']
    else:
        print('ops, this one is out of my analysis... %s' % (','.join(cards)))
    ###
    return score,category


def betting2(name,iQ,rQ,minBet,maxBet,target=None):
    """
    20180524
    This function implements a random betting strategt.
    During the betting process, this player gets instructions from iQ (instruction queue)
    and, if necessary, places responses in rQ (response queue).

    name: player name, a string
    iQ: the instruction queue. Use "aString = iQ.get()" to get the instruction.
    rQ: the response queue. Use "rQ.put(aString)" to put the response.
    minBet: the initial minimum bet of this betting interval.
    maxBet: the maximum bet of this betting interval.
    target (new in v1): the target bet. If None (default), a random target is generated.

    Returns: myBet,oppBet,isSetter
        myBet/oppBet is the amount of money, excluding ante, that this player/the opponent
        has placed in the pot.
        If myBet > oppBet, the opponent has folded.
        If myBet < oppBet, this player has folded.
        If myBet == oppBet, there are two cases.
            Case I: myBet == 0
                Both players checked.
            Case II: myBet > 0
                Bet agreed. If isSetter is True, this player is the one who sets the bet, i.e.,
                the opponent "calls." Otherwise, the opponent is the one who sets the bet.
    """

    oppChecked = False # True/False if the opponent has/hasn't checked.
    checked = False # True/False if this player has/hasn't checked.
    myBet = 0 # The bet, excluding ante, that this player has placed in the pot.
    oppBet = 0 # The bet, excluding ante, that the opponent has placed in the pot.
    isSetter = None # True/False if this player/the opponent sets the agreed bet.
    
    if target == None:
        target = random.randint(minBet,maxBet)
    while True:
        instruction = iQ.get()
        if instruction == 'action:bet,check':
            if random.random() > (maxBet - target)*0.2/(maxBet - minBet): # bet
                myBet = random.randint(minBet,target)
                isSetter = True
                rQ.put('bet %d' % myBet)
            else: # check
                checked = True
                rQ.put('check')
                if oppChecked: # both check, end betting
                    break
        elif instruction == 'action:raise,call,fold': # this follows opponent's "bet" or "raise"
            if target > oppBet: # raise
                myBet = oppBet
                myRaise = random.randint(1,target-oppBet)
                myBet += myRaise
                isSetter = True
                rQ.put('raise %d to be %d' % (myRaise,myBet))
            elif target == oppBet: # call
                myBet = oppBet
                rQ.put('call %d' % oppBet)
                break
            else: # fold
                rQ.put('fold')
                break 
        elif instruction == 'action:call,fold': # no "raise" option because maximum bet is reached
            if oppBet == target: # call
                myBet = oppBet
                rQ.put('call %d' % myBet)
                break
            else: # fold
                rQ.put('fold')
                break
        elif instruction.startswith('opponent bet'): # the 3rd token is the amount of bet
            oppBet = int(instruction.split()[2])
            isSetter = False
        elif instruction.startswith('opponent raise'): # the 3rd token the amount of raise
            oppBet = myBet + int(instruction.split()[2])
            isSetter = False
        elif instruction == 'opponent check':
            oppChecked = True
            if checked:
                break
        elif instruction == 'opponent fold':
            break
        elif instruction == 'opponent call':
            oppBet = myBet
            break
        else:
            print('%s > unknown instruction: %s' % (name,instruction))
    return myBet,oppBet,isSetter

def bettingours(name,iQ,rQ,minBet,maxBet,hand,countcards):
    
    myBet = 0 # The bet, excluding ante, that this player has placed in the pot.
    oppBet = 0 # The bet, excluding ante, that the opponent has placed in the pot.
    isSetter = False # True/False if this player/the opponent sets the agreed bet.
    oppRaise = False
    oppBrave = False
    gameEnd = False
    low = ['one pair', 'two pair']
    med = ['three card', 'straight', 'full house']
    medhigh = ['four card']
    high = ['five card', 'royal straight flush']
    score = analyzeHand(hand)[0]
    category = analyzeHand(hand)[1]
    
    if hasJoker(hand) and (countcards+10) >= 13:
        instruction = iQ.get()
        if instruction.startswith('action') and myBet == 0: #我先發言
            rQ.put('check')
            instruction = iQ.get() #opponent decision
            if instruction == 'opponent check': #兩個人都check
                gameEnd = True #遊戲結束
            elif instruction.startswith('opponent bet'): #opp 下注(整場第一次)
                oppBet = int(instruction.split()[2])
                if oppBet >= (minBet+maxBet)//2:
                    oppBrave = True
        elif instruction.startswith('opponent') and myBet ==0: #我後發言
            if instruction == 'opponent check':#對方check
                instruction = iQ.get() #ask for my action 
                if category in medhigh or category in high:
                    myBet = random.randint((minBet+maxBet)//2, maxBet)
                else:
                    myBet = random.randint(minBet,(minBet+maxBet)//2)
                rQ.put('bet %d' % myBet)
                isSetter = True
            else: #對方下注
                oppBet = int(instruction.split()[2])
                if oppBet >= (minBet+maxBet)//2:
                    oppBrave = True
        while True:
            if gameEnd == True:
                break
            instruction = iQ.get() 
            if instruction =='action:raise,call,fold' and (not (oppRaise and oppBrave)):
                oppBrave = False
                if category in medhigh or category in high:
                    choice = ['call', 'raise']
                    decision = random.choice(choice) 
                    if decision == 'call': # "isSetter" is still False
                        myBet = oppBet
                        rQ.put('call %d' % myBet) 
                        break #此輪結束
                    else: #選擇加注
                        myBet = oppBet
                        myRaise = random.randint(1,maxBet-oppBet) #加一到加最多任選一個數字
                        myBet += myRaise
                        rQ.put('raise %d to be %d' % (myRaise,myBet))
                        isSetter = True
                        #繼續
                else:
                    decision = 'call'
                    myBet = oppBet
                    rQ.put('call %d' % myBet)
                    break #此輪結束
            elif instruction =='action:raise,call,fold' and (oppRaise or oppBrave):
                oppBrave = False
                if category in high:
                    choice = ['call', 'raise']
                    decision = random.choice(choice) 
                    if decision == 'call': # "isSetter" is still False
                        myBet = oppBet
                        rQ.put('call %d' % myBet) 
                        break #此輪結束
                    else: #選擇加注
                        myBet = oppBet
                        myRaise = random.randint(1,maxBet-oppBet) #加一到加最多任選一個數字
                        myBet += myRaise
                        rQ.put('raise %d to be %d' % (myRaise,myBet))
                        isSetter = True
                        #繼續
                elif category in medhigh:
                    decision = 'call'
                    myBet = oppBet
                    rQ.put('call %d' % myBet)
                    break
                elif category in med:
                    decision = 'fold'
                    rQ.put('fold')
                    break #此輪結束
            elif instruction == 'action:call,fold': #對方已經加滿 很有信心
                if category in medhigh or category in high:
                    decision = 'call'
                    myBet = oppBet
                    rQ.put('call %d' % myBet)
                    break
                else:
                    decision = 'fold'
                    rQ.put('fold')
                    break #此輪結束
            elif instruction == 'opponent call':
                oppBet = myBet
                break
            elif instruction.startswith('opponent raise'):# the 3rd token the amount of raise
                oppBet = myBet + int(instruction.split()[2])
                isSetter = False
                oppRaise = True
                continue
            elif instruction == 'opponent fold':
                break    
                
    elif hasJoker(hand) and (countcards+10) < 13:
        instruction = iQ.get()
        if instruction.startswith('action') and myBet == 0: #我先發言
            rQ.put('check')
            instruction = iQ.get() #opponent decision
            if instruction == 'opponent check': #兩個人都check
                gameEnd = True #遊戲結束
            elif instruction.startswith('opponent bet'): #opp 下注(整場第一次)
                oppBet = int(instruction.split()[2])
                if oppBet >= (minBet+maxBet)//2:
                    oppBrave = True
        elif instruction.startswith('opponent') and myBet ==0: #我後發言
            if instruction == 'opponent check':#對方check
                instruction = iQ.get() #ask for my action 
                if category in medhigh or category in high:
                    myBet = random.randint((minBet+maxBet)//2, maxBet)
                else:
                    myBet = random.randint(minBet,(minBet+maxBet)//2)
                rQ.put('bet %d' % myBet)
                isSetter = True
            else: #對方下注
                oppBet = int(instruction.split()[2])
                if oppBet >= (minBet+maxBet)//2:
                    oppBrave = True
        while True:
            if gameEnd == True:
                break
            instruction = iQ.get() 
            if instruction =='action:raise,call,fold':
                if category in medhigh or category in high:
                    choice = 'raise'
                    myBet = oppBet
                    myRaise = random.randint((maxBet-oppBet)//2 +1,maxBet-oppBet)
                    #從可以加的一半到加最多任選一個數字 我有信心
                    myBet += myRaise
                    rQ.put('raise %d to be %d' % (myRaise,myBet))
                    isSetter = True
                    #繼續
                else:
                    decision = 'call'
                    myBet = oppBet
                    rQ.put('call %d' % myBet)
                    break #此輪結束
            elif instruction == 'action:call,fold': #對方已經加滿 很有信心
                decision = 'call'
                myBet = oppBet
                rQ.put('call %d' % myBet)
                break #此輪結束
            elif instruction == 'opponent call':
                oppBet = myBet
                break
            elif instruction.startswith('opponent raise'):# the 3rd token the amount of raise
                oppBet = myBet + int(instruction.split()[2])
                isSetter = False
                continue
            elif instruction == 'opponent fold':
                break    
              
    elif not hasJoker(hand) and (countcards+10)>= 13:
        instruction = iQ.get()
        if instruction.startswith('action') and myBet == 0: #我先發言
            rQ.put('check')
            instruction = iQ.get() #opponent decision
            if instruction == 'opponent check': #兩個人都check
                gameEnd = True #遊戲結束
            elif instruction.startswith('opponent bet'): #opp 下注(整場第一次)
                oppBet = int(instruction.split()[2])
                if oppBet >= (minBet+maxBet)//2:
                    oppBrave = True
        elif instruction.startswith('opponent') and myBet ==0: #我後發言
            if instruction == 'opponent check':#對方check
                instruction = iQ.get() #ask for my action 
                if category in medhigh:
                    myBet = random.randint(minBet + (maxBet-minBet)//2, maxBet)
                    #加一到可以raise的一半任選一個數字
                    rQ.put('bet %d' % myBet)
                    isSetter = True
                    #繼續
                elif category in med:
                    myBet = random.randint(minBet, minBet + (maxBet-minBet)//2 +1)
                    rQ.put('bet %d' % myBet)
                    isSetter = True
                else: #category in low
                    rQ.put('check')
                    gameEnd = True
            else: #對方下注
                oppBet = int(instruction.split()[2])
                if oppBet >= (minBet+maxBet)//2:
                    oppBrave = True
        while True:
            if gameEnd == True:
                break
            instruction = iQ.get() 
            if instruction =='action:raise,call,fold' and (not (oppRaise and oppBrave)):#對方沒有很好
                oppBrave = False
                if category in medhigh:
                    choice = ['call','raise']
                    decision = random.choice(choice)
                    if decision == 'call':
                        myBet = oppBet
                        rQ.put('call %d'% myBet)
                        break
                    else: #raise
                        myBet = oppBet
                        myRaise = random.randint(1,(maxBet-oppBet)*3//4 +1)
                        myBet += myRaise
                        rQ.put('raise %d to be %d' % (myRaise,myBet))
                        isSetter = True                
                elif category in med:
                    decision = 'call'
                    myBet = oppBet
                    rQ.put('call %d' % myBet)
                    break
                elif category in low:
                    rQ.put('fold')
                    break #此輪結束
            elif instruction =='action:raise,call,fold' and (oppRaise or oppBrave):
                oppBrave = False
                if category in medhigh:
                    myBet = oppBet
                    rQ.put('call %d' % myBet)
                    break #此輪結束                    
                elif category in med:
                    choice = ['fold','call']
                    decision = random.choice(choice)
                    if decision == 'call':
                        myBet = oppBet
                        rQ.put('call %d' % myBet)
                        break
                    else: #choose fold
                        rQ.put('fold')
                        break
                elif category in low:
                    rQ.put('fold')
                    break #此輪結束
            elif instruction == 'action:call,fold': #對方已經加滿 很有信心
                if category in medhigh:
                    myBet = oppBet
                    rQ.put('call %d' % myBet)
                    break #此輪結束                    
                elif category in med:
                    choice = ['fold','call']
                    decision = random.choice(choice)
                    if decision == 'call':
                        myBet = oppBet
                        rQ.put('call %d' % myBet)
                        break
                    else: #choose fold
                        rQ.put('fold')
                        break
                elif category in low:
                    rQ.put('fold')
                    break #此輪結束
            elif instruction == 'opponent call':
                oppBet = myBet
                break
            elif instruction.startswith('opponent raise'):# the 3rd token the amount of raise
                oppBet = myBet + int(instruction.split()[2])
                isSetter = False
                oppRaise = True
                continue
            elif instruction == 'opponent fold':
                break          

    else:
        instruction = iQ.get()
        if instruction.startswith('action') and myBet == 0: #我先發言
            rQ.put('check')
            instruction = iQ.get() #opponent decision
            if instruction == 'opponent check': #兩個人都check
                gameEnd = True #遊戲結束
            elif instruction.startswith('opponent bet'): #opp 下注(整場第一次)
                oppBet = int(instruction.split()[2])
                if oppBet >= (minBet+maxBet)//2:
                    oppBrave = True
        elif instruction.startswith('opponent') and myBet ==0: #我後發言
            if instruction == 'opponent check':#對方check
                instruction = iQ.get() #ask for my action 
                if category in medhigh:
                    myBet = random.randint(minBet +(maxBet-minBet)//2, maxBet)
                    #加一到可以raise的一半任選一個數字
                    rQ.put('bet %d' % myBet)
                    isSetter = True
                    #繼續
                elif category in med:
                    myBet = random.randint(minBet, minBet + (maxBet-minBet)//2 +1)
                    rQ.put('bet %d' % myBet)
                    isSetter = True
                else: #category in low
                    choice = ['check','bet']
                    decision = random.choice(choice)
                    if decision == 'check':
                        rQ.put('check')
                        gameEnd = True
                    else:
                        myBet = random.randint(minBet, minBet + (maxBet-minBet)//2)
                        rQ.put('bet %d' % myBet)
                        isSetter = True
            else: #對方下注
                oppBet = int(instruction.split()[2])
                if oppBet >= (minBet+maxBet)//2:
                    oppBrave = True
        while True:
            if gameEnd == True:
                break
            instruction = iQ.get() 
            if instruction =='action:raise,call,fold' and (not (oppRaise and oppBrave)):#對方沒有很好
                oppBrave = False
                if category in medhigh:
                    choice = ['call','raise']
                    decision = random.choice(choice)
                    if decision == 'call':
                        myBet = oppBet
                        rQ.put('call %d'% myBet)
                        break
                    else: #raise
                        myBet = oppBet
                        myRaise = random.randint(1,maxBet-oppBet)
                        myBet += myRaise
                        rQ.put('raise %d to be %d' % (myRaise,myBet))
                        isSetter = True                
                elif category in med:
                    choice = ['call','raise']
                    decision = random.choice(choice)
                    if decision == 'call':
                        myBet = oppBet
                        rQ.put('call %d'% myBet)
                        break
                    else: #raise
                        myBet = oppBet
                        myRaise = random.randint(1,(maxBet-oppBet)*3//4 +1)
                        myBet += myRaise
                        rQ.put('raise %d to be %d' % (myRaise,myBet))
                        isSetter = True       
                elif category in low:
                    myBet = oppBet
                    rQ.put('call %d'% myBet)
                    break
            elif instruction =='action:raise,call,fold' and (oppRaise or oppBrave): #對方不錯
                oppBrave = False
                if category in medhigh:
                    choice = ['call','raise']
                    decision = random.choice(choice)
                    if decision == 'call':
                        myBet = oppBet
                        rQ.put('call %d'% myBet)
                        break
                    else: #raise
                        myBet = oppBet
                        myRaise = random.randint(1,maxBet-oppBet)
                        myBet += myRaise
                        rQ.put('raise %d to be %d' % (myRaise,myBet))
                        isSetter = True                
                elif category in med:
                    myBet = oppBet
                    rQ.put('call %d'% myBet)
                    break    
                elif category in low:
                    rQ.put('fold')
                    break
            elif instruction == 'action:call,fold': #對方已經加滿 很有信心                
                if category in low:
                    rQ.put('fold')
                    break #此輪結束
                else:
                    myBet = oppBet
                    rQ.put('call %d' % myBet)
                    break #此輪結束    
            elif instruction == 'opponent call':
                oppBet = myBet
                break
            elif instruction.startswith('opponent raise'):# the 3rd token the amount of raise
                oppBet = myBet + int(instruction.split()[2])
                isSetter = False
                oppRaise = True
                continue
            elif instruction == 'opponent fold':
                break          
    return myBet,oppBet,isSetter
    
    
    
    
def setTarget(cards):
    """
    20180524
    Given the five cards, set the target bet.

    cards: The five cards. See "analyzeHand" for more details.

    Returns: a score such that 0 <= score <= 1.
        Larger score implies better hands and you should bet more.
    """
    score,cat = analyzeHand(cards)
    score = int(random.triangular(score-5000,score+10000,score))
    score = (score - 20000) / (100000 - 200000) # from 0 to 1
    score = max(0,score)
    score = min(1,score)
    return score

def changeCards(cards,maxChange=5):
    """
    20180524
    Determine which cards to change.
    The strategy is simple -- give up the singltons except for when the hand is straight.

    cards: The five cards. See "analyzeHand" for more details.
    maxChange: The maximum number of cards that can be changed.
        If there are more cards than "maxChange" that we would like to give up,
        randomly pick "maxChange" ones to replace.

    Returns: The set of cards to give up.
    """
    hasJoker = False
    rankToCount = dict()
    suitToCount = dict() # needed to tell straight from royal straight flush
    ### pre-processing
    for card in cards:
        if len(card) == 1: # joker
            hasJoker = True
        else:
            rankToCount[card[1]] = rankToCount.get(card[1],0) + 1
            suitToCount[card[0]] = suitToCount.get(card[0],0) + 1
    countToRank = dict()
    for k in rankToCount:
        countToRank.setdefault(rankToCount[k],list()).append(k)
    #
    score,cat = analyzeHand(cards)
    targetCards = set() # the cards to change
    if cat == 'five card' or cat == 'royal straight flush' or cat == 'straight' or cat == 'full house':
        pass
    elif cat == 'four card': # change the singleton
        for card in cards:
            if card != 'J' and card[1] in countToRank[1]:
                targetCards.add(card)
                break
    elif cat == 'three card': # give up the two singleton cards
        for card in cards:
            if card != 'J' and card[1] in countToRank[1]: # skip singltons
                targetCards.add(card)
    elif cat == 'two pair' or cat == 'one pair': # give up the singletons
        for card in cards:
            if card != 'J' and card[1] in countToRank[1]:
                targetCards.add(card)
    else:
        print('SOMETHING WRONG in "changeCards()" .........................................')
    ###
    if maxChange < len(targetCards):
        targetCards = random.sample(targetCards,maxChange)
    return targetCards

def hasJoker(s):
    for i in range(len(s)):
        if s[i]=='J':
            return True
    return False

def play(gameCount,iQ,rQ):
    """
    This function implements the fate17 protocol.
    Compared to the players in v1, decisions are now somewhat determinnistic, according to
    the cards in hand.
    * Bugfix:
        In v0 and v1, there was a bug that the host took the changed cards but didn't give
        back replacement cards. This is fixed in this version.

    gameCount: the number of games to play.
    iQ: the instruction queue. (See "betting2" for more.)
    rQ: the response queue. (See "betting2" for more.)
    """
    ########## ########## ########## ########## ########## INITIALIZATION
    balance = 0
    rQ.put('%s report for %d gmaes' % (name,gameCount)) # You can say anything here ...
    ##### start games
    for gameIndex in range(1,gameCount+1):
        ##### receive the assigned order (first or second)
        instruction = iQ.get() # first or second
        leader = True if instruction == 'first' else False
        ##### pay ante
        instruction = iQ.get()
        balance -= 5
        ##### recieve cards
        instruction = iQ.get()
        hand = instruction.split(' ')[1].split(',')
        ########## ########## ########## ########## BETTING INTERVAL I
        minBet = 5
        maxBet = 15
        target = int(setTarget(hand) * (maxBet - minBet) + minBet)
        target = min(maxBet,target)
        target = max(minBet,target)
        myBet1,oppBet1,isSetter1 = bettingours(name,iQ,rQ,minBet,maxBet,hand,13)
        balance -= myBet1
        if myBet1 == 0 and oppBet1 == 0: # both check
            continue # go to next game
        elif myBet1 != oppBet1: # no agreement on bet
            if isSetter1: # get all money in the pot (ante lost to the host)
                balance += myBet1 + oppBet1
            continue # go to next game
        ########## ########## ########## ########## CHANGING CARDS
        countcards = 0
        if isSetter1: # me change first
            instruction = iQ.get() # action:change
            selected = changeCards(hand,5) # can change up to 5 cards
            c = rQ.put('change %s' % (','.join(selected)))
            countcards += len(selected)
            instruction = iQ.get() # cards J,QH -- was missing in v0 and v1
            newCards = list() if len(selected) == 0 else instruction.split()[1].split(',')
            instruction = iQ.get() # opponent change X cards
            oppChangeCount = int(instruction.split()[2])
            countcards += oppChangeCount
            
        else: # the opponent changes first
            instruction = iQ.get() # opponent change X cards
            oppChangeCount = int(instruction.split()[2])
            countcards += oppChangeCount
            iQ.get() # action:change
            selected = changeCards(hand,7-oppChangeCount)
            countcards += len(selected)
            rQ.put('change %s' % (','.join(selected)))
            instruction = iQ.get() # cards J,QH -- was missing in v0
            newCards = list() if len(selected) == 0 else instruction.split()[1].split(',')
        for i in selected: # remove changed cards
            hand.remove(i)
        for i in newCards: # include new cards
            hand.append(i)
        ########## ########## ########## ########## BETTING INTERVAL II
        minBet = myBet1 + 1
        maxBet = 30
        target = int(setTarget(hand) * (maxBet - minBet) + minBet)
        target = min(maxBet,target)
        target = max(minBet,target)
        myBet2,oppBet2,isSetter2 = bettingours(name,iQ,rQ,minBet,maxBet,hand,countcards)###記得改arguement
        balance -= myBet2
        if myBet2 == 0 and oppBet2 == 0: # both check -- split the pot (no ante)
            balance += myBet1
            continue
        elif myBet2 != oppBet2: # no agreement in betting interval 2
            if isSetter2: # get all the money in the pot (no ante)
                balance += myBet1 + myBet2 + oppBet1 + oppBet2
            continue
        ########## ########## ########## ########## SHOW HANDS
        response = iQ.get() # opponent cards J,HA,DA,CQ,CA <=== added in v2.1
        response = iQ.get()
        if response == 'win': # win the pot and ante (myBet == oppBet)
            balance += (myBet1 + myBet2 + ANTE) * 2
        elif response == 'tie': # split the pot and get ante back
            balance += myBet1 + myBet2 + ANTE
    #print('Hi, this is %s. My final balance should be %d.' % (name,balance))
    
