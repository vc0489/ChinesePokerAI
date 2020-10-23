
// Array to store computer splits
var comSplitInfo = new Array(3);
for (let cI=0; cI<3; cI++) {
  comSplitInfo[cI] = {
    'SplitInds':null,
    'SplitCodes':null,
  };
}
var playerSplitWithCom100;

var randomSplitOutput;
var allSplitDesc = new Array(4);
for (let pI=0; pI<4; pI++) {
  allSplitDesc[pI] = new Array(3);
}

var cardIdPrefix;

// Game variables
var gameID;
var seatID;
var dealtCardImgFilesFull;
var dealtCardImgFiles;
var setCodes = ['()', '()', '()'];
var n_cards_in_set = [0, 0, 0];
const setLengths = [3,5,5];
var comDifficulty = [undefined, undefined, undefined];
var appGameID = undefined;
var appRoundID = undefined;
//var completedGameData = {
//  'ComDifficulty': undefined,
//  'GameScoreHistory': undefined,
//  'HandHistory': undefined
//}

//var cumGameScores = [0, 0, 0, 0];
var gameScoreHistory;
var playerScoreHistoryCom100;
var handHistory;
var nRoundsPlayed; // Number of rounds played

//var firstGame = true;
var handRankEl;
var clientIp;
// Initalise upon load
window.onload = initialiseGame;

function updateStatus(statusText, textColor=undefined) {
  statusTextEl = $( ".status-text" )
  statusTextEl.html(statusText);
  if (textColor != undefined) {
    statusTextEl.css('color', textColor);
  }
}

function initialiseGame() {
  $.ajax({
    type: 'GET',
    contentType: 'application/json',
    url: '/get/initialise',
  }).done(function(response) {
    cardIdPrefix = response['CardIdPrefix'];
    console.log('Initalisation successful');
    $( "#button-new-game" ).attr("disabled", false);
    
    
    updateStatus('Ready for new game', 'green');
  }).fail(function(xhr, textStatus, errorThrown) {
    console.log('Error during initialisation');
  });


  handRankEl = document.getElementById("hand-ranks-hover");
  handRankEl.addEventListener('dragstart', dragStart, false);
  document.addEventListener('dragover', dragOver, false);
  document.addEventListener('drop', dropElement, false);
  
  document.getElementById("hand-rank-toggle").addEventListener("click", showHandRankToggle);

  // Add button event handlers
  document.getElementById("button-new-game").addEventListener("click", newGame);
  document.getElementById("button-new-round").addEventListener("click", newRound);
  document.getElementById("button-score-table-toggle").addEventListener("click", showScoreTableToggle);
  //document.getElementById("button-submit-score").addEventListener("click", submitScore);
  document.getElementById("button-end-game").addEventListener("click", endGame);

  document.getElementById("submit-score-form").addEventListener("submit", submitScore);
  

  // COM slider event handers
  for (let comId=1; comId<=3; comId++) {
    document.getElementById("COM" + comId.toString() + "-slider").addEventListener("input", updateComDifficulty);
  }
}



function newGame() {
  /*
  if (firstGame == true) {
    firstGame = false;
  } else {
    res = confirm("This will reset all scores. Continue?");
    if (res == false) {
      return;
    }
  }
  */

  gameScoreHistory = [[],[],[],[]];
  playerScoreHistoryCom100 = [];
  handHistory = [];

  nRoundsPlayed = 0;
  resetScoreTable();
  clearAllCards();
  updateStatus("Press 'Next round' to play round 1", 'green');
  

  $( "#button-new-game" ).attr("disabled", true);
  
  $( "#button-score-table-toggle" ).attr("disabled", false);
  for (let comID=1; comID<=3; comID++) {
    $( "#COM" + comID.toString() + " .container-status" ).html('Ready!');
    $( "#COM" + comID.toString() + "-slider" ).attr("disabled", true);
    
    comDifficulty[comID-1] = document.getElementById( "COM" + comID.toString() + "-slider" ).value;
  }
  $( "#score-table" ).hide();
  $( "#submit-score-section" ).hide();
  $( "#high-score-table-section" ).hide();

  function createAppGameDbRow() {
    return new Promise((resolve, reject) => {
      $.ajax({
        type: 'POST',
        contentType: 'application/json',
        url: '/post/gen_app_game_id',
        dataType: 'json',
        data: JSON.stringify({
          'ClientIP':clientIp,
          'ComDifficulty': comDifficulty,
        }),
        success: function(data) {
          appGameID = data['AppGameID'];
          $( "#button-new-round" ).attr("disabled", false);
          resolve();
        },
        error: function(error) {
          reject(error);
        },
      })
    })
  }

  getClientIp()
    .then(createAppGameDbRow);

}

function roundDecimal(val, dps) {
  return Math.round((val + Number.EPSILON) * Math.pow(10,dps)) / Math.pow(10,dps)
}
function endGame() {
  // Display some information (history?)
  // Clear cards
  // Show high score table
  // Option to submit score
  // Activate computer difficulty sliders
  // Activate new game button
  // Deactivate some buttons
  $( "#score-table" ).show();
  for (let comID=1; comID<=3; comID++) {
    $( "#COM" + comID.toString() + " .container-status" ).html('zzz...');
    
    
    $( "#COM" + comID.toString() + "-slider" ).attr("disabled", false);
    document.getElementById( "COM" + comID.toString() + "-slider" ).value = comDifficulty[comID-1];
    //comDifficulty[comID-1] = document.getElementById( "COM" + comID.toString() + "-slider" ).value;
  }

  $( "#button-new-game" ).attr("disabled", false);
  $( "#button-new-round" ).attr("disabled", true);
  $( "#button-submit-score" ).attr("disabled", false);
  $( "#submit-score-section" ).show();
  
  $( "#end-game-n-rounds").html(nRoundsPlayed.toString());
  let avgScore = sumArray(gameScoreHistory[0])/gameScoreHistory[0].length;
  avgScoreR = roundDecimal(avgScore,2);
  //avgScoreR = Math.round((avgScore + Number.EPSILON) * 100) / 100;
  $( "#end-game-avg-score").html(avgScoreR.toString());
  
  
  let tempScore = sumArray(playerScoreHistoryCom100)
  $( "#end-game-pot-tot-score").html(tempScore.toString());
  tempScore = tempScore/playerScoreHistoryCom100.length
  tempScoreR = roundDecimal(tempScore,2);
  //tempScoreR = Math.round((tempScore + Number.EPSILON) * 100) / 100
  $( "#end-game-pot-avg-score").html(tempScoreR.toString());
  
  //tempScoreR = Math.round((avgScore - tempScore + Number.EPSILON) * 100) / 100
  tempScoreR = roundDecimal(avgScore - tempScore,2);
  $( "#end-game-CPT-score" ).html(tempScoreR.toString());
  // TODO: Generate plot of games
  
  // Send ajax request to server to update DB with game completion
  $.ajax({
    type: 'POST',
    contentType: 'application/json',
    url: '/post/end_game',
    dataType: 'json',
    data: JSON.stringify({
      'AppGameID':appGameID, 
      'NoRounds': nRoundsPlayed,
      'TotScore': sumArray(gameScoreHistory[0]),
      'TotCptScore': sumArray(playerScoreHistoryCom100)
    }),
    retryLimit: 3,
    tryCount: 0,
    success: function() { 
      console.log("End game submitted to server");
    },
    error: function(jqXHR, textStatus, errorThrown) {
      //alert('Error: getComputerSplit fail for com_id=' + com_id.toString());
      //console.log(jqXHR);
      //console.log(textStatus);
      //console.log(errorThrown);
      if (this.tryCount < this.retryLimit) {
        // Try again
        this.tryCount++;
        $.ajax(this);
        console.log(this.tryCount);
      } else {
        console.log("end_game failed")
      }
    },
  })

  if (nRoundsPlayed < 10) {
    $( "#end-game-no-score-submit" ).show();
    $( "#end-game-score-submit" ).hide();
  } else {
    $( "#end-game-no-score-submit" ).hide();
    $( "#end-game-score-submit" ).show();
  }

  $( "#button-end-game" ).attr("disabled", true);
}

var tempEvent;
function updateComDifficulty(event) {
  console.log("Hi")
  tempEvent = event.target;
  event.target.nextElementSibling.innerHTML = event.target.value;
}
function clearAllCards() {
  // Remove dealt cards display
  
  // Remove cards
  // -- document.querySelectorAll(".card").forEach(e => e.remove()); <- JS equivalent
  $( ".card" ).remove();
  $( ".card-set" ).empty();

  // Remove set desciptions
  clearSetDescriptions(false);

  // Reset computer status (to Waiting...)
  for (let comID=1; comID<=3; comID++) {
    $( "#COM" + comID.toString() + " .container-status" ).empty();
  }

  
}

function getPlayerSplitUsingCom100Strat() {
  return new Promise((resolve, reject) => {
    $.ajax({
      type: 'POST',
      contentType: 'application/json',
      url: '/post/get_computer_split',
      dataType: 'json',
      data: JSON.stringify({
        'ComID':0, 
        'Difficulty': 100,
        'AppRoundID': appRoundID,
        'IsTrueCom': false
      }),
      retryLimit: 3,
      tryCount: 0,
      success: function(response) {
        resolve(response);
      },
      error: function(jqXHR, textStatus, errorThrown) {
        //alert('Error: getComputerSplit fail for com_id=' + com_id.toString());
        //console.log(jqXHR);
        //console.log(textStatus);
        //console.log(errorThrown);
        if (this.tryCount < this.retryLimit) {
          // Try again
          this.tryCount++;
          $.ajax(this);
          console.log(this.tryCount);
        } else {
          reject(jqXHR)
        }
      },
    })
  })
}

function getComputerSplitNew(com_id) {
  console.log('Getting best split for COM' + com_id.toString())
  $( "#COM" + com_id.toString() + " .container-status" ).html("Thinking...")
  updateStatus('Round ' + (nRoundsPlayed+1).toString() + ' - COM thinking - select your split', 'red');
  
  return new Promise((resolve, reject) => {
    $.ajax({
      type: 'POST',
      contentType: 'application/json',
      url: '/post/get_computer_split',
      dataType: 'json',
      data: JSON.stringify({
        'ComID':com_id, 
        'Difficulty': comDifficulty[com_id-1],
        'AppRoundID': appRoundID,
        'IsTrueCom': true
      }),
      retryLimit: 3,
      tryCount: 0,
      success: function(response) {
        let pool_id="#COM" + com_id.toString() +  "-pool";
        card_back = $( pool_id ).children(":first");
        $( pool_id ).empty();
        for (let setNo = 1; setNo <= 3; setNo++)
        {
          set_id = "#COM" + com_id.toString() + "-set" + setNo.toString();
          for (let c=0; c<setLengths[setNo-1]; c++) {
            $( set_id ).append(card_back.clone());
          }
        }
        $( "#COM" + com_id.toString() + " .container-status" ).html("Ready!")
  
        comSplitInfo[com_id-1]['SplitInds'] = response['SplitInds'];
        comSplitInfo[com_id-1]['SplitCodes'] = response['SplitCodes'];
        resolve(comSplitInfo[com_id-1]);
      },
      error: function(jqXHR, textStatus, errorThrown) {
        //alert('Error: getComputerSplit fail for com_id=' + com_id.toString());
        //console.log(jqXHR);
        //console.log(textStatus);
        //console.log(errorThrown);
        if (this.tryCount < this.retryLimit) {
          // Try again
          this.tryCount++;
          $.ajax(this);
          console.log(this.tryCount);
        } else {
          reject(jqXHR)
        }
      },
    })
  })
}
var comSplits; // VC: temp to check com selected split output


function newRound() {
  //window.location.href='{{ url_for('play_game') }}';

  function clearAllCardsPromise() {
    return new Promise((resolve, reject) => {
      clearAllCards();
      resolve();
    })
  }
  function dealRoundCardsPromise() {
    return new Promise((resolve, reject) => {
      $.ajax({
        type: 'POST',
        contentType: 'application/json',
        url: '/post/deal_new_round',
        dataType: 'json',
        data: JSON.stringify({}),
        success: function(data) {
          resolve(data);
        },
        error: function(error) {
          reject(error);
        },
      })
    })
  }
  
  function showDealtCardsPromise(response) {
    return new Promise((resolve, reject) => {
      gameID = response['GameID'];
      seatID = response['SeatID'];
      handHistory.push([gameID, seatID]);
      dealtCardImgFilesFull = response['DealtCardsImgFilenamesFull'];
      dealtCardImgFiles = response['DealtCardsImgFilenames'];
      displayDealtCardsFull();
      displayDealtCardsSet();
      displayComCards();
      $( "#card-pool, #set1, #set2, #set3" ).sortable("enable");
      n_cards_in_set = [0, 0, 0];
      resolve();
      //resolve({'a':1, 'b':2});
    })
  }
  
  function addRoundInfoToDBPromise() {
    return new Promise((resolve, reject) => {
      //Update CPT_rounds
      $.ajax({
        type: 'POST',
        contentType: 'application/json',
        url: '/post/add_round_info_to_db',
        dataType: 'json',
        data: JSON.stringify({
          'AppGameID': appGameID,
          'HandGameID': gameID,
          'HandSeatID': seatID,
          'RoundNo': handHistory.length,
        }),
        success: function(data) {
          appRoundID = data['AppRoundID'];
          resolve();
        },
        error: function(error) {
          reject(error);
        },
      });
    })
  }
  
  function getComSplitsPromise() {
    return Promise.all([getComputerSplitNew(1), getComputerSplitNew(2), getComputerSplitNew(3)])
  }
  
 $( "#button-submit" ).hide();
  $( "#button-new-game" ).prop("disabled", true);
  $( "#button-new-round" ).prop("disabled", true);
  $( "#score-table" ).hide();
  $( "#button-score-table-toggle" ).html("Show scores");    
  updateScoreTableClearGame();
  
  clearAllCardsPromise()
    .then(dealRoundCardsPromise)
    .then(showDealtCardsPromise)
    .then(addRoundInfoToDBPromise)
    .then(function(result) {
      //console.log(result);
      //$( "#button-reset" ).attr("disabled", false);
      $( "#button-random" ).attr("disabled", false);
    })
    .then(getComSplitsPromise)
    .then(function(result) {
      comSplits = result;
      updateStatus('Round ' + (nRoundsPlayed+1).toString() + ' - COM ready - select your split', 'green');
    })
    .then(getPlayerSplitUsingCom100Strat) 
    .then(function(result) {
      playerSplitWithCom100 = result['SplitCodes'];
      $( "#button-submit" ).show();
    })
    .finally(() => {
      //$( "#button-new-game" ).attr("disabled", false);
      //$( "#button-new-round" ).attr("disabled", true);
    });
}

function showScoreTableToggle() {
  toggleButtonEl = $( )
  if ($( "#score-table" ).css('display') == 'table') {
    $( "#score-table" ).hide();
    $( "#button-score-table-toggle" ).html("Show scores");
  } else {
    $( "#score-table" ).show();
    $( "#button-score-table-toggle" ).html("Hide scores");
    window.scrollTo(0,0);
  }
}

// <img src="/static/CardImages/{{ img_info[0] }}.png", width="35", height="66", title="{{ img_info[1] }}">
function genCardImgEl(filebase, title, width=35, height=66) {
  imgEl = $( "<img>" )
    .attr({
      "src": `/static/CardImages/${filebase}.png`,
      "title": title,
      "width": width,
      "height": height
    });
  return imgEl;
}

function genCardDivEl(filebase, id=undefined) {
  divEl = $( "<div>" )
    .addClass("card")
    .css({
      "background-image": 'url("/static/CardImages/' + filebase + '.png")',
      "background-size": "cover"
    });
  if (id !== null)
    divEl.prop("id", id);
  return divEl;  
}
function displayDealtCardsFull() {
  // Shows grid of cards, dealt cards shown face up while
  // other cards are shown face down
  mainDiv = $( ".card-set" );
  mainDiv.empty();
  // dealtCardImgFilesFull
  for (let sI=0; sI<4; sI++) {
    for (let cI=0; cI<13; cI++) {
      imgEl = genCardImgEl(dealtCardImgFilesFull[sI][cI][0], dealtCardImgFilesFull[sI][cI][1]);

      /*
      if (dealtCardImgFilesFull[sI][cI][1] == "Not selected") {
        
      } else {
        imgEl = genCardImgEl(dealtCardImgFilesFull[sI][cI][0], dealtCardImgFilesFull[sI][cI][1]);
      }
      */
     mainDiv.append(imgEl);
    }
    mainDiv.append( $( "<br>" ) );
  }
}

function displayDealtCardsSet() {
  containerDiv = $( "#card-pool" );
  for (let cI=0; cI<13; cI++) {
    divEl = genCardDivEl(dealtCardImgFiles[cI][0], cardIdPrefix + cI.toString());
    containerDiv.append(divEl);
  }
}


function displayComCards() {
  cardEl = genCardDivEl('BlackBack');
  for (let comI=1; comI<=3; comI++) {
    comPoolEl = $( "#COM" + comI.toString() + "-pool" );
    for (let cI=0; cI<13; cI++) {
      comPoolEl.append(cardEl.clone());
    }
  }
}

function assignRandomSplitOutput(output)  {
  randomSplitOutput = output;
}

function updateSetContainersWithFullSplit(
  containerID,
  fileArray,
  descArray,
  cardIdPrefix
) {

  var card_sel;
  
  console.log(fileArray);
  outerDivID =  "#" + containerID;
  // First, empty cards from pool and sets
  $( outerDivID  + " .container-pool").empty();

  for (setInd=0; setInd<3; ++setInd) {
    setSelector = outerDivID + " .set-container-full > div:nth-child(" + (setInd+1).toString() + ")";
    
    $( setSelector ).empty();
  }
  // Second, loop over sets and add card images and descriptions
  for (let setInd=0; setInd<3; ++setInd) {
    setSelector = outerDivID + " .set-container-full > div:nth-child(" + (setInd+1).toString() + ")";
    setNumStr = (setInd+1).toString();
    
    setLength = setLengths[setInd]
    for (let cardInd=0; cardInd<setLength; ++cardInd) {
      card_el = $('<div></div>');  
      card_el.attr('class','card');
      card_el.attr('id',cardIdPrefix + fileArray[setInd][cardInd][2]); // Ind in dealt cards
      card_el.attr('style',"background-image: url('/static/CardImages/" + fileArray[setInd][cardInd][0] + ".png'); background-size:cover;");
      
      //console.log(card_el);
      $( setSelector ).append(card_el);
      
    }
    set_desc = constructHeaderContent(setInd+1, descArray[setInd]);
    $( outerDivID + " .header" + setNumStr ).html(set_desc);
  }
}

function randomSplit() {
  $.ajax({
    type: 'POST',
    contentType: 'application/json',
    url: '/post/random_valid_split',
    dataType: 'json',
    data : JSON.stringify({}),
  }).done(function(response) {
    
    assignRandomSplitOutput(response); // VC: remove later
    
    allSplitDesc[0] = [response['set1Desc'], response['set2Desc'], response['set3Desc']];
    updateSetContainersWithFullSplit(
      "USER",
      [response['set1Files'],response['set2Files'],response['set3Files']],
      allSplitDesc[0],
      response['CardIdPrefix'],
    );
    
    setCodes = [response['set1Code'],response['set2Code'],response['set3Code']];
    n_cards_in_set = [...setLengths];
    $( "#button-submit" ).attr("disabled", false);
    $( "#button-reset" ).attr("disabled", false);
  }).fail(function() {
    alert('Error: Could not contact server');
  });
}

var is_valid;
function callback(response) {
  is_valid = response;
}

function validateSplit() {

  for (sI=0; sI<3; sI++) {
    if (n_cards_in_set[sI] != setLengths[sI]) {
      return false;
    }
  }

  //var is_valid = false;
  // Check code strength ascending
    
  $.ajax({
    type: 'POST',
    contentType: 'application/json',
    url: '/post/check_valid_split',
    dataType: 'json',
    data : JSON.stringify({
      'set1Code':setCodes[0],
      'set2Code':setCodes[1],
      'set3Code':setCodes[2],
    }),
  }).done(function(response) {
    var tmp_is_valid;
    if (response['isValid'] == 0) {
      alert('Invalid split');
      tmp_is_valid = false;
    } else {
      alert('Valid split');
      tmp_is_valid = true;
    }
    callback(tmp_is_valid)
    //alert(response['Description']);
    //html_content = 'Set ' + targetIdNum + ' (' + targetSetLength.toString() + ' cards)' + '<br>' + response['Description'];
    //$('#header' + targetIdNum).html(html_content);
    //setCodes[parseInt(targetIdNum)-1] = response['SetCode'];
    //console.log("respone['SetCode']:" + response['SetCode']);
    //console.log('setCodes:' + setCodes.toString());
    //alert(html_content)
  }).fail(function() {
    alert('Error: Could not contact server');
  });
    
  
  return is_valid;
}



function resetCards() {
  for (let cI=0; cI<13; cI++) {
    $( "#card-pool" ).append($( "#c" + cI.toString() ));
  }
  n_cards_in_set = [0, 0, 0];

  clearSetDescriptions();
}

function clearSetDescriptions(userOnly=true) {
  let htmlContent;
  for (let sI=1; sI<=3; sI++) {
    htmlContent = constructHeaderContent(sI);
    $( "#USER .header" + sI.toString() ).html(htmlContent);
  }

  if (userOnly == false) {
    for (let comID=1; comID<=3; comID++) {
      for (let sI=1; sI<=3; sI++) {
        //htmlContent = constructHeaderContent(sI);
        $( "#COM" + comID.toString() + " .header" + sI.toString() ).html('Set ' + sI.toString());
      }
    }
  }
}

var compRes; // VC: temp to store split comparison results
//var gameScores;

function getSplitInds() {
  let splitInds = [[],[],[]];
  for (let sI=0; sI<3; sI++) {
    $( "#set" + (sI+1).toString() ).sortable("toArray").forEach(function(item) {
      splitInds[sI].push(parseInt(item.substring(1)));
    })
  }
  return splitInds;
}
function playHand() {
  
  let gameScores;
  $( "#card-pool, #set1, #set2, #set3" ).sortable("disable");
  $( "#gameplay-button-container button" ).attr("disabled", true);
  
  splitInds = getSplitInds();
  console.log(splitInds);
  // VC: server side need to sort cards
  $.ajax({
    type: 'POST',
    contentType: 'application/json',
    url: '/post/play_hand',
    dataType: 'json',
    data : JSON.stringify({
      'Set1Code':setCodes[0],
      'Set2Code':setCodes[1],
      'Set3Code':setCodes[2],
      'Set1CodeCom100':playerSplitWithCom100[0],
      'Set2CodeCom100':playerSplitWithCom100[1],
      'Set3CodeCom100':playerSplitWithCom100[2],
      'Com1SplitInfo':comSplitInfo[0],
      'Com2SplitInfo':comSplitInfo[1],
      'Com3SplitInfo':comSplitInfo[2],
      'AppGameID': appGameID,
      'AppRoundID': appRoundID,
      'SplitInds': splitInds,
    }),
  }).done(function(response) {
    console.log(response);
    compRes = response['SplitComp'];
    gameScores = response['GameScores'];

    for (let com_id=1; com_id<=3; com_id++) {
      updateSetContainersWithFullSplit(
        "COM"+com_id.toString(),
        response['Com' + com_id.toString() + 'Files'],
        response['Com' + com_id.toString() + 'SplitDesc'],
        'COM' + com_id.toString() + 'c'
      );
      allSplitDesc[com_id] = response['Com' + com_id.toString() + 'SplitDesc'];
    }
    
    for (let pI=0; pI<4; pI++) {
      gameScoreHistory[pI].push(response['TotGameScores'][pI]);
    }
    updateScoreTable(gameScores);
    
    playerScoreHistoryCom100.push(response['TotGameScoresCom100'][0])
    // Show score table
    $( "#score-table" ).show();
    $( "#button-score-table-toggle" ).html("Hide scores");
    $( "#button-new-round" ).attr("disabled", false);
    $( "#button-end-game" ).attr("disabled", false);
    nRoundsPlayed += 1;
    updateStatus("Press 'Next round' to  play round " + (nRoundsPlayed+1).toString(), 'green');
    //gameScores[]
    window.scrollTo(0,0);
  })
}


function constructHeaderContent(setNo, desc=undefined) {
  setLength = setLengths[setNo-1];
  html_content = 'Set ' + setNo.toString() + ' (' + setLength.toString() + ' cards)';
  if (typeof desc !== "undefined") {
    html_content += '<br>' + desc;
  }
  return html_content;
}





// Scoreboard functions
function sumArray(toSum) {
  sum = toSum.reduce(function(a, b) {
    return a + b;
  });
  return sum;
}

function getCumGameScores() {
  

  let cumGameScores = [0, 0, 0, 0];
  if (gameScoreHistory[0].length > 0) {
    for (let pI=0; pI<4; pI++) {
      cumGameScores[pI] = sumArray(gameScoreHistory[pI]);
    }
  };
  return cumGameScores;
}
function resetScoreTable() {
  var cellSelector;
  var colInd;
  for (let p1=0; p1<4; p1++) {
    colInd=0;
    for (let p2=0; p2<4; p2++) {
      if (p1==p2) {
        continue;
      }
      cellSelector = ".score-row:eq(" + 
        (p1).toString() + 
        ") > .cell-score-base:eq(" +
        (colInd).toString() +
        ")";
      //console.log(cellSelector);

      $(cellSelector).empty();
      colInd++;
    }

    cellSelector = ".score-row:eq(" + 
        (p1).toString() + 
        ") > .cell-score-tot:eq(0)";
    $(cellSelector).empty();

    cellSelector = ".score-row:eq(" + 
        (p1).toString() + 
        ") > .cell-score-tot:eq(1)";
    $(cellSelector).html('0');
  }
}

function updateScoreTableClearGame() {
  var cellSelector;
  var colInd;
  $( ".cell-score-base" ).empty();
  for (let pI=0; pI<4; pI++) {
    cellSelector = ".score-row:eq(" + 
        (pI).toString() + 
        ") > .cell-score-tot:eq(0)";
    $(cellSelector).empty()
  }
}

function updateScoreTable(gameScores) {
  var cellSelector;
  var colInd;
  var playerGameScore;
  let cumGameScores = getCumGameScores(); // Get total game score over all rounds
  for (let p1=0; p1<4; p1++) {
    colInd=0;
    for (let p2=0; p2<4; p2++) {
      if (p1==p2) {
        continue;
      }

      cellSelector = ".score-row:eq(" + 
        (p1).toString() + 
        ") > .cell-score-base:eq(" +
        (colInd).toString() +
        ")";
      //console.log(cellSelector);

      $(cellSelector).html(gameScores[p1][p2].toString());
      colInd++;

      hoverEl = $("<div></div>")
      hoverEl.addClass("score-cell-hover")

      tableEl = $( "<table></table>" )
      for (let sI=0; sI<3; sI++) {
        rowEl = $( "<tr></tr>" )
        rowEl.append("<td>Set " + (sI+1).toString() + "</td>");

        forDesc = allSplitDesc[p1][sI]
        agaDesc = allSplitDesc[p2][sI]
        if (compRes[p1][p2][sI] == 1) {
          forDesc = "<b>" + forDesc + "</b>";
          compSymbol = ">";
          compScore = "+1";
        } else if (compRes[p1][p2][sI] == -1) {
          agaDesc = "<b>" + agaDesc + "</b>";
          compSymbol = "<";
          compScore = "-1";
        } else if (compRes[p1][p2][sI] == 0) {
          compSymbol = "=";
          compScore = "0";
        }

        rowEl.append("<td>" + forDesc + "</td>");
        rowEl.append("<td>" + compSymbol + "</td>");
        rowEl.append("<td>" + agaDesc + "</td>");
        rowEl.append("<td>" + compScore + "</td>");

        tableEl.append(rowEl);
      }
      hoverEl.append(tableEl);

      if (gameScores[p1][p2] == 6) {
        hoverEl.append( "<br><b>+3 points for winning all sets</b>");
      } else if (gameScores[p1][p2] == -6) {
        hoverEl.append( "<br><b>-3 points for losing all sets</b>");
      }

      $(cellSelector).append(hoverEl);
    }
    
    cellSelector = ".score-row:eq(" + 
        (p1).toString() + 
        ") > .cell-score-tot:eq(0)";
    $(cellSelector).html(gameScoreHistory[p1].slice(-1)[0]); // Last element of array
    
    
    cellSelector = ".score-row:eq(" + 
        (p1).toString() + 
        ") > .cell-score-tot:eq(1)";
    $(cellSelector).html(cumGameScores[p1]).toString();
  }
}


// Set up sortable  IIFC
$( function() {
  $( "#card-pool, #set1, #set2, #set3").sortable({
    connectWith: ".connected",
    tolerance: "pointer",
    helper: "clone",
    start: function(evt, ui) {
      $(this).attr('orig-div-id', ui.item.closest('div').parent().attr('id'));
    },
    stop: function(evt, ui) {
      //var source = ui.item.html();
      const targetId = ui.item.closest('div').parent().attr('id');
      const targetIdNum = targetId[targetId.length-1];
      const targetResultLength = $('#' + targetId + ' div').length;

      const sourceId = $(this).attr('orig-div-id')
      const sourceIdNum = sourceId[sourceId.length-1];

      var html_content;
      console.log('sourceId:' + sourceId)

      var targetSetLength;
      var sourceSetLength;
      var targetInd;
      var sourceInd;
      var card_ids;

      if (targetId == sourceId) {
        return true;
      }

      // If card moved to pool then can't submit for sure
      if (targetId == 'card-pool') {
        setCodes[parseInt(sourceIdNum)-1] = '()';
        $( "#button-submit" ).attr("disabled", true);
        //return true;
      }
      //console.log('setLength:' + setLength.toString())

      // If card moved to a set
      if (['1','2','3'].includes(targetIdNum)) {
        targetInd = parseInt(targetIdNum)-1;
        targetCurLength = n_cards_in_set[targetInd];
        targetSetLength = setLengths[targetInd];
        if (targetCurLength == targetSetLength) {
          return false;
        } else if (targetCurLength+1 == targetSetLength) {
          card_ids = $("#" + targetId).sortable("toArray");
          $.ajax({
            type: 'POST',
            contentType: 'application/json',
            url: '/post/update_set_descriptions',
            dataType: 'json',
            data : JSON.stringify({
              'cardIds':card_ids,
              'set1Code': setCodes[0],
              'set2Code': setCodes[1],
              'set3Code': setCodes[2],
              'targetSet': targetInd+1,
            }),
          }).done(function(response) {
            //alert(response['Description']);
            allSplitDesc[0][targetInd] = response['Description'];
            html_content = 'Set ' + targetIdNum + 
              ' (' + targetSetLength.toString() + ' cards)' + 
              '<br>' + response['Description'];
            $('#USER > .header' + targetIdNum).html(html_content);
            setCodes[targetInd] = response['SetCode'];
            //console.log("respone['SetCode']:" + response['SetCode']);
            //console.log('setCodes:' + setCodes.toString());
            //alert(html_content)
            console.log(response)
            if (response['ValidSplit'] == 1) {
              $( "#button-submit" ).attr("disabled", false);
            }
          }).fail(function() {
            alert('Error: Could not contact server');
          })
        }
        n_cards_in_set[targetInd]++;
        $( "#button-reset" ).attr("disabled", false);
      }

      // If card moved from a set
      if (['1','2','3'].includes(sourceIdNum)) {
        sourceInd = parseInt(sourceIdNum)-1;
        sourceCurLength = n_cards_in_set[sourceInd];
        sourceSetLength = setLengths[sourceInd];
        if (sourceCurLength == sourceSetLength) {
          html_content = 'Set ' + sourceIdNum + ' (' + sourceSetLength.toString() + ' cards)';
          $('#USER > .header' + sourceIdNum).html(html_content);
        }
        n_cards_in_set[sourceInd]--;
        if (sumArray(n_cards_in_set) == 0) {
          $( "#button-reset" ).attr("disabled", true);
        }
        setCodes[sourceInd] = '()';
      }
    }
  }).disableSelection();
});


/* START draggable element START */
function dragStart(event) {
  var style = window.getComputedStyle(event.target, null);
  event.dataTransfer.setData("text/plain",
    (parseInt(style.getPropertyValue("left"),10) - event.clientX) + ',' + (parseInt(style.getPropertyValue("top"),10) - event.clientY));
}

function dragOver(event){
  event.preventDefault();
  return false;
}

function dropElement(event) {
  var offset = event.dataTransfer.getData("text/plain").split(',');
    var dm = document.getElementById('hand-ranks-hover');
    dm.style.left = (event.clientX + parseInt(offset[0],10)) + 'px';
    dm.style.top = (event.clientY + parseInt(offset[1],10)) + 'px';
    event.preventDefault();
    return false;
} 



function showHandRankToggle() {
  if ($( "#hand-ranks-hover" ).css('display') == 'none') {
    $( "#hand-ranks-hover" ).show();
    $('#hand-rank-toggle').html('Hide hand ranks');
    document.getElementById('hand-ranks-hover').style.top = "10%";
    document.getElementById('hand-ranks-hover').style.left = "10%";
  } else {
    $( "#hand-ranks-hover" ).hide();
    $('#hand-rank-toggle').html('Show hand ranks');
  }
}


/* END draggable element END */

var eventObj;
/* Submit score */
function submitScore(event) {
  // 
  event.preventDefault();
  eventObj = event;
  console.log('Name:' + document.getElementById("submit-score-input-name").value)
  console.log('Email:' + document.getElementById("submit-score-input-email").value)
  // submit gameScoreHistory[0]
  let name = document.getElementById("submit-score-input-name").value
  let email = document.getElementById("submit-score-input-email").value
  //alert('Submitting score');
  // TODO: add form checking - name must be filled
  
  function submitScorePromise() {
    return new Promise((resolve, reject) => {
      $.ajax({
        type: 'POST',
        contentType: 'application/json',
        url: '/post/submit_score',
        dataType: 'json',
        data: JSON.stringify({
          'Name': name,
          'Email': email,
          'AppGameID': appGameID,
        }),
        success: function(data) {
          console.log('Submitted Score!');
          resolve(data);
        },
        error: function(error) {
          reject(error);
        },
      })
    })
  }
  
  
  submitScorePromise()
    .then(function() {
      return new Promise((resolve, reject) => {
        showLeaderboard(appGameID,20);
        resolve();
      })
    })
    .then(function(output) {
      $( "#end-game-score-submit" ).hide();
    })
}

function showLeaderboard(appGameID, showTop=10) {
  showLeaderboardPromise(appGameID, showTop)
    .then(function(output) {
      genLeaderboard(output['Leaders'])
    })
    .then($( "#high-score-table-section" ).show())
  
}

function showLeaderboardPromise(appGameID, showTop) {
  return new Promise((resolve, reject) => {
    $.ajax({
      type: 'POST',
      contentType: 'application/json',
      url: '/post/get_leaderboard',
      dataType: 'json',
      data: JSON.stringify({
        'AppGameID': appGameID,
        'ShowTop': showTop
      }),
      success: function(data) {
        //console.log('Submitted Score!');
        resolve(data);
      },
      error: function(error) {
        reject(error);
      },
    })
  })
}

/* */
var globLeaderInfo;
function genLeaderboard(leaderInfo) {
  globLeaderInfo = leaderInfo;

  // Rank, Name, CPT Score, Tot COM Ability, NoRounds, Date
  tableEl = $("<table></table>");

  let titleRow = $("<tr></tr>");
  titleRow.addClass("high-score-table-title")
  let tempEntryRow;
  let tempCptScore;
  let tempRank;
  titleRow.append("<td>Rank</td><td>Name</td><td>CPT Score</td><td>COM Ability</td><td>Rounds</td><td>Date</td>");
  tableEl.append(titleRow);
  for (let rI=0; rI<leaderInfo.length; rI++) {
    tempEntryRow = $("<tr></tr>");
    
    if (leaderInfo[rI][0] == null) { 
      tempEntryRow.append("<td></td><td></td><td></td><td></td><td></td><td></td>");
      tableEl.append(tempEntryRow);
      
      tempRank = '-';
      tempEntryRow = $("<tr></tr>");
    } else {
      tempRank = leaderInfo[rI][0]
    }

    if (leaderInfo[rI][7] == 1) {
      tempEntryRow.addClass("player-score-entry");
    }

    tempCptScore = roundDecimal((leaderInfo[rI][4]-leaderInfo[rI][5])/leaderInfo[rI][3],2);
    tempEntryRow.append(`<td>${tempRank}</td><td>${leaderInfo[rI][1]}</td><td>${tempCptScore}</td><td>${leaderInfo[rI][2]}</td><td>${leaderInfo[rI][3]}</td><td>${leaderInfo[rI][6]}</td>`);
    tableEl.append(tempEntryRow);
  }
  console.log(tableEl);
  $( "#high-score-table-section" ).html("<h2>High Scores:</h2>");
  $( "#high-score-table-section" ).append(tableEl);
}
// Get client IP
// https://ipdata.co/blog/how-to-get-the-ip-address-in-javascript/
function getClientIp() {
  let ipRequest = new Request(`https://www.cloudflare.com/cdn-cgi/trace`);
  return fetch(ipRequest)
    .then(function(response) {
      return response.text()
    })
    .then(function(text) {
      const ipRegex = /[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/;
      clientIp = text.match(ipRegex)[0];
    });
}
/*
Old Sortable Code
$( function() {
    $( "#sortable-grid" ).sortable(
      {
        items: ':not(.static)',
        start: function(){
          $('.static', this).each(function(){
              var $this = $(this);
              $this.data('pos', $this.index());
          });
        },
        change: function(){
          $sortable = $(this);
          $statics = $('.static', this).detach();
          $helper = $('<div></div>').prependTo(this);
          $statics.each(function(){
              var $this = $(this);
              var target = $this.data('pos');

              $this.insertAfter($('div', $sortable).eq(target));
          });
          $helper.remove();
        }
      }
    );
    $( "#sortable-grid" ).disableSelection();
  } 
);

$( function() {
  $( "#swapable-grid" ).sortable(
    {
      items: ':not(.static)',
      start: function(){
        $('.static', this).each(function(){
            var $this = $(this);
            $this.data('pos', $this.index());
        });
      },
      change: function(){
        $sortable = $(this);
        $statics = $('.static', this).detach();
        $helper = $('<div></div>').prependTo(this);
        $statics.each(function(){
            var $this = $(this);
            var target = $this.data('pos');

            $this.insertAfter($('div', $sortable).eq(target));
        });
        $helper.remove();
      }
    }
  );
  $( "#swapable-grid" ).disableSelection();
} 
);
*/
