deps = ['jquery',
        'moment',
        'admin/browser',
        'admin/toolbar',
        'admin/dom',
        'admin/utils']

requirejs deps, ($, moment, Browser, Toolbar, dom, Utils) ->
    # constants
    PUBLIC = 0
    PRIVATE = 1
    TRASH = 2

    PRIVATE_IMG_SRC = '/static/img/eye-blocked.png'
    DRAFT_IMG_SRC = '/static/img/pencil3.png'


    # browser for posts
    # 3 columns: title, tags, and date
    class PostBrowser extends Browser
        # show human-readable at the date column
        showDate: ->
            now = new Date()
            $(@items).find('TD.date > time').each ->
                date = moment($(@).attr('datetime'), 'YYYY-MM-DD HH:mm:ssZ')
                $(@).text date.fromNow()

        # generate a new item dom tree from a post
        makePostItem: (post) ->
            draftIcon = if post.draft
                ['img', {class: 'draft', src: DRAFT_IMG_SRC}]
            else
                null
            statusIcon = if post.status is PRIVATE
                ['img', {class: 'private', src: PRIVATE_IMG_SRC}]
            else
                null
            return dom ['tr', {class: "item", 'data-id': post.id, 'data-status': post.status}
                ['td', {class: 'title'}, Utils.truncate(post.title, 64), draftIcon, statusIcon]
                ['td', {class: 'tags'},  post.tags.join(',')]
                ['td', {class: 'date'},  ['time', {datetime: post.created_at + 'Z'},
                    moment(post.created_at, 'YYYY-MM-DD HH:mm:ssZ').fromNow()]]]

        # set browser's posts
        setPosts: (posts) ->
            @tbody.empty()
            @tbody.append(@makePostItem(post)) for post in posts
            @reload()

        # append posts to this browser
        appendPosts: (posts) ->
            @tbody.append(@makePostItem post) for post in posts
            @reload()

        # remove post selections (not removing selected posts!)
        removeSelections: (callback) ->
            removedCount = 0
            length = @getSelections().length
            browser = @
            @getSelections().fadeOut 'fast', ->
                $(@).remove()
                removedCount++
                if removedCount >= length
                    browser.reload()
                    callback?()

        # remove all post selections
        removeAll: (callback) ->
            removedCount = 0
            length = @items.length
            browser = @
            @items.fadeOut 'fast', ->
                $(@).remove()
                removedCount++
                if removedCount >= length
                    browser.reload()
                    callback?()

        # change the selected posts's status to another by changing the status data attribute
        markSelectedPostsAs: (status) ->
            postItems = @getSelections()
            if status == 'private'
                postItems.data('status', PRIVATE)
            else if status == 'public'
                postItems.data('status', PUBLIC)
            else if status == 'trash'
                postItems.data('status', TRASH)

            for item in postItems
                img = $(item).find('TD.title > IMG.private')
                if status == 'private'
                    if img.length == 0
                        $(item).children('TD.title').append dom(['img', {class: 'private', src: PRIVATE_IMG_SRC}])
                else if status == 'public'
                    if img.length > 0
                        img.remove()

        # count the number of selections for each status
        countSelectionsByStatus: ->
            publicItems = []
            privateItems = []
            trashItems = []
            for item in @getSelections()
                if $(item).data('status') is PUBLIC
                    publicItems.push(item)
                else if $(item).data('status') is PRIVATE
                    privateItems.push(item)
                else if $(item).data('status') is TRASH
                    trashItems.push(item)
            return [publicItems, privateItems, trashItems]

    parseWindowQueryString = () ->
        queryString = window.location.search.substring(1)
        params = {}
        for param in queryString.split('&')
            kv = param.split('=')
            key = kv[0]
            val = if kv.length > 1 then kv[1] else null
            params[key] = val
        return params

    makeQueryString = (params) ->
        s = ''
        for key, val of params
            s = if s then s + '&' else '?'
            s += key
            if val?
                s += '='
                s += encodeURIComponent(val)
        return s

    # this function will be exported
    setupPosts = ->
        toolbar          = new Toolbar '#toolbar'
        browser          = new PostBrowser 'TABLE.browser'

        # get api path to get new posts
        # arguments will be used to generate query string
        getApiPath = (offset, limit, currentStatus) ->
            unless currentStatus?
                currentStatus = $(browser.selector).data('status')
            params = parseWindowQueryString()
            if offset?
                params['offset'] = offset
            if limit?
                params['limit'] = limit
            if currentStatus?
                params['status'] = currentStatus
            params['meta'] = true
            return "/api/posts/#{ makeQueryString(params) }"

        # delete all trashed posts from the server
        clearTrash = ->
            $.ajax(
                url: '/api/posts/?status=trash'
                type: 'DELETE'
                success: (data) ->
                    browser.removeAll ->
                        Utils.flash "#{ data.response.total_posts } #{ if data.response.total_posts==1 then 'post' else 'posts' } got deleted"
                error: ->
                    showToolbar()
                    Utils.flash 'failed to clear trash', 'error'
            )

        # a browser shows a number of posts
        # if some posts are removed from the browser,
        # this function will fetch some of other posts to complement the browser
        complementBrowser = (currentStatus) ->
            limit  = browser.getSelections().length
            offset = browser.items.length - limit
            $.get getApiPath(offset, limit, currentStatus), (data) ->
                browser.removeSelections ->
                    showToolbar()
                    browser.appendPosts data.response.posts
                    if not data.response.more
                        $('#more-posts').hide()
            .error (data, text) ->
                browser.clearSelections()
                showToolbar()
                Utils.flash 'failed to get new posts', 'error'

        # delete selected posts from the server
        deleteSelectedPosts = (currentStatus) ->
            selections = browser.getSelections()
            $.ajax(
                url: '/api/posts/?bulk=' + encodeURIComponent(($(item).data('id') for item in browser.getSelections()).join(','))
                type: 'DELETE'
                success: (data) ->
                    Utils.flash "#{ selections.length } #{ if selections.length==1 then 'post' else 'posts' } has been deleted"
                    complementBrowser(currentStatus)
                error: ->
                    browser.clearSelections()
                    showToolbar()
                    Utils.flash 'failed to delete selected posts', 'error'
            )

        # mark selected posts as another status
        markSelectedPostsAs = (currentStatus, status) ->
            selections = browser.getSelections()
            if not selections.length
                return
            if status =='public'
                action = 'publish'
                passiveAction = 'published'
            else if status == 'private'
                action = 'hide'
                passiveAction = 'hidden'
            else if status == 'trash'
                action = 'trash'
                passiveAction = 'trashed'

            $.post "/api/posts/#{ action }",
                # post IDs
                {id: ($(item).data('id') for item in selections).join(',')}
                # success
                ->
                    if currentStatus == 'trash' or status == 'trash'
                        Utils.flash "#{ selections.length } #{ if selections.length==1 then 'post' else 'posts' } has been #{ passiveAction }"
                        complementBrowser currentStatus
                    else
                        Utils.flash "#{ selections.length } #{ if selections.length==1 then 'post' else 'posts' } has been #{ passiveAction }"
                        browser.markSelectedPostsAs status
                        showToolbar()
            .error (data) ->
                browser.clearSelections()
                Utils.flash 'failed to #{ action } selected posts', 'error'

        browser.bind 'click', ->
            showToolbar()

        # double click to open that post
        browser.bind 'dblclick', ->
            window.location = "/post/#{ $(@).data 'id' }/edit"

        showToolbar = ->
            currentStatus = $(browser.selector).data('status')

            toolbar.hideAllMenus()

            toolbar.showMenu 'new-post'

            [publicCount, privateCount, trashCount] = (item.length for item in browser.countSelectionsByStatus())

            if publicCount + privateCount == 1
                toolbar.showMenu 'edit'
            else
                toolbar.hideMenu 'edit'

            if publicCount > 0 or privateCount > 0
                toolbar.showMenu 'trash'
            else
                toolbar.hideMenu 'trash'

            if publicCount > 0 or trashCount > 0
                toolbar.showMenu 'hide'
            else
                toolbar.hideMenu 'hide'

            if privateCount > 0 or trashCount > 0
                toolbar.showMenu 'publish'
            else
                toolbar.hideMenu 'publish'

            if trashCount > 0
                toolbar.showMenu 'delete'
                toolbar.hideMenu 'delete-all'
            else
                toolbar.hideMenu 'delete'
                if currentStatus == 'trash'
                    toolbar.showMenu 'delete-all'

        # click elsewhere to clear selections, and reset toolbar
        $('html').click (e) ->
            if browser.items.find(e.target).length == 0 and
                    $(toolbar.selector).find(e.target).length == 0
                browser.clearSelections()
                showToolbar()

        # click more to download more posts
        $('#more-posts').click (event) ->
            event.preventDefault()
            offset = browser.items.length
            path = getApiPath offset
            $.get path, (data) ->
                browser.appendPosts data.response.posts
                if not data.response.more
                    $('#more-posts').hide()
            .error ->
                Utils.flash 'failed to get new posts', 'error'

        do ->
            currentStatus = $(browser.selector).data('status')

            # add new post button
            toolbar.addMenu 'new-post', ['li', ['a', {href: '/admin/compose'}, 'New Post']]

            # add edit button
            li = toolbar.addMenu 'edit', ['li', ['a', {href: "#"}, 'Edit']]
            toolbar.hideMenu 'edit'
            $('a', li).click (event) ->
                event.preventDefault()
                id = $(browser.getSelections()).data('id')
                window.location = "/post/#{ id }/edit"

            # add delete-all button
            li = toolbar.addMenu 'delete-all', ['li', ['a', {href: '#'}, 'Delete All']]
            toolbar.hideMenu 'delete-all'
            $('a', li).click (event) ->
                event.preventDefault()
                clearTrash()

            # add delete button
            li = toolbar.addMenu 'delete', ['li', ['a', {href: '#'}, 'Delete']]
            toolbar.hideMenu 'delete'
            $('a', li).click (event) ->
                event.preventDefault()
                deleteSelectedPosts(currentStatus)

            # add trash button
            li = toolbar.addMenu 'trash', ['li', ['a', {href: '#', 'data-action': '/api/posts/trash'}, 'Trash']]
            toolbar.hideMenu 'trash'
            $('a', li).click (event) ->
                event.preventDefault()
                markSelectedPostsAs currentStatus, 'trash'

            # add hide button
            li = toolbar.addMenu 'hide', ['li', ['a', {href: '#', 'data-action': '/api/posts/hide'}, 'Hide']]
            toolbar.hideMenu 'hide'
            $('a', li).click (event) ->
                event.preventDefault()
                markSelectedPostsAs currentStatus, 'private'

            # add publish button
            li = toolbar.addMenu 'publish', ['li', ['a', {href: '#', 'data-action': '/api/posts/publish'}, 'Publish']]
            toolbar.hideMenu 'publish'
            $('a', li).click (event) ->
                event.preventDefault()
                markSelectedPostsAs(currentStatus, 'public')

            # show date
            showToolbar()
            browser.showDate()
    setupPosts()
