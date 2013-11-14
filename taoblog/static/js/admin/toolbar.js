// Generated by CoffeeScript 1.6.3
(function() {
  var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  define(['jquery', 'admin/dom'], function($, makeDom) {
    var Toolbar;
    return Toolbar = (function() {
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

    })();
  });

}).call(this);
