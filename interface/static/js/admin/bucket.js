$(function() {
  function toggle(what) {
    id=$(what).data("id");

    $.post("/admin/buckets/toggle/"+id, function(data) {
      if(data[0]["data"]["success"]) {
        console.log("dim-wit twat");
        if($(what).hasClass("btn-default")) {
          $(what).removeClass("btn-default")
                 .addClass("btn-theme")
                 .html('<i class="icon-ok"></i>');
        } else {
          $(what).removeClass("btn-theme")
                 .addClass("btn-default")
                 .html('<i class="icon-remove"></i>');
        }
      }
    });
  };

  $(".toggle_btn").click(function(){
    if($(this).hasClass("btn-theme")) {
      toggle(this);
    } else {
      var yesno = confirm("Are you sure you want to activate this bucket?");

      if(yesno) {
        toggle(this);
      };
    }
  });
});
