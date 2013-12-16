$ ->
  $("#start").click ->
    $.post

queue_action = (id, action) ->
  $.post "/containers/#{ id }/queue", {action: action}, (data) ->
    if data.success
      window.location.reload
