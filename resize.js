function resizeleft() {
var rh = document.getElementById('rightcontent').offsetHeight;
document.getElementById('leftcontent').style.height=rh 'px';
}

function showhideattrib() {
 var x = document.getElementById("attrib");
 if (x.style.display === "none") {
   x.style.display = "block";
 } else {
   x.style.display = "none";
 }
}
