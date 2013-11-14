deps = ['jquery', 'admin/toolbar']

requirejs deps, ($, Toolbar) ->
    setupCompose = ->
        title = $('div.post-editor input[name="title"]')
        text = $('div.post-editor textarea[name="text"]')

        editor = ace.edit('editor')
        editor.renderer.setShowGutter(false)
        editor.setTheme("ace/theme/tomorrow")
        editor.getSession().setMode("ace/mode/markdown")
        editor.setValue(text.val())

        $('#save-draft').click (event) ->
            event.preventDefault()
            editorText = editor.getValue()
            if not title.val() and not editorText
                normalColor = title.css('border-color')
                title.select()
                title.css('border-color': 'red')
                title.one 'keydown', ->
                    title.css('border-color', normalColor)
            else
                text.text(editorText)
                $('#compose-form').attr({action: $(this).data('action'), method: 'POST'})
                $('#compose-form').submit()

        $('#new-post').click (event) ->
            event.preventDefault()
            title = $('div.post-editor > input.title')
            titleVal = $.trim(title.val())
            editorText = editor.getValue()
            if titleVal
                text.text(editorText)
                $('#compose-form').attr({action: $(this).data('action'), method: 'POST'})
                $('#compose-form').submit()
            else
                normalColor = title.css('border-color')
                title.css('border-color', 'red')
                title.select()
                title.one 'keydown', ->
                    title.css {'border-color': normalColor}

    setupCompose()