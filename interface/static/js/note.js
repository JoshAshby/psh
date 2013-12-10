$(function() {
  $("#del_btn").click(function() {
    var yesno = confirm("Are you sure you want to delete this note?");

    if(yesno) {
      var img=$(this).data("short");

      $.post("/notes/edit/delete/"+img, function(data) {
        if(data[0]["data"]["success"]) {
          window.location.href="/notes";
        }
      });
    };
  });

  $("#save_btn").click(function() {
    $("#edit_form").submit();
  });

  $("a").click(function() {
    var wat = $(this).data("toggle");

    if(wat) {
      $(".inset").hide();
      $("#"+wat).show();
    };
  });

  $("#menu-toggle").click(function(e) {
    e.preventDefault();
    $("#wrapper").toggleClass("active");
  });

  $(".sidebar-nav").find('a[href="#"]').click(function(e) {
    e.preventDefault();
    $("#wrapper").toggleClass("active");
  });

  var editor = new EpicEditor({
    theme: {
      base: 'css/lib/epic/base/epiceditor.css',
      preview: 'css/lib/epic/preview/github.css',
      editor: 'css/lib/epic/editor/epic-dark.css'
    },
    basePath: '/static/',
    autogrow: true,
    textarea: "content"
  }).load();

  editor.on('update', function () {
    $("#preview").html(this.exportFile(null, 'html'));
  }).emit('update');

  //setup before functions
  var typingTimer;                //timer identifier
  var doneTypingInterval = 5000;  //time in ms, 5 second for example

  //on keyup, start the countdown
  $('#title').keyup(function(){
      typingTimer = setTimeout(doneTyping, doneTypingInterval);
  });

  //on keydown, clear the countdown 
  $('#title').keydown(function(){
      clearTimeout(typingTimer);
  });

  //user is "finished typing," do something
  function doneTyping () {
    $("#title_header").html($("#title").val());
  };

  $("#tags").pillbox();

  var tags = $.ajax({url: "/notes/json/tags", async: false});

  $('.pillbox input').typeahead({
    name: 'notes_tags',
    local: tags.responseJSON[0]["data"],
    limit: 10
  });
});
