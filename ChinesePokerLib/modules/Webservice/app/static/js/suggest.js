window.onload = initialise;

function initialise() {
  x = document.getElementById("top-nav-btn-split");
  x.classList.add("active");
}

function selectRandom() {
  var ids = $(".input-card-image").toArray();
  console.log(ids)
  console.log(ids.length);
  var inds = new Array(ids.length);
  console.log(inds);
  //console.log(ids)
  var n_cards = 13;
  random_inds = getRandomIndices(ids.length, n_cards);
  console.log(random_inds);

  for (var i=0; i<ids.length; i++) {
    if (random_inds.includes(i)) {
      ids[i].checked = true;
    } else {
      ids[i].checked = false;
    }
  }

}

function getRandomIndices(arr_len, n){
return getRandomNumbers(0, arr_len, n)
}

function getRandomNumbers(lower_bound, upper_bound, n) {
  var random_numbers = [];

  while (random_numbers.length < n) {
    var random_number = Math.floor(Math.random()*(upper_bound - lower_bound) + lower_bound);
    if (random_numbers.indexOf(random_number) == -1) { 
        // Yay! new random number
        random_numbers.push( random_number );
    }
  }
  return random_numbers
}
function getRandom(arr, n) {
  var result = new Array(n),
      len = arr.length,
      taken = new Array(len);
  if (n > len)
      throw new RangeError("getRandom: more elements taken than available");
  while (n--) {
      var x = Math.floor(Math.random() * len);
      result[n] = arr[x in taken ? taken[x] : x];
      taken[x] = --len in taken ? taken[len] : len;
  }
  return result;
}
