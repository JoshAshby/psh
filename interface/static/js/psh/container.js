// Generated by CoffeeScript 1.5.0
(function() {

  $(function() {
    var id, worker;
    id = $("#container-id").val();
    $("#start").click(function() {
      return $.post("/containers/" + id + "/start", function(data) {
        $("#start").button('loading');
        return worker();
      });
    });
    $("#restart").click(function() {
      return $.post("/containers/" + id + "/restart", function(data) {
        $("#stop").button('restarting');
        return worker();
      });
    });
    $("#stop").click(function() {
      return $.post("/containers/" + id + "/stop", function(data) {
        $("#stop").button('stopping');
        return worker();
      });
    });
    return (worker = function() {
      return $.post("/containers/" + id + "/status", function(data) {
        $("#status").html(data[0]["status"]);
        $("#start").button('reset');
        $("#stop").button('reset');
        if (!data[0]["status"].search("Up")) {
          $("#start").hide();
          $("#stop").show();
          return $("#restart").show();
        } else {
          $("#start").show();
          $("#stop").hide();
          return $("#restart").hide();
        }
      }).done(function() {
        return setTimeout(worker, 30000);
      });
    })();
  });

}).call(this);
