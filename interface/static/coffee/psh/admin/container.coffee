$ ->
  id = $("#container-id").val()

  $("#disable").click ->
    yn = confirm "Are you sure you want to disable this container?"
    if yn
      toggle()

  $("#enable").click ->
    toggle()

  toggle = () ->
    $.post "/admin/containers/#{ id }/disable"
    window.location.reload()
