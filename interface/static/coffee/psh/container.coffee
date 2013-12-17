$ ->
  id = $("#container-id").val()

  $("#start").click ->
    $.post "/containers/#{ id }/start", (data) ->
      $("#start").button 'loading'
      worker()

  $("#restart").click ->
    $.post "/containers/#{ id }/restart", (data) ->
      $("#stop").button 'restarting'
      worker()

  $("#stop").click ->
    $.post "/containers/#{ id }/stop", (data) ->
      $("#stop").button 'stopping'
      worker()

  (worker = () ->
    $.post "/containers/#{ id }/status", (data) ->
      $("#status").html data[0]["status"]
      $("#start").button 'reset'
      $("#stop").button 'reset'

      if not data[0]["status"].search "Up"
        $("#start").hide()
        $("#stop").show()
        $("#restart").show()
      else
        $("#start").show()
        $("#stop").hide()
        $("#restart").hide()

    .done ->
        setTimeout worker, 30000
  )()
