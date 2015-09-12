import AuxFunctions
    
def solveIDFS(game, over, dir):
    nivel_limite = 0
    max = 0
    while True:
        stack = [game]
        repetidos.clear()
        dis.clear()
        dis[game] = 0
        while not len(stack) == 0:
            node = stack.pop(0)
            if AuxFunctions.isSolution(list(node), list(over)):
                print "Tiveram em dada altura um maximo de", max, "nos na fila."
                return nivel_limite
            index = node.index('0')
            if dis.get(node) < nivel_limite:
                for value in dir[index]:
                    nodeTrader = list(node)[:]
                    nodeTrader[index+value], nodeTrader[index] = nodeTrader[index], nodeTrader[index+value]
                    nodeTraderString = AuxFunctions.returnString(nodeTrader)
                    if not caminho.get(nodeTraderString):
                        caminho[nodeTraderString] = node
                    if not dis.get(nodeTraderString) or dis.get(node) + 1 < dis.get(nodeTraderString):
                        dis[nodeTraderString] = dis.get(node) + 1
                        stack.insert(0, nodeTraderString)
                        print len(stack)
                        if len(stack) > max: max = len(stack)
        nivel_limite += 1

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
    tabOver = AuxFunctions.buildGame(over)

    if AuxFunctions.isSolvable(tabGame, tabOver):
        print solveIDFS(tabGame, tabOver, dir)
        jogadas = AuxFunctions.printCaminho(caminho, tabGame, tabOver)
    else:
        print "Nao e resolvivel"

main()