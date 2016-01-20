$(document).ready(function(){

  $("#PlayAgain").click(function(){
    $("#gamePage").fadeOut();
    window.setTimeout(function() {
      $("#dificultyPage").fadeIn();
    }, 500);
  });

  $('#choices input:radio').addClass('input_hidden');
  $('#choices label').click(function() {
      $(this).children("img").addClass('yellow');
      $(this).siblings().children().removeClass('yellow');
  });
});

function goToGame() {
  $("#dificultyPage").fadeOut();
  window.setTimeout(function() {
    $("#gamePage").fadeIn();
  }, 500);
}
