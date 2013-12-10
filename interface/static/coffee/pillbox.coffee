$ = jQuery

$.fn.extend
  pillbox: (options) ->
    self = $.fn.pillbox
    opts = $.extend {}, self.default_options, options
    $(this).each (i, el) ->
      self.init el, opts

$.extend $.fn.pillbox,
  default_options:
    placeholder: ''

  init: (_el, opts) ->
    self = this
    self._tags = {}

    el = $ _el
    self._init_val = el.val()
    el.hide()

    el.after """<div class="pillbox"><input type="text" placeholder="#{ opts.placeholder }"/></div>"""

    el = $ el.next ".pillbox"
    self._el = el

    self.build()

  build: () ->
    self = this
    re_label = () ->
      text = ""
      tags = []
      self._el.find("span.label").remove()
      for tag, status of self._tags
        if status and tag
          self._el.prepend """ <span class="label label-theme">#{ tag } <i data-role="remove" class="icon-remove"></i></span> """
          tags.push tag

      val_string = tags.join ","
      self._el.prev().val val_string

    input_keypress = (e) ->
      switch e.keyCode
        when 13
          e.preventDefault()
          tag = self._el.find('input').last().val().trim()
          self._tags[tag] = true
          self._el.find("input").val ""
          self.refresh()

        when 8, 46
          input = self._el.find("input").last()
          if self.getCaretPosition(input[0]) is 0
            e.preventDefault()
            last = self._el.find("span.label").last()
            if last?
              key = last.text().trim()
              self._tags[key]= false
              self.refresh()

    remove_this = () ->
      key = $(this).parent().text().trim()
      self._tags[key]= false
      $(this).parent().remove()

    for tag in self._init_val.split(",")
      self._tags[tag.trim()] = true
      self.refresh()

    self._el.on "keydown", input_keypress
    self._el.on "click", 'i[data-role="remove"]', remove_this

    self._el.click () ->
      self._el.find("input").last().focus()

  refresh: () ->
    self = this
    text = ""
    tags = []
    self._el.find("span.label").remove()
    for tag, status of self._tags
      if status and tag
        self._el.prepend """ <span class="label label-theme">#{ tag } <i data-role="remove" class="icon-remove"></i></span> """
        tags.push tag

    val_string = tags.join ","
    self._el.prev().val val_string

  remove: (item) ->
    self = this
    if item of self._tags
      self._tags[item] = false
      self.refresh()

  add: (item) ->
    self = this
    self._tags[item] = true
    self.refresh()

  empty: () ->
    this._tags = {}
    this.refresh()

  getCaretPosition: (oField) ->
    iCaretPos = 0
    if document.selection
      oField.focus()
      oSel = document.selection.createRange()
      oSel.moveStart 'character', -oField.value.length
      iCaretPos = oSel.text.length
    else if oField.selectionStart or oField.selectionStart is '0'
      iCaretPos = oField.selectionStart
    iCaretPos
