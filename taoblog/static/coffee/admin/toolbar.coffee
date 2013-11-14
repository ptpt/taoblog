define ['jquery', 'admin/dom'], ($, makeDom) ->
    class Toolbar
        constructor: (selector) ->
            @selector = selector
            @menus = {}
            
        addMenu: (id, menu) =>
            if id not of @menus
                dom = makeDom menu
                @menus[id] = dom
                $(@selector).append dom
            else
                dom = @menus[id]
            return dom

        # remove everything
        removeAll: -> $(@selector).remove()

        # remove a single menu
        removeMenu: (id) ->
            $(@menus[id]).remove()
            delete @menus[id]

        hideMenu: (id) ->
            $(@menus[id]).hide()

        showMenu: (id) ->
            $(@menus[id]).show()

        hideAllMenus: ->
            $(menu).hide() for id, menu of @menus

        showAllMenus: ->
            $(menu).show() for id, menu of @menus

        # empty all menu items
        empty: ->
            $(@selector).empty()
            @menus = {}