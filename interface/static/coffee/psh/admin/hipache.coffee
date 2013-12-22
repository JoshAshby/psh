$ ->
  $("#add_route").click (e) ->
    e.preventDefault()
    $("#routes").append """
      <div class="input-group">
        <input type="text" class="form-control" name="domains" Placeholder="Domain..." />
        <span class="input-group-btn">
          <button class="btn btn-default remove_route"><i class="fa fa-times"></i></button>
        </span>
      </div>
      <br>
      """

  $("#routes").on "click", ".remove_route", (e) ->
    e.preventDefault()
    $(this).parents("div.input-group").next().remove()
    $(this).parents("div.input-group").remove()

  $("#remove").click ->
    id = $(this).data "id"
    yn = confirm "Are you sure you want to delete this route?"

    if yn
      $.post "/admin/hipache/#{ id }/delete", (data) ->
        if data[0]["status"] == "success"
          window.location = "/admin/hipache"
