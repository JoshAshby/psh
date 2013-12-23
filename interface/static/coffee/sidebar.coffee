$ ->
  $("#hide").click (e) ->
    e.preventDefault()
    $("#sidebar-wrapper").hide().removeClass "col-sm-2"
    $("#main-wrapper").removeClass("col-sm-10 pull-right").addClass "col-sm-12"
    $("#show").parents(".row").show()

  $("#show").click (e) ->
    e.preventDefault()
    $(this).parents(".row").hide()
    $("#main-wrapper").removeClass("col-sm-12").addClass "col-sm-10 pull-right"
    $("#sidebar-wrapper").show().addClass "col-sm-2"
