var jogada = 'O';
var tabuleiro = ["", "", "", "", "", "", "", "", ""];
var gameOver = false;

var jogador = prompt("Quem comeca?\n1- Computador\n2- Jogador");
var metodo = prompt("Escolha o metodo(1- MINIMAX, 2- ALPHABETA");

function restartGame() {
  for(var i = 0; i < 9; i++) {
    document.getElementById(String(i)).innerHTML = "";
    tabuleiro[i] = "";
  }
    gameOver = false;
    jogador = prompt("Quem comeca?\n1- Computador\n2- Jogador");
    metodo = prompt("Escolha o metodo(1- MINIMAX, 2- ALPHABETA");
    if(jogador == 1){
      var answer = play(tabuleiro, -1, metodo, jogador);
      tabuleiro[answer] = 'O';
      document.getElementById(answer).innerHTML = 'O';
    jogador = 2;
    }
  }

function nextTurnWin(tabuleiro){
  for(var i = 0; i < 9; i++){
    if(tabuleiro[i] == ''){
      tabuleiro[i] = 'O';
      if(checkVictory(tabuleiro) == 10) { tabuleiro[i] = ''; return [true ,i]; }
      tabuleiro[i] = '';
    }
  }
  return [false, -1];
}

function changePlayer(jogada){
  if (jogada == 'X') jogada = 'O';
  else jogada = 'X';
  return jogada;
}

if(jogador == 1){
  var answer = play(tabuleiro, -1, metodo, jogador);
  tabuleiro[answer] = 'O';
  document.getElementById(answer).innerHTML = 'O';
  jogador = 2;
}

function clickFunction(buttonID){
  // Funcao principal, continuar o jogo enquanto nao ocorrer vitoria, derrota ou empate.
  if(!gameOver){
    // Se nao estiver ocupada a posicao no botao clicado.
    if (document.getElementById(buttonID).innerHTML == ""){
      jogada = changePlayer(jogada);
      document.getElementById(buttonID).innerHTML=jogada;
      tabuleiro[buttonID] = jogada;
      // Acabar o jogo num empate.
      if(boardIsFull(tabuleiro)) { alert("Empate!"); gameOver = true; return;}
      tabuleiro[buttonID] = "";
      jogada = changePlayer(jogada);
      var answer = play(tabuleiro, buttonID, metodo, jogador);
      // Se jogada nao for valida, nao fazer nada.
      if(answer == -1) {}
      // Senao jogar na posicao mais vantajosa.
      else {
        document.getElementById(answer).innerHTML=jogada;
      }
      if(boardIsFull(tabuleiro)) { alert("Empate!"); gameOver = true; return;}
    }
    else alert("Impossivel jogar ai, por favor escolha outra posicao.");
    if(checkVictory(tabuleiro) == 10) { alert("Ganhei!"); gameOver = true; }
    else if(checkVictory(tabuleiro) == -10) { alert("Perdi!"); gameOver = true; }
  }
}

function checkVictory(tabuleiro){
  var iWon = false, iLost = false;
  // Horizontais
  for(var i = 0; i < 9; i+= 3){
    if(tabuleiro[i] == tabuleiro[i+1] && tabuleiro[i+1] == tabuleiro[i+2] && tabuleiro[i] != ""){
      if(tabuleiro[i] == 'O') iWon = true;
      else iLost = true;
    }
  }
  // Verticais
  for(var i = 0; i < 3; i++){
    if(tabuleiro[i] == tabuleiro[i+3] && tabuleiro[i] == tabuleiro[i+6] && tabuleiro[i] != ""){
      if(tabuleiro[i] == 'O') iWon = true;
      else iLost = true;
    }
  }
  // Diagonal principal
  if(tabuleiro[0] == tabuleiro[4] && tabuleiro[0] == tabuleiro[8] && tabuleiro[0] != ""){
    if(tabuleiro[0] == 'O') iWon = true;
    else iLost = true;
  }
  // Diagonal secundaria
  if(tabuleiro[2] == tabuleiro[4] && tabuleiro[2] == tabuleiro[6] && tabuleiro[2] != ""){
    if(tabuleiro[2] == 'O') iWon = true;
    else iLost = true;
  }
  if(iWon) return 10;
  if(iLost) return -10;
  return 0;
}

function boardIsFull(tabuleiro) {
  for(var i = 0; i < 9; i++)
    if(tabuleiro[i] == "") return false;
  return true;
}

var bestIndex = -1;
function bestPlayALPHABETA(tabuleiro, jogada) {
  var tempV = Number.NEGATIVE_INFINITY;
  for(var i = 0; i < 9; i++){
    if(tabuleiro[i] == ''){
      tabuleiro[i] = jogada;
      jogada = changePlayer(jogada);
      var v = minValue(tabuleiro, jogada, Number.NEGATIVE_INFINITY, Number.POSITIVE_INFINITY);
      jogada = changePlayer(jogada);
      tabuleiro[i] = '';
      if(v > tempV){
        tempV = v;
        bestIndex = i;
      }
    }
  }
  return bestIndex;
}

function maxValue(tabuleiro, jogada, alpha, beta) {
  if(checkVictory(tabuleiro) == 10) return 10;
  if(checkVictory(tabuleiro) == -10) return -10;
  if(boardIsFull(tabuleiro)) return 0;
  var v = Number.NEGATIVE_INFINITY;
  for(var i = 0; i < 9; i++) {
    if(tabuleiro[i] == '') {
      tabuleiro[i] = jogada;
      jogada = changePlayer(jogada);
      v = Math.max(v, minValue(tabuleiro, jogada, alpha, beta));
      jogada = changePlayer(jogada);
      tabuleiro[i] = '';
      alpha = Math.max(alpha, v);
      if( alpha >= beta ) break;
    }
  }
  return v;
}

function minValue(tabuleiro, jogada, alpha, beta) {
  if(checkVictory(tabuleiro) == 10) return 10;
  if(checkVictory(tabuleiro) == -10) return -10;
  if(boardIsFull(tabuleiro)) return 0;
  var v = Number.POSITIVE_INFINITY;
  for(var i = 0; i < 9; i++) {
    if(tabuleiro[i] == '') {
      tabuleiro[i] = jogada;
      jogada = changePlayer(jogada);
      v = Math.min(v, maxValue(tabuleiro, jogada, alpha, beta));
      jogada = changePlayer(jogada);
      tabuleiro[i] = '';
      beta = Math.min(beta, v);
      if( beta <= alpha ) break;
    }
  }
  return v;
}


function bestPlayMINIMAX(tabuleiro, jogada) {
  // Condicoes de paragem da recursao.
  if(checkVictory(tabuleiro) == 10) return [10, -1];
  if(checkVictory(tabuleiro) == -10) return [-10, -1];
  if(boardIsFull(tabuleiro)) return [0, -1];
  // E criado uma lista para cada no com todos os scores de todos os caminhos dos filhos. E de seguida, ordenada e escolhido o primeiro
  // ou ultimo elemento dependendo do minimax.
  var scores = [];
  for(var i = 0; i < 9; i++) {
    if(tabuleiro[i] == "") {
      tabuleiro[i] = jogada;
      if(jogada == 'X') jogada = 'O';
      else jogada = 'X';
      // Scores vai ficar com um par do score do no e com o tabuleiro(jogada) referente a esse caminho
      scores.push([bestPlayMINIMAX(tabuleiro, jogada)[0], i]);
      tabuleiro[i] = "";
      if(jogada == 'X') jogada = 'O';
      else jogada = 'X';
    }
  }
  scores.sort();
  // Retornar o max ou min dependendo de quem esta a jogar.
  if(jogada == 'X') return scores[0];
  else return scores[scores.length-1];
}

var nextTurnWinVar;
function play(tabuleiro, buttonID, metodo, jogador) {
  var score = 0;
    var notPlayed = true;
    score = checkVictory(tabuleiro);
    if(jogador == 2 || jogador == 0) {
      while(notPlayed){
        // Esperar por uma jogada da jogador 1 num lugar que ainda nao esteja ocupado.
        var jogada = buttonID;
        if(tabuleiro[jogada] == ''){
          tabuleiro[jogada] = 'X';
          score = checkVictory(tabuleiro);
          notPlayed = false;
        }
      }
      jogador = 0;
    }
    score = checkVictory(tabuleiro);
    nextTurnWinVar = nextTurnWin(tabuleiro);
    if(nextTurnWinVar[0]) { tabuleiro[nextTurnWinVar[1]] = 'O'; return nextTurnWinVar[1]; }
    if(jogador == 1 || jogador == 0){
      jogador = 0;
      if(metodo == 1) var bestPlayForAI = bestPlayMINIMAX(tabuleiro, 'O')[1];
      else if(metodo == 2) var bestPlayForAI = bestPlayALPHABETA(tabuleiro, 'O');
      if(tabuleiro[bestPlayForAI] != "") return -1;
      tabuleiro[bestPlayForAI] = 'O';
    }
    return bestPlayForAI;
  }
