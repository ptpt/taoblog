// Generated by CoffeeScript 1.6.3
(function() {
  var deps,
    __hasProp = {}.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

  deps = ['jquery', 'moment', 'Uri', 'admin/toolbar', 'admin/browser', 'admin/utils', 'admin/dom'];

  requirejs(deps, function($, moment, Uri, Toolbar, Browser, Utils, dom) {
    var DraftBrowser, setupDrafts, _ref;
    DraftBrowser = (function(_super) {
      __extends(DraftBrowser, _super);

      function DraftBrowser() {
        _ref = DraftBrowser.__super__.constructor.apply(this, arguments);
        return _ref;
      }

      DraftBrowser.prototype.showDate = function() {
        var now;
        now = new Date();
        return $(this.items).find('TD.draft-date > time').each(function() {
          return $(this).text(moment($(this).attr('datetime'), 'YYYY-MM-DD HH:mm:ssZ').fromNow());
        });
      };

      DraftBrowser.prototype.makeDraftItem = function(draft) {
        return dom([
          'tr', {
            "class": 'item',
            'data-id': draft.id
          }, [
            'td', {
              "class": 'draft-title'
            }, Utils.truncate(draft.title, 64)
          ], [
            'td', {
              "class": 'draft-text'
            }, Utils.truncate(draft.text, 64)
          ], [
            'td', {
              "class": 'draft-date'
            }, [
              'time', {
                datetime: draft.saved_at + 'Z'
              }, moment(draft.saved_at, 'YYYY-MM-DD HH:mm:ssZ').fromNow()
            ]
          ]
        ]);
      };

      DraftBrowser.prototype.setDrafts = function(drafts) {
        var draft, _i, _len;
        this.tbody.empty();
        for (_i = 0, _len = drafts.length; _i < _len; _i++) {
          draft = drafts[_i];
          this.tbody.append(this.makeDraftItem(draft));
        }
        return this.reload();
      };

      DraftBrowser.prototype.appenddrafts = function(drafts) {
        var draft, _i, _len;
        for (_i = 0, _len = drafts.length; _i < _len; _i++) {
          draft = drafts[_i];
          this.tbody.append(this.makeDraftItem(draft));
        }
        return this.reload();
      };

      DraftBrowser.prototype.removeSelections = function(callback) {
        var browser, length, removedCount;
        removedCount = 0;
        length = this.getSelections().length;
        browser = this;
        return this.getSelections().fadeOut('fast', function() {
          $(this).remove();
          removedCount++;
          if (removedCount >= length) {
            browser.reload();
            return typeof callback === "function" ? callback() : void 0;
          }
        });
      };

      return DraftBrowser;

    })(Browser);
    setupDrafts = function() {
      var browser, showToolbar, toolbar;
      browser = new DraftBrowser('TABLE.browser');
      toolbar = new Toolbar('#toolbar');
      browser.bind('dblclick', function() {
        return window.location = "/draft/" + ($(this).data('id')) + "/edit";
      });
      browser.bind('click', function() {
        return showToolbar();
      });
      showToolbar = function() {
        toolbar.hideAllMenus();
        toolbar.showMenu('new-post');
        if (browser.getSelections().length > 0) {
          return toolbar.showMenu('delete-draft');
        } else {
          return toolbar.hideMenu('delete-draft');
        }
      };
      $('html').click(function(e) {
        if (browser.items.find(e.target).length === 0 && $(toolbar.selector).find(e.target).length === 0) {
          browser.clearSelections();
          return showToolbar();
        }
      });
      return (function(browser) {
        var li;
        toolbar.addMenu('new-post', [
          'li', [
            'a', {
              href: '/admin/compose'
            }, 'New Post'
          ]
        ]);
        li = toolbar.addMenu('delete-draft', [
          'li', [
            'a', {
              href: '#'
            }, 'Delete'
          ]
        ]);
        toolbar.hideMenu('delete-draft');
        $('a', li).click(function(event) {
          var item;
          event.preventDefault();
          return $.ajax({
            url: '/api/drafts/?bulk=' + encodeURIComponent(((function() {
              var _i, _len, _ref1, _results;
              _ref1 = browser.getSelections();
              _results = [];
              for (_i = 0, _len = _ref1.length; _i < _len; _i++) {
                item = _ref1[_i];
                _results.push($(item).data('id'));
              }
              return _results;
            })()).join(',')),
            type: 'DELETE',
            dataType: 'json',
            success: function(data) {
              var count;
              count = browser.getSelections().length;
              return browser.removeSelections(function() {
                return Utils.flash("" + count + " " + (count === 1 ? 'draft' : 'drafts') + " has been deleted");
              });
            },
            error: function() {
              return Utils.flash('failed to delete selected drafts', 'error');
            }
          });
        });
        return browser.showDate();
      })(browser);
    };
    return setupDrafts();
  });

}).call(this);