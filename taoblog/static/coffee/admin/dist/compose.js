(function(){define("taoblog/admin/1.0.0/compose",["$","./toolbar","./dom","ace"],function(e){var t,n,o,r;return t=e("$"),n=e("./toolbar"),o=e("ace"),r=function(){var e,n,r;return r=t('div.post-editor input[name="title"]'),n=t('div.post-editor textarea[name="text"]'),e=o.edit("editor"),e.setTheme("ace/theme/solarized_light"),e.getSession().setMode("ace/mode/markdown"),e.setValue(n.val()),t("#save-draft").click(function(o){var i,s;return o.preventDefault(),i=e.getValue(),r.val()||i?(n.text(i),t("#compose-form").attr({action:t(this).data("action"),method:"POST"}),t("#compose-form").submit()):(s=r.css("border-color"),r.select(),r.css({"border-color":"red"}),r.one("keydown",function(){return r.css("border-color",s)}))}),t("#new-post").click(function(o){var i,s,u;return o.preventDefault(),r=t("div.post-editor > input.title"),u=t.trim(r.val()),i=e.getValue(),u?(n.text(i),t("#compose-form").attr({action:t(this).data("action"),method:"POST"}),t("#compose-form").submit()):(s=r.css("border-color"),r.css("border-color","red"),r.select(),r.one("keydown",function(){return r.css({"border-color":s})}))})}})}).call(this),function(){var e=function(e,t){return function(){return e.apply(t,arguments)}};define("taoblog/admin/1.0.0/toolbar",["$","./dom"],function(t){var n,o,r;return n=t("$"),r=t("./dom"),o=function(){function t(t){this.addMenu=e(this.addMenu,this),this.selector=t,this.menus={}}return t.prototype.addMenu=function(e,t){var o;return e in this.menus?o=this.menus[e]:(o=r(t),this.menus[e]=o,n(this.selector).append(o)),o},t.prototype.removeAll=function(){return n(this.selector).remove()},t.prototype.removeMenu=function(e){return n(this.menus[e]).remove(),delete this.menus[e]},t.prototype.hideMenu=function(e){return n(this.menus[e]).hide()},t.prototype.showMenu=function(e){return n(this.menus[e]).show()},t.prototype.hideAllMenus=function(){var e,t,o,r;o=this.menus,r=[];for(e in o)t=o[e],r.push(n(t).hide());return r},t.prototype.showAllMenus=function(){var e,t,o,r;o=this.menus,r=[];for(e in o)t=o[e],r.push(n(t).show());return r},t.prototype.empty=function(){return n(this.selector).empty(),this.menus={}},t}()})}.call(this),function(){define("taoblog/admin/1.0.0/dom",[],function(){var e;return e=function(t){var n,o,r,i,s,u,c,a;if(0===t.length)return null;for(o=t[0]instanceof HTMLElement?t[0]:document.createElement(t[0]),a=t.slice(1),u=0,c=a.length;c>u;u++)if(i=a[u],"[object String]"===toString.call(i))o.appendChild(document.createTextNode(i));else if(i instanceof Text)o.appendChild(i);else if(Array.isArray(i))n=e(i),null!=n&&o.appendChild(n);else if(i instanceof Attr)o.setAttributeNode(i);else if(i===Object(i))for(r in i)s=i[r],o.setAttribute(r,s);return o}})}.call(this);
