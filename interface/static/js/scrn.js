$(function() {
  $(".del_btn").click(function(){
    var yesno = confirm("Are you sure you want to delete this screenshot?");

    if(yesno) {
      img=$(this).data("img");

      $.post("/screenshots/delete/"+img, function(data) {
        if(data[0]["data"]["success"]) {
          window.location.href="/screenshots";
        }
      });
    };
  });
});
