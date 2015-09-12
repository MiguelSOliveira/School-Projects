import AuxFunctions, heapq, math

def manhattanDistance(game, over):
  gameString = AuxFunctions.returnString(game)
  overString = AuxFunctions.returnString(over)
  distancias = {0:0, 1:1, 2:2, 3:1, 4:2, 5:3, 6:2, 7:3, 8:4}
  soma = 0
  for x in range(1,9):
    subtracao = gameString.index(str(x)) - overString.index(str(x))
    d = math.fabs(subtracao)
    if subtracao == 1 and (gameString.index(str(x)) == 2 or gameString.index(str(x)) == 5):
      d = 5
    soma += distancias[int(d)]
  return soma

def solveGreedy(game, over, dir):
  estimation = manhattanDistance(game, over)
  max = 0
  caminho[AuxFunctions.returnString(game)] = AuxFunctions.returnString(game)
  distancias = []
  # Implementacao de heap em ordem das distancias
  heapq.heapify(distancias)
  heapq.heappush(distancias, (estimation, game))
  while not len(distancias) == 0:
    node = heapq.heappop(distancias)
    repetidos[AuxFunctions.returnString(node[1])] = 1
    index = node[1].index(0)
    for value in dir[index]:
      # Troca de elementos, acedendo a segunda posicao do tuplo
      node1 = node[1][:]
      node1[index+value], node1[index] = node1[index], node1[index+value]
      node1String = AuxFunctions.returnString(node1)
      if not caminho.get(node1String):
        caminho[node1String] = AuxFunctions.returnString(node[1])
      dis = manhattanDistance(node1, over)
      if dis == 0:
        print "Tiveram em dada altura um maximo de", max, "nos na fila."
        return node
      if not repetidos.get(node1String):
        heapq.heappush(distancias, (dis, node1[:]))
        if len(distancias) > max: max = len(distancias)


def main():
    global repetidos
    repetidos = {}
    global dis
    dis = {}
    global caminho
    caminho = {}

    dir = [[1,3], [-1, 1, 3], [-1,3], [-3, 1, 3], [-3, -1, 1, 3], [-3, -1, 3], [-3, 1], [-3, -1, 1], [-3, -1]]
    game = [0]*9
    over = [0]*9
 
    tabGame = AuxFunctions.buildGame(game)
    tabOver = AuxFunctions.buildGame(over)

    if AuxFunctions.isSolvable(tabGame, tabOver):
        solveGreedy(game, over, dir)
        jogadas = AuxFunctions.printCaminho(caminho, tabGame, tabOver)
        print "Encontrada solucao em", jogadas, "jogadas."
    else:
        print "Nao e resolvivel"

main()