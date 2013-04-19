// Generated by CoffeeScript 1.6.2
(function() {
    define("taoblog/admin/1.0.0/compose-debug", [ "$-debug", "./toolbar-debug", "./dom-debug", "ace-debug" ], function(require, exports, module) {
        var $, Toolbar, ace, setupCompose;
        $ = require("$-debug");
        Toolbar = require("./toolbar-debug");
        ace = require("ace-debug");
        return setupCompose = function() {
            var editor, text, title;
            title = $('div.post-editor input[name="title"]');
            text = $('div.post-editor textarea[name="text"]');
            editor = ace.edit("editor");
            editor.setTheme("ace/theme/solarized_light");
            editor.getSession().setMode("ace/mode/markdown");
            editor.setValue(text.val());
            $("#save-draft").click(function(event) {
                var editorText, normalColor;
                event.preventDefault();
                editorText = editor.getValue();
                if (!title.val() && !editorText) {
                    normalColor = title.css("border-color");
                    title.select();
                    title.css({
                        "border-color": "red"
                    });
                    return title.one("keydown", function() {
                        return title.css("border-color", normalColor);
                    });
                } else {
                    text.text(editorText);
                    $("#compose-form").attr({
                        action: $(this).data("action"),
                        method: "POST"
                    });
                    return $("#compose-form").submit();
                }
            });
            return $("#new-post").click(function(event) {
                var editorText, normalColor, titleVal;
                event.preventDefault();
                title = $("div.post-editor > input.title");
                titleVal = $.trim(title.val());
                editorText = editor.getValue();
                if (titleVal) {
                    text.text(editorText);
                    $("#compose-form").attr({
                        action: $(this).data("action"),
                        method: "POST"
                    });
                    return $("#compose-form").submit();
                } else {
                    normalColor = title.css("border-color");
                    title.css("border-color", "red");
                    title.select();
                    return title.one("keydown", function() {
                        return title.css({
                            "border-color": normalColor
                        });
                    });
                }
            });
        };
    });
}).call(this);

// Generated by CoffeeScript 1.6.2
(function() {
    var __bind = function(fn, me) {
        return function() {
            return fn.apply(me, arguments);
        };
    };
    define("taoblog/admin/1.0.0/toolbar-debug", [ "$-debug", "./dom-debug" ], function(require, exports, module) {
        var $, Toolbar, makeDom;
        $ = require("$-debug");
        makeDom = require("./dom-debug");
        return Toolbar = function() {
            function Toolbar(selector) {
                this.addMenu = __bind(this.addMenu, this);
                this.selector = selector;
                this.menus = {};
            }
            Toolbar.prototype.addMenu = function(id, menu) {
                var dom;
                if (!(id in this.menus)) {
                    dom = makeDom(menu);
                    this.menus[id] = dom;
                    $(this.selector).append(dom);
                } else {
                    dom = this.menus[id];
                }
                return dom;
            };
            Toolbar.prototype.removeAll = function() {
                return $(this.selector).remove();
            };
            Toolbar.prototype.removeMenu = function(id) {
                $(this.menus[id]).remove();
                return delete this.menus[id];
            };
            Toolbar.prototype.hideMenu = function(id) {
                return $(this.menus[id]).hide();
            };
            Toolbar.prototype.showMenu = function(id) {
                return $(this.menus[id]).show();
            };
            Toolbar.prototype.hideAllMenus = function() {
                var id, menu, _ref, _results;
                _ref = this.menus;
                _results = [];
                for (id in _ref) {
                    menu = _ref[id];
                    _results.push($(menu).hide());
                }
                return _results;
            };
            Toolbar.prototype.showAllMenus = function() {
                var id, menu, _ref, _results;
                _ref = this.menus;
                _results = [];
                for (id in _ref) {
                    menu = _ref[id];
                    _results.push($(menu).show());
                }
                return _results;
            };
            Toolbar.prototype.empty = function() {
                $(this.selector).empty();
                return this.menus = {};
            };
            return Toolbar;
        }();
    });
}).call(this);

// Generated by CoffeeScript 1.6.2
(function() {
    define("taoblog/admin/1.0.0/dom-debug", [], function(require, exports, module) {
        var makeDom;
        return makeDom = function(tree) {
            var child, element, key, node, value, _i, _len, _ref;
            if (tree.length === 0) {
                return null;
            }
            if (tree[0] instanceof HTMLElement) {
                element = tree[0];
            } else {
                element = document.createElement(tree[0]);
            }
            _ref = tree.slice(1);
            for (_i = 0, _len = _ref.length; _i < _len; _i++) {
                node = _ref[_i];
                if (toString.call(node) === "[object String]") {
                    element.appendChild(document.createTextNode(node));
                } else if (node instanceof Text) {
                    element.appendChild(node);
                } else if (Array.isArray(node)) {
                    child = makeDom(node);
                    if (child != null) {
                        element.appendChild(child);
                    }
                } else if (node instanceof Attr) {
                    element.setAttributeNode(node);
                } else if (node === Object(node)) {
                    for (key in node) {
                        value = node[key];
                        element.setAttribute(key, value);
                    }
                }
            }
            return element;
        };
    });
}).call(this);
