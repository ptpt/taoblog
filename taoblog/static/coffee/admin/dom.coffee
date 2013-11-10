define (require, exports, module) ->
    makeDom = (tree) ->
        if tree.length == 0
            return null

        if tree[0] instanceof HTMLElement
            element = tree[0]
        else
            element = document.createElement(tree[0])

        for node in tree[1..]

            if toString.call(node) == '[object String]'
                element.appendChild document.createTextNode(node)

            else if node instanceof Text
                element.appendChild node

            else if Array.isArray(node)
                child = makeDom node
                element.appendChild child if child?

            else if node instanceof Attr
                element.setAttributeNode node

            else if node == Object(node)
                element.setAttribute key, value for key, value of node

        return element