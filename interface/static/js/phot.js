$(function() {
  //$("#del_btn").click(function(){
    //var yesno = confirm("Are you sure you want to disable this image? It will no longer be visible in the index to anyone except for admins, however the source will not be removed.");

    //if(yesno) {
      //img=$(this).data("img");

      //$.post("/admin/phots/toggle/"+img, function(data) {
        //if(data[0]["data"]["success"]) {
          //window.location.href="/phots";
        //}
      //});
    //};
  //});

  $("#pillbox").pillbox();

  var tags = $.ajax({url: "/phots/json/tags", async: false});

  $('.pillbox input').typeahead({
    name: 'phots_tags',
    local: tags.responseJSON[0]["data"],
    limit: 10
  });
});
