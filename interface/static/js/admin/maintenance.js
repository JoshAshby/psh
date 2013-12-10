$(function() {
  function toggle(what) {
    id=$(what).data("id");

    $.post("/admin/maintenance/toggle/"+id, function(data) {
      if(data[0]["data"]["success"]) {
        window.location.href = "/admin/maintenance";
      }
    });
  };

  $(".toggle_btn").click(function(){
    if($(this).hasClass("btn-theme")) {
      toggle(this);
    } else {
      var yesno = confirm("Are you sure you want to restore this message?");

      if(yesno) {
        toggle(this);
      };
    }
  });
});
