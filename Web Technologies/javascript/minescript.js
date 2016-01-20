var levels = { '1' : { rows : 9, cols : 9, mines : 10   },
'2' : { rows : 16, cols : 16, mines : 40 },
'3' : { rows : 16, cols : 30, mines : 99 }}
var firstClick = true, uncoveredCells = {}, flagsAndQuestions = {};
var positions = [[-1,-1], [-1,0], [-1,1], [0,-1], [0,1], [1,-1], [1,0], [1,1]];
var dificultyString, game_id, game_key, multiplayer, username;
var server_data, server_response;
var loadBarAnimInterval, loadBarCleared,  turnAnimInterval, foundOponent = false, password, lastTurn = "";
var firstTry = true;
var SomeoneWon = false;
var enemyBombs = 0, myBombs = 0, curPlayer = "";

// ----------------------------------------------------------------------------

var xhttp = new XMLHttpRequest();
xhttp.onreadystatechange = function() {
  if (xhttp.readyState == 4 && xhttp.status == 200) {
    var response = JSON.parse(xhttp.responseText);
    if(response.key != undefined) {
      server_data = response;
      update(username, server_data.key, server_data.game);
    }
    if(firstTry) {
      if(response.error != undefined) { createSwal(response.error, "Register:", "error", null); }
      else {
        goToGame();
        $("#MyScoreDiv").show();
        $("#containerFlagsMP").show();
        $("#containerMyBombs").show();
        tableInit();
        StartMPGame(username, password, group);
        firstTry = false;
      }
    }
    if(response.ranking != undefined) {
      var scores = "";
      for(var i = 0; i < response.ranking.length; i++) {
        var curScore = response.ranking[i];
        scores += curScore.name + " " + curScore.score + '\n';
      }
      createSwal(scores, "Ranking:", "info", null);
    }
    else if(response.score != undefined) {
      createSwal(response.score, "Your score is:", "info", null);
    }
  }
};

function ShowMPCell(cells){
  for(var i = 0; i < cells.length; i++){
    var row = cells[i][0]-1, col = cells[i][1]-1, valueInCell = cells[i][2];
    if(cells[i][2] == "0") {
      board.rows[row].cells[col].setAttribute("style", "background-color: white");
      continue;
    }
    else if(cells[i][2] == "-1"){
      if(curPlayer == username) { setInnerHTML(row, col, getImgURL("BombMe")); myBombs++; }
      else { setInnerHTML(row, col, getImgURL("BombEnemy")); enemyBombs++; }
    }
    if(cells[i][2] != "-1" && cells[i][2] != "0") setInnerHTML(row, col, valueInCell);
    $("#myBombs").html(myBombs + "/" + levels[dificulty].mines);
    $("#enemyBombNumber").html(enemyBombs + "/" + levels[dificulty].mines);
  }
}

function StartMPGame(user, pass, group){
  $("#myBombs").html(myBombs + "/" + levels[dificulty].mines);
  $("#enemyBombNumber").html(enemyBombs + "/" + levels[dificulty].mines);
  join(group , user, pass, dificultyString);
}

function sendPostRequest(sub_domain, params) {
  xhttp.open("POST", "http://twserver.alunos.dcc.fc.up.pt:8040/" + sub_domain, true);
  xhttp.setRequestHeader("Content-type", "application/json");
  xhttp.send(JSON.stringify(params));
}

function sendGetRequest(params) {
  xhttp.open("GET", "http://twserver.alunos.dcc.fc.up.pt:8040/" + params, true);
  xhttp.setRequestHeader("Content-type", "application/json");
  xhttp.send();
}

function leave(name, key, game){
  if(SomeoneWon) { location.reload(); }
  else { createSwal("Game's not over yet.", "Error:", "error", null); }
}

function ranking(level){
  var params = {};
  params.level = level;
  sendPostRequest("ranking", params);
}

function score(name, level){
  var params = {};
  params.name = name;
  params.level = level;
  sendPostRequest("score", params);
}

function ReturnToMenu(){
  if(multiplayer) {
    if(loadBarCleared) {
      leave(username, server_data.key, server_data.game);
      return;
    }
  }
  location.reload();
}

function notify(name, key, game, row, col) {
  var params = {};
  params.name = name;
  params.key = key;
  params.game = game;
  params.row = row;
  params.col = col;
  sendPostRequest("notify", params);
}

function update(name, key, game){
  params = "update?name=" + name + "&game=" + game + "&key=" + key;
  source = new EventSource("http://twserver.alunos.dcc.fc.up.pt:8040/" + params);
  source.onmessage = function(event) {
    server_response = JSON.parse(event.data);
    if(server_response.winner) {
      SomeoneWon = true;
      $("#playerTurn").html("Winner: " + server_response.winner);
      source.close();
    }
    else {
      if(!foundOponent){
        foundOponent = true;
        clearInterval(loadBarAnimInterval);
        loadBarCleared = true;
        $("#canvasContainer").remove();
      }
      curPlayer = server_response.turn;
      $("#playerTurn").html("Turn: " + curPlayer);
      if(curPlayer == username && lastTurn != curPlayer) {
        SetTurnAnimation();
        setTimeout(function(){
          $("#canvasContainer").remove();
          clearInterval(turnAnimInterval);
        }, 1000);
      }
      lastTurn = curPlayer;
    }

    if(typeof server_response.move != "undefined") {
      ShowMPCell(server_response.move.cells);
    }
  };
}

function CreateCanvasOverlay() {
  var canvasContainer = document.createElement('div');
  canvasContainer.setAttribute("id", "canvasContainer");
  document.body.appendChild(canvasContainer);
  canvasContainer.style.position="absolute";
  canvasContainer.style.left="25%";
  canvasContainer.style.top="25%";
  canvasContainer.style.width="50%";
  canvasContainer.style.height="60%";
  canvasContainer.style.zIndex="1000";

  myCanvas = document.createElement('canvas');
  myCanvas.setAttribute("id", "loadingBarCanvas");
  myCanvas.style.width = canvasContainer.scrollWidth+"px";
  myCanvas.style.height = canvasContainer.scrollHeight+"px";
  myCanvas.width=canvasContainer.scrollWidth;
  myCanvas.height=canvasContainer.scrollHeight;
  myCanvas.style.overflow = 'visible';
  myCanvas.style.position = 'absolute';
  canvasContainer.appendChild(myCanvas);
}

function SetLoadingAnimation() {
  CreateCanvasOverlay();
  var canvas = document.getElementById("loadingBarCanvas");
  canvas.width = 1000;
  canvas.height = 1000;
  var ctx= canvas.getContext("2d");

  var frame = 0;
  var xpos = 0;
  var img = new Image();
  function animate() {
    ctx.clearRect(20, 20, 1024, 768);
    frame = (frame + 1) % 6;
    ctx.drawImage(img, 1024*frame, 0, 1024, 768, 20, 20, 1024, 768);
  }
  img.onload = function () {
    loadBarAnimInterval = setInterval(animate, 250);
  };
  img.src = "resources/loadbar2.jpg";
}

function SetTurnAnimation() {
  CreateCanvasOverlay();
  var canvas = document.getElementById("loadingBarCanvas");
  canvas.width = 1000;
  canvas.height = 1000;
  var ctx= canvas.getContext("2d");

  var frame = 0;
  var xpos = 0;
  var img = new Image();
  function animate() {
    ctx.clearRect(20, 20, 1024, 576);
    frame = (frame + 1) % 1;
    ctx.drawImage(img, 1024*frame, 0, 1024, 576, 20, 20, 1024, 576);
  }
  img.onload = function () {
    turnAnimInterval = setInterval(animate, 250);
  };
  img.src = "resources/turnImg.jpg";
}

function join(group, name, pass, level) {
  loadBarCleared = false;
  SetLoadingAnimation();
  var params = {};
  params.group = group;
  params.name = name;
  params.pass = pass;
  params.level = level;
  sendPostRequest("join", params);
}

function register(name, pass){
  var params = {};
  params.name = name;
  params.pass = pass;
  sendPostRequest("register", params);
}

// ----------------------------------------------------------------------------


if(typeof localStorage.scores1 == 'undefined') { localStorage.setItem("scores1", ""); }
if(typeof localStorage.scores2 == 'undefined') { localStorage.setItem("scores2", ""); }
if(typeof localStorage.scores3 == 'undefined') { localStorage.setItem("scores3", ""); }

window.onload = function() { board = document.getElementById("board"); }

function errorsDisplayed(un, pw){
  var message = "";
  if(un)  { message += "Username must contain at least 4 alphanum chars.\n"; }
  if(pw)  { message += "Password must contain at least 8 alphanum characters.\n"; }

  if(!message) { return false; }
  else { createSwal(message, "Errors:", "error", null); }
  return true;
}

function setDificulty() {
  if(document.getElementById('dealwithit').checked) { dificulty = 1; dificultyString = "beginner"; }
  else if(document.getElementById('waitwhat').checked) { dificulty = 2; dificultyString = "intermediate"; }
  else if(document.getElementById('ohno').checked){ dificulty = 3; dificultyString = "expert"; }
}

function getDificulty() {
  var usernamePattern = /^[a-zA-Z0-9]{2,}/, usernameError;
  var passwordPattern = /^[a-zA-Z0-9]{2,}/, passwordError;
  username = document.getElementById("username").value;
  password = document.getElementById("password").value;
  group = document.getElementById("group").value;
  usernameError = !(usernamePattern.test(username));
  passwordError = !(passwordPattern.test(password));
  if(errorsDisplayed(usernameError, passwordError)) { return; }

  multiplayer = document.getElementById("multiplayer").checked;
  setDificulty();
  $("#containerScore").hide();
  $("#containerFlags").hide();
  $("#containerFlagsMP").hide();
  $("#containerMyBombs").hide();

  if(multiplayer) {
    if(group == "") {
      createSwal("Group missing.", "Error:", "error", null);
    }
    else {
      document.addEventListener("contextmenu", function(e){ e.preventDefault(); }, false);
      register(username, password);
    }
  }
  else {

    $("#PlayAgainDiv").show();
    $("#containerScore").show();
    $("#containerFlags").show();
    goToGame();
    tableInit();
    totalClickableCells = levels[dificulty].rows*levels[dificulty].cols-levels[dificulty].mines;
  }
}

function setHTMLProperties(table, placedMines) {
  flags = levels[dificulty].mines;
  var dificultyClass = "e" + dificulty;
  document.getElementById("clicks").innerHTML = flags + "/" + levels[dificulty].mines;
  board.innerHTML = "";
  if(!multiplayer) { board.addEventListener('contextmenu', listener = function (ev) { rightClick(ev, table, placedMines); }); }
  document.getElementById("table").setAttribute("class", dificultyClass);
  document.getElementById("ScoreBoard").onclick = function () { showScores(); }
  document.getElementById("MyScore").onclick = function () { score(username, dificultyString); }
}

function tableInit() {
  var table = createTableMatrix();
  var placedMines = {}
  if(!multiplayer) {
    var returnValues = generateMines(levels[dificulty].mines, table, {});
    placedMines = returnValues[1];
    table = returnValues[0];
  }
  setHTMLProperties(table, placedMines);
  createTableHTML(table, placedMines);
}

function createTableMatrix(){
  var rows = levels[dificulty].rows, cols = levels[dificulty].cols, tableTemp = new Array(rows);
  for(var i = 0; i < rows; i++){
    tableTemp[i] = new Array(cols);
    for(var k = 0; k < cols; k++){ tableTemp[i][k] = 0; }
  }
return tableTemp;
}

function createTableHTML(table, placedMines) {
  for(var i = 0; i < levels[dificulty].rows; i++){
    var row = document.createElement("tr");
    for(var j = 0; j < levels[dificulty].cols; j++){
      var cell = document.createElement("td");
      cell.onclick = function() { showCell(table, this, placedMines); }
      row.appendChild(cell);
    }
    board.appendChild(row);
  }
}

function sortInNewScore(oldScores, newScore) {
  oldScores = oldScores.split(",");
  var newTime = parseInt(newScore.split(":")[0]);
  var i, sameTimeIndex = false, k;

  outer_loop:
  for(i = 0; i < oldScores.length; i++){
    var currentScore = parseInt(oldScores[i].split(":")[0]);

    if(newTime <  currentScore) { break; }
    else if(newTime == currentScore) {
      var newUser =  newScore.split(":")[1];

      for(k = i; k < oldScores.length; k++){
        var oldUser = oldScores[k].split(":")[1];
        if(newUser < oldUser) {
          sameTimeIndex = k;
          break outer_loop;
        }
      }
      if(k == oldScores.length) { break; }
    }
  }
  if(sameTimeIndex === i) { oldScores.unshift(newScore); }
  else if(sameTimeIndex && sameTimeIndex >= 0) { oldScores.splice(sameTimeIndex, 0, newScore); }
  else if(k == oldScores.length) { oldScores.push(newScore); }
  else { oldScores.splice(i, 0, newScore); }
  return oldScores;
}

function getItemFromStorage(split){
  if     (dificulty == "1") { var scoreVar = localStorage.getItem("scores1"); }
  else if(dificulty == "2") { var scoreVar = localStorage.getItem("scores2"); }
  else if(dificulty == "3") { var scoreVar = localStorage.getItem("scores3"); }

  if(split) { scoreVar = scoreVar.split(","); }
  return scoreVar;
}

function setStorageScore(oldScores){
  if     (dificulty == "1") { localStorage.setItem("scores1", oldScores); }
  else if(dificulty == "2") { localStorage.setItem("scores2", oldScores); }
  else if(dificulty == "3") { localStorage.setItem("scores3", oldScores); }
}

function setNewScore() {

  var newScore = (time-1) + " : " + document.getElementById("username").value;
  try {
    var oldScores = getItemFromStorage("");
    if(oldScores.split(",")[0] == "") { oldScores = oldScores.shift(); }
    oldScores = sortInNewScore(oldScores, newScore);
  }
  catch(err) { var oldScores = new Array(newScore); }
  setStorageScore(oldScores);
}

function showScores() {

  if(multiplayer) {  ranking(dificultyString); return; }

  var scoresArray = getItemFromStorage("split"), message = "";
  if(scoresArray == "") { createSwal("No scores yet!", "Scores:", "info", null); return; }
  for (var i = 0; i < scoresArray.length; i++){
    message += secondsToMinutes(parseInt(scoresArray[i].split(":")[0])) + " " + scoresArray[i].split(":")[1] + '\n';
  }
  createSwal(message, "Scores:", "info", null);
}

function createSwal(msg, title, type, img) {
  swal({
   title: title,
   type: type,
   text: msg,
   animation: "pop",
   imageUrl: img,
   allowEscapeKey: true
 });
}

function gameOverSwal(message) {
  if(message === "YOU WON.") { var image = "resources/thumbsUp.png"; }
  else { var image = "resources/thumbsDown.png"; }
  createSwal(message, "Game Over!", null, image);
}

function playAgain() {
  if(typeof loadBarAnimInterval != "undefined") {
    $("#canvasContainer").remove()
    clearInterval(loadBarAnimInterval);
    loadBarCleared = true;
  }
  if(typeof intervalTimer != "undefined") { clearTimeout(intervalTimer); }
  window.setTimeout(function(){ initVariables(); }, 500);
  document.getElementById("table").style.pointerEvents = 'auto';
}

function setFlagOrQuestionImg(row, col, table) {
  if(row == undefined && col == undefined) { return; }

  if(!flagsAndQuestions.hasOwnProperty(row +","+col)) { var img = "Flag"; flagsAndQuestions[row+','+col] = "F"; }
  else if(flagsAndQuestions[row+','+col] == "F" ) { var img = "Question"; flagsAndQuestions[row+','+col] = "Q"; }
  else if(flagsAndQuestions[row+','+col] == "Q" ) { var img = ""; delete flagsAndQuestions[row+','+col]; }
  if(img === "") { setInnerHTML(row, col, ""); return; }

  var url = getImgURL(img);
  setInnerHTML(row, col, url);

  $("#clicks").fadeOut();
  window.setTimeout(function(){ changeImg(img, ""); }, 350);
}

function changeImg(img, optional) {
  if(img === "Flag") { flags--; }
  else if(img === "Question" || optional) { flags++; }
  document.getElementById("clicks").innerHTML = flags + "/" + levels[dificulty].mines;
  $("#clicks").fadeIn();
  return table;
}

function checkChord(table, row, col, placedMines) {
  var surroundingFlags = 0, bombed = false;

  for(var k = 0; k < positions.length; k++){
    var tableRow = positions[k][0] + row, tableCol = positions[k][1] + col;

    if(tableRow >= 0 && tableRow < levels[dificulty].rows && tableCol >= 0 && tableCol < levels[dificulty].cols){
      if(flagsAndQuestions[tableRow+','+tableCol] == "F"){ surroundingFlags++; continue; }
      if(table[tableRow][tableCol] == -1) { bombed = true; }
    }
  }
  if(surroundingFlags === table[row][col]) {
    if(bombed) { showAllBombs(placedMines); return; }
    showSurroundingSquare(row, col, table);
  }
}

function showSurroundingSquare(row, col, table) {

  for(var k = 0; k < positions.length; k++){
    var tableRow = positions[k][0] + row, tableCol = positions[k][1] + col;

    if(tableRow >= 0 && tableRow < levels[dificulty].rows && tableCol >= 0 && tableCol < levels[dificulty].cols && table[tableRow][tableCol] >= 0) {
      if(table[tableRow][tableCol] == 0) { showEmptyNeighbours(tableRow, tableCol, table); }
      else if(!uncoveredCells.hasOwnProperty(tableRow + ',' + tableCol)) {
        uncoveredCells[tableRow + ',' + tableCol] = 1;
        setInnerHTML(tableRow, tableCol, table[tableRow][tableCol]);
      }
    }
  }
}

function enableChord(row, col, table, placedMines) {
  var cell = board.rows[row].cells[col];
  cell.onclick = function(event) {
    // event.which === 1 means it is a left click
    if(event.which === 1) { checkChord(table, parseInt(row), parseInt(col), placedMines); }
  };
  cell.onmouseup = function(event) {
    // event.which === 3 means it is a right click
    if(event.which === 3) { window.onclick = function(){}; }
  };
}

function rightClick(ev, table, placedMines) {
  ev.preventDefault();
  var row = ev.target.parentNode.rowIndex, col = ev.target.cellIndex;

  if(uncoveredCells.hasOwnProperty(row + ',' + col)) { enableChord(row, col, table, placedMines); return; }

  if(row != undefined && col != undefined) { setFlagOrQuestionImg(row, col, table); }
  else {
    var row = ev.target.parentElement.parentNode.rowIndex, col = ev.target.parentElement.cellIndex;
    setFlagOrQuestionImg(row, col, table);
  }
}

function initVariables() {
  document.getElementById("timer").innerHTML = "00:00";
  board.removeEventListener('contextmenu', listener, false);
  firstClick = true;
  flagsAndQuestions = {};
  firstTry = true;
  time = 0;
  uncoveredCells = {}
}


function showCell(table, cell, placedMines) {
  var row = cell.parentNode.rowIndex, col = cell.cellIndex;
  if(multiplayer) {
    notify(username, server_data.key, server_data.game, row+1, col+1);
    return;
  }
  if(flagsAndQuestions.hasOwnProperty(row+','+col ) || table[row][col] == "-2") { return; }

  if(firstClick) {
    if(table[row][col] === -1) {
      moveBombReturnValues = moveBomb(row, col, table, placedMines);
      table = moveBombReturnValues[0];
      placedMines = moveBombReturnValues[1];
    }
    startTimer();
    firstClick = false;
  }
  if(!uncoveredCells.hasOwnProperty(row + ',' + col)) { uncoveredCells[row + ',' + col] = 1; }

  if(table[row][col] == "-1") { showAllBombs(placedMines); return; }
  if(table[row][col] ==  "0") { table = showEmptyNeighbours(row, col, table); return; }
  if(Object.keys(uncoveredCells).length === totalClickableCells) { setNewScore(); gameOver("YOU WON."); }
  if(table[row][col] != "-2") { setInnerHTML(row, col, table[row][col]); }
  $(board.rows[row].cells[col]).css("visibility", "visible").hide(100).fadeIn(1000);
}

function closeWindow() { self.close(); }

function gameOver(message) {
  gameOverSwal(message);
  clearTimeout(intervalTimer);
  document.getElementById('table').style.pointerEvents = 'none';
}

function setInnerHTML(row, col, message) { board.rows[row].cells[col].innerHTML = message; }

function getImgURL(imgName){
  if(imgName === "Flag") { return '<img class="flag" src="resources/flag.png">'; }
  if(imgName === "Question") { return '<img class="question" src="resources/questionMark.png">'; }
  if(imgName === "Bomb") { return '<img class="bomb" src="resources/bomb.png">'; }
  if(imgName === "BombMe") { return '<img id="bombMe" src="resources/bomb_mine.png">'; }
  if(imgName === "BombEnemy") { return '<img id="bombEnemy" src="resources/bomb_enemy.png">'; }
}

function showAllBombs(placedMines) {
  var bomb_img = getImgURL("Bomb");
  var keys = Object.keys(placedMines);
  for(var i = 0; i < keys.length; i++) {
    var row = keys[i].split(",")[0], col = keys[i].split(",")[1];
    setInnerHTML(row, col, bomb_img);
  }
  gameOver("YOU LOST.");
}

function generateNumber(max) { return Math.round(Math.random() * (max-1)); }

function moveBomb(row, col, table, placedMines) {
  table[row][col] = 0;
  delete placedMines[row + "," + col];
  table = incOneCellsValue(row, col, table);
  table = changeNeighbours(row, col, '-', table);

  var coords = generateMines(1, table, placedMines);
  table = changeNeighbours(coords[0], coords[1], '+', table);

  if(table[row][col] > 0) { setInnerHTML(row, col, table[row][col]); }
  else { table = showEmptyNeighbours(row, col, table); }
  return [table, placedMines];
}

function generateMines(mines, table, placedMines){
  for(var i = 0; i < mines; i++) {
    var found = false, row, col;
    while(!found) {
      row = generateNumber(levels[dificulty].rows), col = generateNumber(levels[dificulty].cols);
      if(!placedMines.hasOwnProperty(row + "," + col)) {
        table[row][col] = -1;
        changeNeighbours(row, col, '+', table);
        placedMines[row + "," + col] = 1;
        found = true;
      }
    }
  }
  if(mines === 1) return [row, col];
  return [table, placedMines];
}

function incOneCellsValue(row, col, table){
  for(var i = 0; i < positions.length; i++){
    var tempRow = row + positions[i][0];
    var tempCol = col + positions[i][1];

    if(tempRow >= 0 && tempRow < levels[dificulty].rows && tempCol >= 0 && tempCol < levels[dificulty].cols){
      if(table[tempRow][tempCol] == -1) { table[row][col]++; }
    }
  }
  return table;
}

function removeFlag(row, col) {
  setInnerHTML(row, col, "");
  changeImg("", "increase");
  delete flagsAndQuestions[row+','+col];
}

function showNeighbours(row, col, table) {
  if(flagsAndQuestions.hasOwnProperty(row+','+col)) { removeFlag(row, col); }
  board.rows[row].cells[col].setAttribute("style", "background-color: white");
  uncoveredCells[row + ',' + col] = 1;
  table[row][col] = -2;

  for(var i = 0; i < positions.length; i++) {
    var tempRow = row + positions[i][0];
    var tempCol = col + positions[i][1];

    if(tempRow >= 0 && tempRow < levels[dificulty].rows && tempCol >= 0 && tempCol < levels[dificulty].cols) {
      if(table[tempRow][tempCol] == 0) { table = showEmptyNeighbours(tempRow, tempCol, table); }

      if(table[tempRow][tempCol]  > 0 && !uncoveredCells.hasOwnProperty(tempRow + ',' + tempCol)) {
        if(flagsAndQuestions.hasOwnProperty(tempRow+','+tempCol)) { removeFlag(row, col); }
        uncoveredCells[tempRow + ',' + tempCol] = 1;
        setInnerHTML(tempRow, tempCol, table[tempRow][tempCol]);
      }
    }
  }
  if(Object.keys(uncoveredCells).length === totalClickableCells) { setNewScore(); gameOver("YOU WON."); }
  return table;
}

function showEmptyNeighbours(row, col, table) {
  $(board.rows[row].cells[col]).css("visibility", "hidden").fadeIn(1000);
  if(dificulty != "3") { window.setTimeout(function(){ table = showNeighbours(row, col, table); }, 30); return table; }
  else { table = showNeighbours(row, col, table); return table; }
}

// (INC|DEC)REMENTS NEIGHBOURS OF A BOMB CELL
function changeNeighbours(row, col, sign, table){
  for(var k = 0; k < positions.length; k++){
    var tableRow = positions[k][0] + row;
    var tableCol = positions[k][1] + col;

    if(tableRow >= 0 && tableRow < levels[dificulty].rows && tableCol >= 0 && tableCol < levels[dificulty].cols){
      if(table[tableRow][tableCol] != -1){
        if(sign === '+') { table[tableRow][tableCol]++; }
        else if(sign === '-') { table[tableRow][tableCol]--; }
      }
    }
  }
  return table;
}

function secondsToMinutes(seconds) {
  var minutes = Math.floor(seconds / 60);
  var seconds = Math.floor(seconds % 60);
  if(seconds < 10) { seconds = "0" + seconds; }
  if(minutes < 10) { minutes = "0" + minutes; }
  return minutes + ":" + seconds;
}

function startTimer() {
  time = 1;
  intervalTimer = window.setInterval(function(){
    document.getElementById("timer").innerHTML = secondsToMinutes(time++);
  }, 1000);
}
