$ ->
  $("#restart").click ->
    $(this).preventDefault()
    id = $(this).parents("form").data "id"
    $(this).parents("form").attr "action", "/containers/#{ id }/restart"
    $(this).parents("form").submit()

  $("#stop").click ->
    $(this).preventDefault()
    id = $(this).parents("form").data "id"
    $(this).parents("form").attr "action", "/containers/#{ id }/stop"
    $(this).parents("form").submit()

