var http = require("http");
var url = require('url');
var mysql = require("mysql");
var connect = require("connect");
var crypto = require("crypto");
var Chance = require("chance"); var chance = new Chance();
var connection = mysql.createConnection({
	host: 'localhost',
	user: 'root',
	database: 'up201304192'
});
connection.connect();

/* Messages To Players */
var gameMessages = {};
var winner = {};
var gameTables = {}, placedMines = {}, games = {}, foundBombs = {};
var opponent = {}, returnValue = {}, keyToGameID = {}, gameToDificulty = {};
var turn = {}, lastGame = {};
var levels = { 'beginner' 		: { rows : 9, cols : 9, mines : 10   },
							 'intermediate' : { rows : 16, cols : 16, mines : 40 },
							 'expert' 			: { rows : 16, cols : 30, mines : 99 }};

function sendResponse(response, returnValue) {
	response.setHeader("Access-Control-Allow-Origin", "*");
	response.writeHead(200, {"Content-Type": "json"});
	response.write(JSON.stringify(returnValue));
	response.end();
}

function checkLoginData(name, original, level, response, join) {
	connection.query('SELECT pass, salt FROM Users WHERE name = ' + connection.escape(name), function(err, rows, fields){
		if(err) { console.log(err); }
		var passFromDB = rows[0].pass;
		var saltFromDB = rows[0].salt;
		var passToTest = original + saltFromDB;
		passToTest = crypto.createHash("md5").update(passToTest).digest("hex");
		if(passToTest == passFromDB) { if(!join) sendResponse(response, {});  }
		else { sendResponse(response, {"error": "User name already exists with a different password"}); if(!join) { return; } }

		if(join) {
			returningResponse = {};
			returningResponse.key = generateKey();

			if(lastGame[level]) { returningResponse.game = lastGame[level]; lastGame[level] = null; }
			else { returningResponse.game = generateRandomNum(12345); lastGame[level] = returningResponse.game; }

			if(games[returningResponse.game] == null) { games[returningResponse.game] = []; }
			games[returningResponse.game].push(name);

			if(gameMessages[returningResponse.game] == null) { gameMessages[returningResponse.game] = {}; }
			gameMessages[returningResponse.game][name] = null;

			winner[returningResponse.game] = "";

			keyToGameID[returningResponse.key] = returningResponse.game;
			createTableMatrix(post.level, returningResponse.game);
			updateRegs();
			sendResponse(response, returningResponse);
		}
	});
}

function addAndOrCheckLogin(name, pass, original, salt, response){
	var insertQuery = "INSERT INTO Users VALUES('" + name + "','" + pass + "','" + salt + "');";
	connection.query(insertQuery, function(err, rows, fields){
		if(err) { checkLoginData(name, original, "", response, false); }
		else { sendResponse(response, {}); }
	});
}

function generateNumber(max) { return Math.round(Math.random() * (max-1)); }
function generateRandomNum(max) { return Math.floor((Math.random() * max) + 1); }
function generateKey() { return chance.string({length: 32, pool: '0123456789abcdef'}); }

function setOptionsHeaders(response) {
	var headers = {};
	headers["Access-Control-Allow-Origin"] = "*";
	headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS";
	headers["Access-Control-Allow-Credentials"] = true;
	headers["Access-Control-Max-Age"] = '86400';
	headers["Access-Control-Allow-Headers"] = "X-Requested-With, Access-Control-Allow-Origin, X-HTTP-Method-Override, Content-Type, Authorization, Accept";
	response.writeHead(200, headers);
	response.end();
}

function createTableMatrix(dificulty, gameID){
	var rows = levels[dificulty].rows, cols = levels[dificulty].cols;
	var table = new Array(rows);
	gameToDificulty[gameID] = dificulty;
	if(gameTables[gameID] == null) {
		for(var i = 0; i < rows; i++){
			table[i] = new Array(cols);
			for(var k = 0; k < cols; k++){ table[i][k] = 0; }
		}
	placedMines[gameID] = {};
	uncoveredCells[gameID] = {};
	gameTables[gameID] = table;

	generateMines(dificulty, gameID);
}
}

function join(request, response){
	if(request.method == 'OPTIONS'){ setOptionsHeaders(response); }
	else if (request.method == 'POST') {
		var body = '';

		request.on('data', function (data) {
			body += data;

			if (body.length > 1e6) { request.connection.destroy(); }
		});
		request.on("end", function(){
			try {
				post = JSON.parse(body);
				checkLoginData(post.name, post.pass, post.level, response, true);
			} catch(e){ /* Body with raw text */ }
		});
	}
}


function generateMines(dificulty, gameID){
	for(var i = 0; i < levels[dificulty].mines; i++) {
		var found = false, row, col;
		while(!found) {
			row = generateNumber(levels[dificulty].rows), col = generateNumber(levels[dificulty].cols);
			if(!placedMines[gameID].hasOwnProperty(row + ", " + col)) {
				gameTables[gameID][row][col] = -1;
				changeNeighbours(row, col, dificulty, gameID);
				placedMines[gameID][row + ", " + col] = 1;
				found = true;
			}
		}
	}
}

function changeNeighbours(row, col, dificulty, gameID){
	var positions = [[-1,-1], [-1,0], [-1,1], [0,-1], [0,1], [1,-1], [1,0], [1,1]];
	for(var k = 0; k < positions.length; k++){
		var tableRow = positions[k][0] + row;
		var tableCol = positions[k][1] + col;

		if(tableRow >= 0 && tableRow < levels[dificulty].rows && tableCol >= 0 && tableCol < levels[dificulty].cols){
			if(gameTables[gameID][tableRow][tableCol] != -1){
				gameTables[gameID][tableRow][tableCol]++;
			}
		}
	}
}

var uncoveredCells = {}
function showNeighbours(row, col, floodFillCells, gameID) {
	var positions = [[-1,-1], [-1,0], [-1,1], [0,-1], [0,1], [1,-1], [1,0], [1,1]];
	var dificulty = gameToDificulty[gameID];
	gameTables[gameID][row][col] = -2;
	uncoveredCells[gameID][row+","+col] = 1;
	if(floodFillCells.indexOf(row+","+col) == -1){ floodFillCells.push(row+","+col); }

	for(var i = 0; i < positions.length; i++) {
		var tempRow = row + positions[i][0];
		var tempCol = col + positions[i][1];

		if(tempRow >= 0 && tempRow < levels[dificulty].rows && tempCol >= 0 && tempCol < levels[dificulty].cols) {
			if(gameTables[gameID][tempRow][tempCol] == 0) { floodFillCells = showNeighbours(tempRow, tempCol, floodFillCells, gameID); }

			if(gameTables[gameID][tempRow][tempCol]  > 0 && !uncoveredCells[gameID].hasOwnProperty(tempRow+","+tempCol)) {
				uncoveredCells[gameID][tempRow+","+tempCol] = 1;
				floodFillCells.push(tempRow+","+tempCol);
			}
		}
	}
	return floodFillCells;
}

function play(row, col, game, key, name, response) {
	if(keyToGameID[key] == game) {
		if(turn[game] == name) {
			if(uncoveredCells[game][parseInt(row-1)+","+parseInt(col-1)] != 1){
				sendResponse(response, {});

				if(gameTables[game][row-1][col-1] != -1) {
					turn[game] = opponent[turn[game]];

					if(gameTables[game][row-1][col-1] == 0) {
						var cells = showNeighbours(row-1, col-1, [], game);
						for(var i = 0; i < cells.length; i++){
							var newRow = cells[i].split(",")[0], newCol = cells[i].split(",")[1];
							if(gameTables[game][newRow][newCol] == -2) { var convertedValue = 0; }
							else {  var convertedValue = gameTables[game][newRow][newCol]; }
							cells[i] = [parseInt(newRow)+1, parseInt(newCol)+1, convertedValue];
						}
					} else { var cells = [[row, col, gameTables[game][row-1][col-1]]]; }
				}
				else {
					foundBombs[turn[game]] += 1;
					if( foundBombs[turn[game]] == Math.ceil(levels[gameToDificulty[game]].mines / 2) ) {
						gameMessages[game][opponent[turn[game]]] = {"move": {"name": name, "cells": [[row, col, gameTables[game][row-1][col-1]]]}, "winner": turn[game]};
						gameMessages[game][turn[game]]           = {"move": {"name": name, "cells": [[row, col, gameTables[game][row-1][col-1]]]}, "winner": turn[game]};
						winner[game] = turn[game];
						clearGame(game);
						return;
					}
					var cells = [[row, col, -1]];
				}
				gameMessages[game][opponent[turn[game]]] = {"move": {"name": name, "cells": cells}, "turn": turn[game]};
				gameMessages[game][turn[game]]           = {"move": {"name": name, "cells": cells}, "turn": turn[game]};
				uncoveredCells[game][parseInt(row-1)+","+parseInt(col-1)] = 1;
			} else {
				sendResponse(response, {"error": "Cell is already uncovered"});
			}
		} else {
			sendResponse(response, {"error": "Not your turn"});
		}
	}
}

function notify(request, response) {
	if(request.method == 'OPTIONS'){ setOptionsHeaders(response); }
	else if (request.method == 'POST') {
		var body = '';

		request.on('data', function (data) {
			body += data;
			if (body.length > 1e6) { request.connection.destroy(); }
		});
		request.on("end", function(){
			try {
				post = JSON.parse(body);
				play(post.row, post.col, post.game, post.key, post.name, response);
				if(winner[post.game] != "") {
					connection.query('SELECT * FROM Rankings WHERE name ="' + post.name + '" AND level="' + gameToDificulty[post.game] + '";', function(err, rows, fields){
						if(Object.keys(rows).length == 0){
							connection.query('INSERT INTO Rankings VALUES("' + winner[post.game] + '", "'
											+ gameToDificulty[post.game] + '", "1", CURRENT_TIMESTAMP);',
											function(err, rows, fields){
												if(err) { console.log(err); }
												gameToDificulty[post.game] = "";
												winner[post.game] = "";
											});
						}
						else {
							connection.query('UPDATE Rankings SET score="' + parseInt(rows[0].score + 1) + '", timestamp=CURRENT_TIMESTAMP'
											+ ' WHERE name="' + winner[post.game] + '" AND level="' + gameToDificulty[post.game] + '";' ,
											function(err, rows, fields){
												if(err) { console.log(err); }
												gameToDificulty[post.game] = "";
												winner[post.game] = "";
											});
						}
					});
				}
			} catch(e) { console.log(e); }
		});
	}
}

function ranking(request, response){
	if(request.method == 'OPTIONS'){ setOptionsHeaders(response); }
	else if (request.method == 'POST') {
		var body = '';

		request.on('data', function (data) {
			body += data;
			if (body.length > 1e6) { request.connection.destroy(); }
		});
		request.on("end", function(){
			try {
				post = JSON.parse(body);
				// post.level
				connection.query('select * from Rankings where level = "' + post.level + '" order by score desc, timestamp asc  limit 10', function(err, rows, fields){
					if(err) { console.log(err); }
					var responseToSend = {};
					responseToSend["ranking"] = [];
					for(var i = 0; i < rows.length; i++){
						responseToSend["ranking"].push({"name" : rows[i].name, "score": rows[i].score});
					}
					sendResponse(response, responseToSend);
				});

			} catch(e) { console.log(e); }
		});
	}
}

function updateRegs() {
	for(gameID in games) {
		if(games[gameID].length > 1) {
			opponent[games[gameID][0]]   = games[gameID][1];
			opponent[games[gameID][1]]   = games[gameID][0];

			foundBombs[games[gameID][0]] = 0;
			foundBombs[games[gameID][1]] = 0;

			gameMessages[gameID][turn[gameID]]           = {"opponent": opponent[turn[gameID]], "turn": turn[gameID] };
			gameMessages[gameID][opponent[turn[gameID]]] = {"opponent": turn[gameID]          , "turn": turn[gameID] };
		}
		turn[gameID] = games[gameID][0];
	}
}

function clearGame(gameID){
	gameTables[gameID] = [];
	placedMines[gameID] = {};
	uncoveredCells[gameID] = {};
	games[gameID] = [];
	opponent[gameID] = {};
	foundBombs[gameID] = {};
	keyToGameID[gameID] = {};
	turn[gameID] = "";
	returnValue = {};
}

function score(request, response){
	if(request.method == 'OPTIONS'){ setOptionsHeaders(response); }
	else if (request.method == 'POST') {
		var body = '';

		request.on('data', function (data) {
			body += data;
			if (body.length > 1e6) { request.connection.destroy(); }
		});
		request.on("end", function(){
			try {
				post = JSON.parse(body);
				connection.query('select score from Rankings where name = "' + post.name + '" and level = "' +
					post.level + '";', function(err, rows, fields){
						if(err || Object.keys(rows).length == 0) { sendResponse(response, {"score": "0"}); }
						else { sendResponse(response, {"score": rows[0].score}); }
				});
			} catch(e) { console.log(e); }
		});
	}
}

function update(request, response){
	response.setHeader("Access-Control-Allow-Origin", "*");
	response.writeHead(200, {"Content-Type":"text/event-stream", "Cache-Control":"no-cache", "Connection":"keep-alive"});
	response.write("retry: 10000\n");
	response.write("event: connecttime\n");
	response.write("data: " + JSON.stringify(null) + "\n\n");

	setInterval(function() {
		if(request.method == 'GET') {
			var urlParsed = url.parse(request.url,true);
			var name = urlParsed.query.name, game = urlParsed.query.game;
			if(JSON.stringify(gameMessages[game][name]) != "{}" && gameMessages[game][name] != null) {
				response.write("data: " + JSON.stringify(gameMessages[game][name]) + "\n\n");
				gameMessages[game][name] = {};
			}
		}
	}, 300);
}

function register(request, response){
	if(request.method == 'OPTIONS'){ setOptionsHeaders(response); }
	else if (request.method == 'POST') {
		var body = '';

		request.on('data', function (data) {
			body += data;

			if (body.length > 1e6) { request.connection.destroy(); }
		});
		request.on("end", function(){
			try {
				post = JSON.parse(body);
				var salt = chance.string({length: 4});
				var hash = crypto.createHash("md5").update(post.pass + salt).digest("hex");

				addAndOrCheckLogin(post.name, hash, post.pass, salt, response);

			} catch(e){ console.log(e); }
		});
	}
}

var app = connect();
app.use("/join", join);
app.use("/register", register);
app.use("/update", update);
app.use("/notify", notify);
app.use("/ranking", ranking);
app.use("/score", score);
http.createServer(app).listen(8040);
