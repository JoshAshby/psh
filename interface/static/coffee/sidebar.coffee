$ ->
  hide = (e) ->
    if e
      e.preventDefault()
    $("#sidebar-wrapper").hide().removeClass "col-sm-2"
    $("#main-wrapper").removeClass("col-sm-10 pull-right").addClass "col-sm-10 col-sm-offset-1"
    $("#show").parents(".row").show()
    sessionStorage.setItem "sidebar", "hide"

  show = (e) ->
    if e
      e.preventDefault()
    $("#show").parents(".row").hide()
    $("#main-wrapper").removeClass("col-sm-12").addClass "col-sm-10 pull-right"
    $("#sidebar-wrapper").show().addClass "col-sm-2"
    sessionStorage.setItem "sidebar", "show"

  wat = sessionStorage.getItem("sidebar")

  if wat isnt null and wat is "show"
    show()
  else
    hide()

  $("#hide").click (e) ->
    hide(e)

  $("#show").click (e) ->
    show(e)
