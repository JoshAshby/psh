$ ->
  default_button_classes = "btn"
  default_icon_classes = "fa"
  id = $("#container-id").val()

  worker_id = null

  states =
    running:
      text: "Shutdown"
      icon: "fa-power-off"
      color: "btn-danger"
      extra: ->
        $("#restart").show()
    stopped:
      text: "Start"
      icon: "fa-power-off"
      color: "btn-success"
      extra: ->
        $("#restart").hide()

  parse_state = (current) ->
    tmp = states[current]
    $("#wat_button").html("""<i class="#{ default_icon_classes } #{ tmp.icon }"></i> #{ tmp.text }""")
      .removeClass()
      .addClass """#{ default_button_classes } #{ tmp.color }"""
    tmp.extra()

  $("#wat_button").click ->
    if $(this).hasClass "btn-success"
      action = "start"
    else
      action = "stop"

    $.post "/containers/#{ id }/#{ action }", (data) ->
      $("#wat_button").button action
      clearTimeout worker_id
      worker_id = setTimeout worker, 1000

  $("#restart").click ->
    $.post "/containers/#{ id }/restart", (data) ->
      $("#wat_button").button "restart"
      clearTimeout worker_id
      worker_id = setTimeout worker, 1000

  $("#add_domain").click (e) ->
    e.preventDefault()
    $("#domain_inputs").append """
      <div class="input-group">
        <input type="text" class="form-control" name="domains" Placeholder="Domain..." />
        <span class="input-group-btn">
          <button class="btn btn-default remove_domain"><i class="fa fa-times"></i></button>
        </span>
      </div>
      <br>
      """

  $("#domain_inputs").on "click", ".remove_domain", (e) ->
    e.preventDefault()
    $(this).parents("div.input-group").next().remove()
    $(this).parents("div.input-group").remove()

  (worker = () ->
    clearTimeout worker_id
    $.post "/containers/#{ id }/status", (data) ->
      $("#status").html data[0]["status"]
      $("#wat_button").button 'reset'

      if data[0]["status"].search "Up"
        parse_state "stopped"
      else
        parse_state "running"

    .done ->
        worker_id = setTimeout worker, 30000

    .fail ->
       clearTimeout worker_id
  )()
