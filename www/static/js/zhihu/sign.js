(function(a){with(a){
a.Dr=function(b){var c=ua(b);return function(){var d=this||fa,d=d.closure_memoize_cache_||(d.closure_memoize_cache_={}),e;e=arguments;for(var g=[c],h=e.length-1;0<=h;--h)g.push(typeof e[h],e[h]);e=g.join("\x0B");return d.hasOwnProperty(e)?d[e]:d[e]=b.apply(this,arguments)}},a.Er=function(){T.call(this)};y(Er,T);Er.prototype.z=function(){this.o(document.body)};
Er.prototype.B=function(b){function c(){q.hide();r.show()}function d(){$(this).trigger("requestStory")}function e(){var b=l.filter(".current");b.length&&h.css("top",b.position().top+b.height()/2-10)}Er.n.B.call(this,b);var g={member:Dr(function(b){return $.get("/node/HomeHeroStoryV2",{params:{member_hash:b}})}),topic:Dr(function(b){return $.get("/node/HomeTopicStoryV2",{params:{url_token:b}})})},h=$("div.single-story > .icon-sign").addClass("visible"),l=$("a.rep"),n=k;l.mouseenter(function(){n=setTimeout(v(d,
this),500)}).mouseleave(function(){clearTimeout(n)}).click(d).on("requestStory",function(){var b=$(this),c=b.data(),d=c.type,c=c.token;b.addClass("current").siblings().removeClass("current");e();g[d](c).done(function(c){$(".single-story-inner").fadeOut(150,function(){$(this).remove();$(c).insertAfter(h).hide().fadeIn(150)});b.trigger("afterRequestStory")})});e();var q=$("div.mobi-front"),r=$("div.desk-front");q.find(".js-signin, .js-signup").click(function(){r.find(".js-title-label").text("返回");r.find(".return").off().click(function(){window.location.hash=
""});c()});this.m().e(window,"hashchange",function(){var b=window.location.hash.slice(1);"signin"===b?(c(),B.Lt()):"signup"===b?(c(),B.CH()):(r.css("display",""),q.css("display",""))});this.m().e(Y,["accountcallback","sina_callback","qqconn_callback"],c);var b=window.location.hash.slice(1),w="signin"===b||"signup"!==b&&$("div.view-signin").hasClass("selected"),B=new il;("signin"===b||"signup"===b)&&c();B.tc=j;B.sn=w?"signin":"signup";B.o(J("js-sign-flow"));this.Tn();if(!sb){var b=$("div.single-story"),
H=$("div.rep"),I=k,Q=function(){var b=H.filter(":not(.current)").get();z.BS(b);return b[0]},w=function(){I||(I=setInterval(function(){$(Q()).trigger("requestStory")},5E3))},X=function(){clearInterval(I);I=k};b.hover(X,w);H.on("requestStory",X).on("afterRequestStory",w);b={start:w,stop:X};b.start();b=b.stop;this.Bo||(this.Bo=[]);this.Bo.push(v(b,i))}};
Er.prototype.Tn=function(){$.each({".app-link.ios":["click_zhihu_ios_dl_link","homepage_not_logged_in"],".app-link.android":["click_zhihu_android_dl_link","homepage_not_logged_in"],'a.app-download-button[href^="http://itunes"]':["click_zhihu_ios_dl_link","homepage_mobile_big_not_logged_in"],'a.app-download-button[href^="https://play.google.com"]':["click_zhihu_android_dl_link","homepage_mobile_big_not_logged_in"]},function(b,c){$(b).on("click",function(){W.apply(k,["app-promotion"].concat(c))})})};
Ca("ZH.entrySignPage",function(){(new Er).z()});If("sign");}})(zhihu);