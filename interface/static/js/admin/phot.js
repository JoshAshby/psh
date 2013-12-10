$(function() {
  function toggle(what) {
    var id = $(what).data("id");
    var di = $("#"+id);

    $.post("/admin/phots/toggle/"+id, function(data) {
      if(data[0]["data"]["success"]) {
        di.fadeOut().find("button").popover('hide');
      };
    });
  };

  $(document).on("click", ".confirm_btn", function() {
    toggle(this);
  });

  $(document).on("click", ".nope_btn", function() {
    $(".toggle_btn").popover('hide');
  });

  $(".toggle_btn").click(function() {
    id = $(this);
    $(".toggle_btn").not(this).popover('hide');
    $(this).popover('show');
    $(".popover").find(".confirm_btn").data("id", $(this).data("id"));

    var timeout = setTimeout(function () {
      id.popover('hide');
    }, 3000);

    $(document).on("mouseenter", ".popover", function() {
      clearTimeout(timeout);
    }).on("mouseleave", ".popover", function() {
      timeout = setTimeout(function () {
        id.popover('hide');
      }, 3000);
    });

  }).popover({
    trigger: "manual",
    placement: "auto right",
    html: true,
    content: '<div class="btn-group"><button class="btn btn-success btn-sm confirm_btn"><i class="icon-ok"></i></button><button class="btn btn-default btn-sm nope_btn"><i class="icon-remove"></i></button></div>',
    container: "body"
  });
});
