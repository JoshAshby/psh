$(function() {
  function toggle(what) {
    id=$(what).data("id");

    $.post("/admin/buckets/"+id, function(data) {
      if(data[0]["success"]) {
        if($(what).hasClass("btn-default")) {
          $(what).removeClass("btn-default")
                 .addClass("btn-theme")
                 .html('<i class="fa fa-check"></i>');
        } else {
          $(what).removeClass("btn-theme")
                 .addClass("btn-default")
                 .html('<i class="fa fa-times"></i>');
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
