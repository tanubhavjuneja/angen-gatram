mainNav = function() {
	$("#topnav li").bind("mouseenter",function(){
                this.className += "_over over";
	}).bind("mouseleave",function(){
                this.className = this.className.replace("_over over", "");
	});
}

//For the DESKTOP site
$(function() {
	var url = window.location.pathname;
	var base;
	base = "m.justice.gov/";
	//base = "m.publicdevelopment.doj.gov/";
	//base = "m.justice.ews/";

	var android = navigator.userAgent.match(/Android/i);
	var iphone = navigator.userAgent.match(/iPhone/i);
	var berry = navigator.userAgent.match(/BlackBerry/i);
	var windows = navigator.userAgent.match(/Windows Phone/i);

	if(berry || iphone || android || windows) {
		var newRef;
	
		if(url.match("/ag/")) {
			newRef = base+"ag/index.html";
			prependRef(newRef);
		}
		else if(url.match("/agencies/")) {
			newRef = base+"agencies/index-list.html";
			prependRef(newRef);
		}
		else if(url.match("/careers/")) {
			newRef = base+"careers/careers.html";
			prependRef(newRef);
		}
		else if(url.match("accessibility_info")) {
			newRef = base+"accessibility_info.htm";
			prependRef(newRef);
		}
		else if(url.match("opa/pr")) {
			newRef = base+"top-stories.html";
			prependRef(newRef);
		}
		else if(url.match("/actioncenter/") || url.match("contact-us") || url.match("privacy-file") || url.match("legalpolicies") || url.match("accessibility_info")) {
			newRef = base+url;
			prependRef(newRef);
		}
		else {
			newRef = base;
			prependRef(newRef);
		}	
	}
});

prependRef = function(newRef) {
	if($(".printer").length > 0) {
		$(".printer").addClass("printerButton");
		$(".printer").prepend("<a href='http://"+newRef+"'><img src=\"/images/return-to-mobile_bt.jpg\" /></a>");
		$(".breadcrumbmenucontent").addClass("breadcrumbmenucontentshort");
		$(".breadcrumbmenucontentshort").removeClass("breadcrumbcontent");
	}
	else {
		console.log('here');
		$(".breadcrumbmenucontent").addClass("printer");
		$(".breadcrumbmenucontent").addClass("forceWidth");
		$(".breadcrumbmenucontent").append("<div class='printerButton'><a href='http://"+newRef+"'><img src=\"/images/return-to-mobile_bt.jpg\" /></a></div>");
	}
}
