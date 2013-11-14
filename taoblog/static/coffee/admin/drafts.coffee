deps = ['jquery',
        'moment',
        'Uri',
        'admin/toolbar',
        'admin/browser',
        'admin/utils',
        'admin/dom']

requirejs deps, ($, moment, Uri, Toolbar, Browser, Utils, dom) ->
    # browser showing drafts
    class DraftBrowser extends Browser
        # show human-readable at the date column
        showDate: ->
            now = new Date()
            $(@items).find('TD.draft-date > time').each ->
                $(this).text moment($(this).attr('datetime'), 'YYYY-MM-DD HH:mm:ssZ').fromNow()

        # generate a new draft item dom tree from a draft
        makeDraftItem: (draft) ->
            dom ['tr', {class: 'item', 'data-id': draft.id}
                ['td', {class: 'draft-title'}, Utils.truncate(draft.title, 64)]
                ['td', {class: 'draft-text'},  Utils.truncate(draft.text, 64)]
                ['td', {class: 'draft-date'},  ['time', {datetime: draft.saved_at + 'Z'},
                    moment(draft.saved_at, 'YYYY-MM-DD HH:mm:ssZ').fromNow()]]]

        # set drafts for this browser
        setDrafts: (drafts) ->
            @tbody.empty()
            @tbody.append(@makeDraftItem(draft)) for draft in drafts
            @reload()

        # append drafts to this browser
        appenddrafts: (drafts) ->
            @tbody.append(@makeDraftItem draft) for draft in drafts
            @reload()

        # remove draft selections
        removeSelections: (callback) ->
            removedCount = 0
            length = @getSelections().length
            browser = this
            @getSelections().fadeOut 'fast', ->
                $(this).remove()
                removedCount++
                if removedCount >= length
                    browser.reload()
                    callback?()

    setupDrafts = ->
        browser = new DraftBrowser 'TABLE.browser'
        toolbar = new Toolbar '#toolbar'

        # double click to edit draft
        browser.bind 'dblclick', ->
            window.location = "/draft/#{ $(this).data 'id' }/edit"

        browser.bind 'click', ->
            showToolbar()

        showToolbar = ->
            toolbar.hideAllMenus()

            toolbar.showMenu 'new-post'

            if browser.getSelections().length > 0
                toolbar.showMenu 'delete-draft'
            else
                toolbar.hideMenu 'delete-draft'

        # click elsewhere to clear selections
        $('html').click (e) ->
            if browser.items.find(e.target).length == 0 and
                    $(toolbar.selector).find(e.target).length == 0
                browser.clearSelections()
                showToolbar()

        do (browser) ->
            toolbar.addMenu 'new-post', ['li', ['a', {href: '/admin/compose'}, 'New Post']]
            li = toolbar.addMenu 'delete-draft', ['li', ['a', {href: '#' }, 'Delete']]
            toolbar.hideMenu 'delete-draft'
            $('a', li).click (event) ->
                event.preventDefault()
                $.ajax(
                    url: '/api/drafts/?bulk=' + encodeURIComponent(($(item).data('id') for item in browser.getSelections()).join(','))
                    type: 'DELETE'
                    dataType: 'json'
                    success: (data) ->
                        count = browser.getSelections().length
                        browser.removeSelections ->
                            Utils.flash "#{ count } #{ if count==1 then 'draft' else 'drafts' } has been deleted"
                    error: ->
                        Utils.flash 'failed to delete selected drafts', 'error'
                )

            browser.showDate()

    setupDrafts()
