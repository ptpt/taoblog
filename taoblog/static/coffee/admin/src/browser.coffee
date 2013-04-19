define (require, exports, module) ->
    $ = require '$'

    class Browser
        constructor: (selector) ->
            browser = this
            @selectedClass = 'selected'
            @tbody = $(selector).children 'TBODY'
            @items = @tbody.children 'TR.item'
            @lastSelectedRow = 0
            @selector = selector
            @events = []
            @bind 'click', (event, row) ->
                if event.shiftKey
                    browser.select r for r in [row .. browser.lastSelectedRow]
                else if event.ctrlKey
                    browser.toggleSelection row
                else
                    browser.clearSelections()
                    browser.select row
                browser.lastSelectedRow = row

        select: (row) ->
            if not @isSelected row
                @items.eq(row).addClass @selectedClass

        unselect: (row) ->
            if @isSelected row
                @items.eq(row).removeClass @selectedClass

        clearSelections: ->
            @unselect i for i in [0 .. this.items.length]

        isSelected: (row) ->
            @items.eq(row).hasClass @selectedClass

        toggleSelection: (row) ->
            if @isSelected row
                @unselect row
            else
                @select row

        getSelections: ->
            @items.filter '.' + @selectedClass

        selectAll: ->
            @items.addClass selectedClass

        bind: (type, handler) ->
            @events.push {type: type, handler: handler}
            @items.each (row) ->
                $(this).bind type, (event) ->
                    handler.apply this, [event, row]

        rebind: ->
            events = @events
            @events = []
            @bind event.type, event.handler for event in events

        reload: ->
            @items = @tbody.children 'TR.item'
            @lastSelectedRow = 0
            @items.unbind()
            @rebind()
