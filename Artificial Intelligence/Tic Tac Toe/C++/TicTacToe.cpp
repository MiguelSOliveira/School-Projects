#include <bits/stdc++.h>
using namespace std;

bool MaxPlayer = true;

int maxValue(char* tabuleiro, char jogada, int alpha, int beta);
int minValue(char* tabuleiro, char jogada, int alpha, int beta);

void printTabuleiro(char tabuleiro[]){
  int linhasVerticais = 0, linhasHorizontais = 0;
  for(int i = 0; i < 9; i+=3){
    cout << ' ';
    for(int j = 0; j < 3; j++){
      cout << tabuleiro[i+j];
      if(linhasVerticais++ < 2){ cout << " | "; }
    }
    linhasVerticais = 0;
    if(linhasHorizontais++ < 2)
      cout << "\n--- --- ---\n";
  }
  cout << '\n';
  cout << "_____________________________________________________________________\n";
}

int checkVictory(char tabuleiro[]){
  bool iWon = false, iLost = false;
  // Horizontais
  for(int i = 0; i < 9; i+= 3){
    if(tabuleiro[i] == tabuleiro[i+1] && tabuleiro[i+1] == tabuleiro[i+2] && tabuleiro[i] != ' '){
      if(tabuleiro[i] == 'O') iWon = true;
      else iLost = true;
    }
  }
  // Verticais
  for(int i = 0; i < 3; i++){
    if(tabuleiro[i] == tabuleiro[i+3] && tabuleiro[i] == tabuleiro[i+6] && tabuleiro[i] != ' '){
      if(tabuleiro[i] == 'O') iWon = true;
      else iLost = true;
    }
  }
  // Diagonal principal
  if(tabuleiro[0] == tabuleiro[4] && tabuleiro[0] == tabuleiro[8] && tabuleiro[0] != ' '){
    if(tabuleiro[0] == 'O') iWon = true;
    else iLost = true;
  }
  // Diagonal secundaria
  if(tabuleiro[2] == tabuleiro[4] && tabuleiro[2] == tabuleiro[6] && tabuleiro[2] != ' '){
    if(tabuleiro[2] == 'O') iWon = true;
    else iLost = true;
  }
  if(iWon) return 10;
  if(iLost) return -10;
  return 0;
}

bool boardIsFull(char tabuleiro[]){
  for(int i = 0; i < 9; i++)
    if(tabuleiro[i] == ' ') return false;
  return true;
}

char changePlayer(char jogada) {
	if(jogada == 'X') jogada = 'O';
	else jogada = 'X';
	return jogada;
}

pair<bool, int> nextTurnWin(char tabuleiro[]){
  for(int i = 0; i < 9; i++){
    if(tabuleiro[i] == ' '){
      tabuleiro[i] = 'O';
      if(checkVictory(tabuleiro) == 10) { tabuleiro[i] = ' '; return make_pair(true ,i); }
      tabuleiro[i] = ' ';
    }
  }
  return make_pair(false, -1);
}

int nosAnalisados = 0;
pair<int, int> bestPlayMINIMAX(char tabuleiro[], char jogada){

  if(checkVictory(tabuleiro) == 10) return make_pair(10, -1);
  if(checkVictory(tabuleiro) == -10) return make_pair(-10, -1);
  if(boardIsFull(tabuleiro)) return make_pair(0, -1);

  vector<pair<int, int> > scores;

  for(int i = 0; i < 9; i++) {
    if(tabuleiro[i] == ' ') {
      tabuleiro[i] = jogada;
      jogada = changePlayer(jogada);
      nosAnalisados++;
      scores.push_back(make_pair(bestPlayMINIMAX(tabuleiro, jogada).first, i));
      tabuleiro[i] = ' ';
      jogada = changePlayer(jogada);
    }
  }

  sort(scores.begin(), scores.end());

  if(jogada == 'X') return scores.front();
  else return scores.back();
}

int bestIndex = -1;
int bestPlayALPHABETA(char tabuleiro[], char jogada) {
  int tempV = INT_MIN;
  for(int i = 0; i < 9; i++){
    if(tabuleiro[i] == ' '){
      tabuleiro[i] = jogada;
      jogada = changePlayer(jogada);
      int v = minValue(tabuleiro, jogada, INT_MIN, INT_MAX);
      jogada = changePlayer(jogada);
      tabuleiro[i] = ' ';
      if(v > tempV){
        tempV = v;
        bestIndex = i;
      }
    }
  }
  return bestIndex;
}

int maxValue(char tabuleiro[], char jogada, int alpha, int beta) {
  if(checkVictory(tabuleiro) == 10) return 10;
  if(checkVictory(tabuleiro) == -10) return -10;
  if(boardIsFull(tabuleiro)) return 0;
  int v = INT_MIN;
  for(int i = 0; i < 9; i++) {
    if(tabuleiro[i] == ' ') {
      nosAnalisados++;
      tabuleiro[i] = jogada;
      jogada = changePlayer(jogada);
      v = max(v, minValue(tabuleiro, jogada, alpha, beta));
      jogada = changePlayer(jogada);
      tabuleiro[i] = ' ';
      alpha = max(alpha, v);
      if( alpha >= beta ) break;
    }
  }
  return v;
}

int minValue(char tabuleiro[], char jogada, int alpha, int beta) {
  if(checkVictory(tabuleiro) == 10) return 10;
  if(checkVictory(tabuleiro) == -10) return -10;
  if(boardIsFull(tabuleiro)) return 0;
  int v = INT_MAX;
  for(int i = 0; i < 9; i++) {
    if(tabuleiro[i] == ' ') {
      tabuleiro[i] = jogada;
      nosAnalisados++;
      jogada = changePlayer(jogada);
      v = min(v, maxValue(tabuleiro, jogada, alpha, beta));
      jogada = changePlayer(jogada);
      tabuleiro[i] = ' ';
      beta = min(beta, v);
      if( beta <= alpha ) break;
    }
  }
  return v;
}

pair<bool,int> nextTurnWinVar;
int play(char tabuleiro[], int metodo, int jogador) {
  int score = 0, nJogadas = 0, bestPlayForAI = -1;
  while(1){
    bool notPlayed = true;
    score = checkVictory(tabuleiro);
    // Se alguem ganhar sai do ciclo
    if(checkVictory(tabuleiro) == 10 || checkVictory(tabuleiro) == -10) break;
    else if(boardIsFull(tabuleiro)) return 0;
    if(jogador == 2 || jogador == 0) {
      while(notPlayed){
        // Esperar por uma jogada da jogador 1 num lugar que ainda nao esteja ocupado.
        int jogada; cin >> jogada;
        if(tabuleiro[jogada] == ' '){
          nJogadas++;
          tabuleiro[jogada] = 'X';
          // Se empatar acabar o jogo.
          if(nJogadas == 5) {  printTabuleiro(tabuleiro); return 0; }
          if(checkVictory(tabuleiro) == 10 || checkVictory(tabuleiro) == -10) return checkVictory(tabuleiro);
          score = checkVictory(tabuleiro);
          notPlayed = false;
        }
        else cout << "Impossivel jogar nesse lugar, por favor escolha outro." << '\n';
      }
      jogador = 0;
    }
    score = checkVictory(tabuleiro);
    nextTurnWinVar = nextTurnWin(tabuleiro);
    if(nextTurnWinVar.first) { tabuleiro[nextTurnWinVar.second] = 'O'; continue; }
    if(checkVictory(tabuleiro) == 10 || checkVictory(tabuleiro) == -10) { printTabuleiro(tabuleiro); break; }
    if(jogador == 1 || jogador == 0) {
      jogador = 0;
      clock_t time = clock();
      if(metodo == 1) bestPlayForAI = bestPlayMINIMAX(tabuleiro, 'O').second;
      else if(metodo == 2) bestPlayForAI = bestPlayALPHABETA(tabuleiro, 'O');
      time = clock()-time;
      if(bestPlayForAI != -1) tabuleiro[bestPlayForAI] = 'O';
      else return 0;
      cout << "Jogada gerada em " << (float)time/CLOCKS_PER_SEC << " segundos.\n";
    }
    printTabuleiro(tabuleiro);
  }
  return score;
}


int main(){

  char tabuleiro[] = {' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '};
  cout << "Quem comeca?\n";
  cout << "1- Computador\n";
  cout << "2- Jogador\n";
  int jogador; cin >> jogador;
  cout << "Escolha o metodo(1- MINIMAX, 2- ALPHABETA)" << '\n';
  int metodo; cin >> metodo;
  int vitoria;
  if(jogador == 2) printTabuleiro(tabuleiro);
  clock_t time;
  time = clock();
  vitoria = play(tabuleiro, metodo, jogador);
  if(vitoria == -10) cout << "Bolas, perdi." << '\n';
  else if(vitoria == 0) cout << "Empate." << '\n';
  else cout << "Ahah, ganhei!" << '\n';
  cout << nosAnalisados << " Nos Analisados.\n";
  time = clock()-time;
  cout << "O jogo demorou um total de " << ((float)time/CLOCKS_PER_SEC) << " segundos.\n";
  printTabuleiro(tabuleiro);
  return 0;
}
