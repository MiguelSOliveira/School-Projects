import AuxFunctions

def solveDFS(game, over, dir):
    tabGame = AuxFunctions.returnString(game)
    tabTemp = AuxFunctions.returnString(game)
    stack = [tabGame]
    max = 0
    dis[tabGame] = 0
    while not len(stack) == 0:
        game = list(stack.pop(0))
        tabGame = AuxFunctions.returnString(game)
        #printTable(game)
        index = game.index('0')
        if not repetidos.get(tabGame):
          repetidos[tabGame] = 1
          for value in dir[index]:
            tempGame = game[:]
            tempGame[index+value], tempGame[index] = tempGame[index], tempGame[index+value]
            tabTemp = AuxFunctions.returnString(tempGame)
            stack.insert(0,tabTemp)
            if max < len(stack): max = len(stack)
            dis[tabTemp] = dis.get(tabGame) + 1
            if AuxFunctions.isSolution(tempGame, over):
                print "Tiveram em dada altura um maximo de", max, "nos na fila."
                return dis.get(tabTemp)

def main():
    global repetidos
    repetidos = {}
    global dis
    dis = {}

    dir = [[1,3], [-1, 1, 3], [-1,3], [-3, 1, 3], [-3, -1, 1, 3], [-3, -1, 3], [-3, 1], [-3, -1, 1], [-3, -1]]
    game = [0]*9
    over = [0]*9
 
    tabGame = AuxFunctions.buildGame(game)
    repetidos[tabGame] = 0
    tabOver = AuxFunctions.buildGame(over)

    if AuxFunctions.isSolvable(tabGame, tabOver):
        print solveDFS(game, over, dir)
    else:
        print "Nao e resolvivel"

main()