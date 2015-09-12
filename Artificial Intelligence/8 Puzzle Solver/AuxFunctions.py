def buildGame(game):
    tabuleiro = ""
    i = 0
    for _ in range(3):
        t = map(int, raw_input().split())
        for j in range(3):
            game[i] = t[j]
            tabuleiro += str(game[i])
            i += 1
    return tabuleiro

def returnString(game):
    return "".join(map(str, game))

def isSolution(game, over):
    return True if returnString(game) == returnString(over) else False

def printTable(table):
    for x in range(0, 9, 3):
        print table[x], table[x+1], table[x+2]
    print '\n'

def isSolvable(game, over):
    if(sorted(game) != sorted(over)): return False
    sum1 = 0
    sum2 = 0
    for x in range(9):
        if int(game[x]) != 0:
            for y in range(x+1, 9):
                if int(game[y]) < int(game[x]) and int(game[y]) != 0:
                    sum1 += 1
        if int(over[x]) != 0:
            for y in range(x+1, 9):
                if int(over[y]) < int(over[x]) and int(over[y]) != 0:
                    sum2 += 1
    return False if (sum1-sum2) % 2 else True

def printCaminho(caminho, tabGame, tabOver):
    caminhoAnswer = []
    x = tabOver
    printTable(tabGame)
    while x != tabGame:
        caminhoAnswer.append(x)
        x = caminho[x]
    for value in caminhoAnswer[::-1]:
        printTable(value)
    return len(caminhoAnswer)