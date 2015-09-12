import AuxFunctions

def solveBFS(game, over, dir):
    tabGame = AuxFunctions.returnString(game)
    queue = [tabGame]
    dis[tabGame] = 0
    max = 0
    while not len(queue) == 0:
        game = list(queue.pop(0))
        tabGame = AuxFunctions.returnString(game)
        index = game.index('0')
        if not repetidos.get(tabGame):
            repetidos[tabGame] = 1
            for value in dir[index]:
                tempGame = game[:]
                tempGame[index+value], tempGame[index] = tempGame[index], tempGame[index+value]
                tabTemp = AuxFunctions.returnString(tempGame)
                dis[tabTemp] = dis[tabGame] + 1
                queue.append(tabTemp)
                if len(queue) > max:
                    max = len(queue)
                if not caminho.get(tabTemp):
                    caminho[tabTemp] = tabGame
                if AuxFunctions.isSolution(tempGame, over):
                    print "Tiveram em dada altura um maximo de", max, "nos na fila."
                    return dis.get(tabTemp)

def main():
    global repetidos
    repetidos = {}
    global caminho
    caminho = {}
    global dis
    dis = {}

    dir = [[1,3], [-1, 1, 3], [-1,3], [-3, 1, 3], [-3, -1, 1, 3], [-3, -1, 3], [-3, 1], [-3, -1, 1], [-3, -1]]
    game = [0]*9
    over = [0]*9
 
    tabGame = AuxFunctions.buildGame(game)
    caminho[tabGame] = tabGame
    repetidos[tabGame] = 0
    tabOver = AuxFunctions.buildGame(over)

    if AuxFunctions.isSolvable(tabGame, tabOver):
        solveBFS(game, over, dir)
        jogadas = AuxFunctions.printCaminho(caminho, tabGame, tabOver)
        print "Encontrada solucao otima em", jogadas, "jogadas."
    else:
        print "Nao e resolvivel"

main()