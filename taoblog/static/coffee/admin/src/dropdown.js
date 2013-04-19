define(function(require, exports, module) {
    var $ = require('$');

    function Dropdown(selector) {
        var dropdown = this;
        var trigger = $(selector);
        var menu = $($(selector).data('menu')).first();
        var isOpen = false;
        menu.css({'z-index': 1,
                  'position': 'absolute'});
        this.show = function () {
            menu.show();
            isOpen = true;
        };
        this.hide = function() {
            menu.hide();
            isOpen = false;
        };
        this.toggle = function() {
            if (isOpen) {
                this.hide();
            } else {
                this.show();
            }
        };
        trigger.click(function () {
            dropdown.toggle();
        });
    }

    module.exports = Dropdown;
});
