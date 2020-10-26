function navIcon () {
  var x = document.getElementById("top-nav-bar");
  if (x.className === "top-nav") {
    x.className += " responsive";
  } else {
    x.className = "top-nav";
  }
}