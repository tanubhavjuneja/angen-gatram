document.getElementsByClassName = function(cl) {
	var retnode = [];
	var myclass = new RegExp('\\b'+cl+'\\b');
	var elem = this.getElementsByTagName('*');
	for (var i = 0; i < elem.length; i++) {
		var classes = elem[i].className;
		if (myclass.test(classes)) retnode.push(elem[i]);
	}
	return retnode;
}; 

// days after which the cookie will expire
var referrerCookieExpirationDays = 5000;

// referring and landing page URLs
var REF = document.referrer;
var LAND = location.href;

//CID
var l = "ABCDEFGHJKLMNPQRSTUVWXYZ";
var n = "23456789";
var CID = n.charAt(Math.floor(Math.random() * n.length));
CID += l.charAt(Math.floor(Math.random() * l.length));
CID += l.charAt(Math.floor(Math.random() * l.length));
CID += n.charAt(Math.floor(Math.random() * n.length));
CID += l.charAt(Math.floor(Math.random() * l.length));
CID += l.charAt(Math.floor(Math.random() * l.length));

// identify domain
var domain = location.hostname;
if(domain.indexOf(".") < domain.lastIndexOf(".")) {
	domain = domain.substr(domain.indexOf(".") + 1);
}

function setReferrerCookie () {
	var nowDate = new Date();

	var expiresDate = new Date();
	expiresDate.setTime(expiresDate.getTime() + (referrerCookieExpirationDays*24*60*60*1000));

	var cookieValue =
		"REF=" + escape(REF) +
		":REFD=" + escape(nowDate.toGMTString()) +
		":CID=" + escape(CID) +
		":SRC=" + escape(LAND) +
		"; expires=" + expiresDate.toGMTString() +
		"; path=/" + "; domain=" + domain; 

	document.cookie = cookieValue;
}

function isReferrerCookieSet () {
	return (document.cookie.indexOf("REF=") == -1);
}

function isValidReferrerDomain () {
	// invalid domains regular expression
	var invalidDomainsRE = new RegExp("^https?:\\/\\/(www\\.)?" + domain + "", "gi");
	return !invalidDomainsRE.test(REF);
}

function isValidPPCSrc (src) {
	// valid PPC source regular expression
	var validPPCRE = new RegExp("\\?(as|aw|as&.*|aw&.*|az|ar|biz|be|ci|dt|ls|msn|my|nt|ov|pg|pr|ps|pt|pw|sd|sm|sp|y|source=CashbackShopping)(&zmam=2134960&zmas=1&zmac=[0-9]+&zmap=.*?)?$");
	return validPPCRE.test(src);
}

function isValidAffiliateSrc (src) {
	// valid affiliate source regular expression
	var validAffiliateRE = new RegExp("\\?aff-(isv)-(.+)$", "i");
	return validAffiliateRE.test(src);
}

if (isReferrerCookieSet()) {
	setReferrerCookie ();
} else {
	var cookieREF = unescape(document.cookie.replace(/.*REF=([^:]*).*/g, "$1"));
	var cookieLAND = unescape(document.cookie.replace(/.*SRC=([^;]*).*/g, "$1"));

	if (isValidReferrerDomain() && !isValidAffiliateSrc(cookieLAND) && (isValidPPCSrc(LAND) || isValidAffiliateSrc(LAND) || ((cookieREF == "") && !isValidAffiliateSrc(cookieLAND) && !isValidPPCSrc(cookieLAND)))) {
		setReferrerCookie ();
	}
}

if(document.cookie.indexOf("CID=") == -1) {
	var REF = unescape(document.cookie.replace(/.*REF=([^:]*).*/g, "$1"));
	var LAND = unescape(document.cookie.replace(/.*SRC=([^;]*).*/g, "$1"));
	setReferrerCookie ();
}

var CID = unescape(document.cookie.replace(/.*CID=([^:]*).*/g, "$1"));
var REMOTE_HOST = "(none)";

var availablehtml = "Product ships the same business day if your order is placed before 4:00 p.m. CT (6:00 p.m. CT for 2nd day or faster service).<small><br><br>Same day shipping not available for some products.</small>";
var addtocartpricehtml = "Some manufacturers don't allow us to advertise our low prices. Add this item to your cart to see our lowest available price.";
var loginpricehtml = "Some manufacturers don't allow us to advertise our low prices. By creating an account or logging in, you'll have access to all our best prices across the site.";
var configurationshtml = "We carry a number of options or configurations of this product (for example, different interfaces or different included cables, etc).<br><br>Products marked <strong>TOP SELLING</strong> are the most popular configurations with our customers.";

function addChecked(classname, link, qty) {
	var cartlink = link;
	var addtocart = document.getElementsByClassName(classname);
	var addtnqtystr = '';
	for (var i = 0; i < addtocart.length; i++ ) {
		if (addtocart[i].type == 'checkbox') {
			if (addtocart[i].checked == true) {
				cartlink = cartlink + "," + addtocart[i].value;
				addtnqtystr += ',1';
			}
		}
	}
	qtynode = document.getElementById(qty);
	var qtyval = qtynode.options[qtynode.selectedIndex].value;
	cartlink = cartlink + '/qty=' + qtyval + addtnqtystr;
	location.href=cartlink;
}

function warrantyChecker(currentwarr) {
	warrchecks = document.getElementsByClassName("add-to-cart-warranties");
	for (var i = 0; i < warrchecks.length; i++ ) {
		if((currentwarr.getAttribute('id') != warrchecks[i].getAttribute('id')) && (currentwarr.value == warrchecks[i].value)){
			if(currentwarr.checked == true){
				warrchecks[i].checked = true;
			}
			else{
				warrchecks[i].checked = false;
			}
		}
		else if((currentwarr.getAttribute('id') != warrchecks[i].getAttribute('id')) && (currentwarr.value != warrchecks[i].value)){
			if(currentwarr.checked == true){
				warrchecks[i].checked = false;
			}
		}
	}
}

//if no filters, results span across entire div
function filterCheck() {
	var boxbodycheck = document.getElementsByClassName('boxbody'),
		filters = document.getElementById('filter_categories'),
		filtertd = document.getElementById('filtertd'),
		filterspace = document.getElementById('filterspace'),
		cat_description = document.getElementById('body_container_520'),
		resultsshadow = document.getElementById('filtersPresent_Shadow');
	if(boxbodycheck.length > 1) {
		if(filtertd){
			if(jQuery.trim(boxbodycheck[1].innerHTML) == ""){
				filters.style.display = 'none';
				filtertd.style.display = 'none';
			}
			else{
				filters.style.display = 'block';
				filtertd.style.display = 'block';
			}
		}
	} else {
		cat_description.style.width = '700px';
		resultsshadow.style.width = '950px';
		resultsshadow.style.background = 'url(/images/shadow_mainimage.png) center 0 no-repeat';
		if(filterspace){
			filterspace.style.paddingLeft = '8px';
		}
	}
}

function showFilters(){
	var filtercats = document.getElementById('filter_categories');
	if(filtercats){
		filtercats.style.display = 'block';
	}
}

function modelPageResizer(){
	var productimages = document.getElementById('product-images');
	var modeldetails = document.getElementById('model-details');
	var modelinfo = document.getElementById('model-info');
	if(!productimages){
		jQuery(modeldetails).width(jQuery(modelinfo).width());
	}
}

function switchFilterGroupNav (nav_obj, group, switch_from, switch_to)
{
	document.getElementById("filter_group_nav_" + group + "_" + switch_from).className = "filter_group_nav_off";
	nav_obj.className = "filter_group_nav_on";
	document.getElementById("filter_" + group + "_" + switch_from).style.display = "none";
	document.getElementById("filter_" + group + "_" + switch_to).style.display = "block";
}

function toggleHiddenDivs(arg)
{
	var callingA = document.getElementById("Control_" + arg);
	var displayTABLE = document.getElementById("DT_" + arg);
	var titleTD = document.getElementById("BARTD_" + arg);
	var blocksToHide = getElementsByClass("HE_" + arg, displayTABLE, "tr");
	var message = "";
	if(titleTD.style.display == "")
	{
		titleTD.style.display = "none";
		message = "+ All descriptions";
	}
		else
	{
		titleTD.style.display = "";
		message = "- One description";
	}
	for(var i in blocksToHide)
	{
		if(blocksToHide[i].style.display == "")
	{
		blocksToHide[i].style.display = "none";
	}
		else
	{
		blocksToHide[i].style.display = "";
	}
	}
		while(callingA.hasChildNodes())
	{
		callingA.removeChild(callingA.childNodes[0]);
	}
		callingA.appendChild(document.createTextNode(message));
}

//Thanks be to Dustin Diaz and John Resig
function getElementsByClass(searchClass,node,tag)
{
	var classElements = new Array();
	if ( node == null )
	node = document;
	if ( tag == null )
	tag = '*';
	var els = node.getElementsByTagName(tag);
	var elsLen = els.length;
	var pattern = new RegExp("(^|\\s)"+searchClass+"(\\s|$)");
	for (i = 0, j = 0; i < elsLen; i++) {
	if ( pattern.test(els[i].className) ) {
		classElements[j] = els[i];
		j++;
	}
	}
	return classElements;
}

function redirectToURL(path, sorting)
{
	var dropSelect = document.getElementById('sortDrop');
	var urlTemplate = path;
	var currSort = "Best Match,";
	var newSort = dropSelect.options[dropSelect.selectedIndex].value;
	//window.alert(newSort + " => " + currSort);
	if(newSort != currSort)
	{
	newSort = newSort.split(",");
	var redirectURL = urlTemplate.replace("XXXXXXXXXX", sorting);
	var pattern = /page[0-9]+/g;
	//redirectURL = redirectURL.replace(new RegExp(pattern, "page1"), redirectURL);
	if(newSort[1])
	{
		redirectURL = redirectURL + newSort[1];
	}
	location.href = redirectURL;
	}
}

function copy_clip(copy_text) {
	if (window.clipboardData) {
		window.clipboardData.setData("Text", copy_text);
	}
	else if (window.netscape) {
		netscape.security.PrivilegeManager.enablePrivilege('UniversalXPConnect');
		var clip = Components.classes['@mozilla.org/widget/clipboard;1'].createInstance(Components.interfaces.nsIClipboard);
		if (!clip) return;
		var trans = Components.classes['@mozilla.org/widget/transferable;1'].createInstance(Components.interfaces.nsITransferable);
		if (!trans) return;
		trans.addDataFlavor('text/unicode');
		var str = new Object();
		var len = new Object();
		var str = Components.classes["@mozilla.org/supports-string;1"].createInstance(Components.interfaces.nsISupportsString);
		str.data = copy_text;
		trans.setTransferData("text/unicode", str, copy_text.length*2);
		var clipid = Components.interfaces.nsIClipboard;
		if (!clip) return false;
		clip.setData(trans, null, clipid.kGlobalClipboard);
	}
}

function stockChecker(partnum, stockcode){
	data = new Object();
	data.partnum = partnum;
	data.stockcode = stockcode
	$.ajax({
		url: "http://" + window.location.hostname + "/stockchecker.htm",
		type: "POST",
		dataType: "json",
		data:  data,
		'beforeSend': function(){
			$('.stockbtn' + data.partnum).hide();
			$('.loading' + data.partnum).show();
		},
		error: function(jqXHR, textStatus, error){
			$('.stockbtn' + data.partnum).show();
			$('.loading' + data.partnum).hide();
		},
		success: function(response){
			$('.stockbtn' + data.partnum).show();
			$('.loading' + data.partnum).hide();
			$.each(response, function(rootlv){
				//Go through for each vendor and show the stock and cost numbers
				if(rootlv != 'updatetime' && rootlv != 'partnum'){
					var stocknum = response[rootlv].stocknum;
					var costnum = response[rootlv].costnum;
					$('#' + rootlv + 'Stock' + response.partnum).html(stocknum);
					if(costnum != 0 && costnum != ''){ $('#' + rootlv + 'Cost' + response.partnum).html(costnum); }
				}
			});
			//Now let's display the date that the stock was last refreshed for this item
			if(response.updatetime){
				$('#lastref' + response.partnum).html(response.updatetime);
			}
		}
	});
}

function searchRedirect(searchtext, perlfect){
	var redirstr = "/search.htm?";
	if(perlfect){
		redirstr += "q=";
	}
	window.location.replace(redirstr + searchtext);
}

/***********************************************
* 
* JavaScript Tool Tip for all Mouse-over text
* 
***********************************************/
var tooltip=function(){
 var id = 'tt';
 var top = 3;
 var left = 3;
 var maxw = 300;
 var speed = 10;
 var timer = 20;
 var endalpha = 95;
 var alpha = 0;
 var tt,t,c,b,h;
 var ie = document.all ? true : false;
 return{
  show:function(v,w){
   if(tt == null){
	tt = document.createElement('div');
	tt.setAttribute('id',id);
	t = document.createElement('div');
	t.setAttribute('id',id + 'top');
	c = document.createElement('div');
	c.setAttribute('id',id + 'cont');
	b = document.createElement('div');
	b.setAttribute('id',id + 'bot');
	tt.appendChild(t);
	tt.appendChild(c);
	tt.appendChild(b);
	document.body.appendChild(tt);
	tt.style.opacity = 0;
	tt.style.filter = 'alpha(opacity=0)';
	document.onmousemove = this.pos;
   }
   tt.style.display = 'block';
   c.innerHTML = v;
   tt.style.width = w ? w + 'px' : 'auto';
   if(!w && ie){
	t.style.display = 'none';
	b.style.display = 'none';
	tt.style.width = tt.offsetWidth;
	t.style.display = 'block';
	b.style.display = 'block';
   }
  if(tt.offsetWidth > maxw){tt.style.width = maxw + 'px'}
  h = parseInt(tt.offsetHeight) + top;
  clearInterval(tt.timer);
  tt.timer = setInterval(function(){tooltip.fade(1)},timer);
  },
  pos:function(e){
   var u = ie ? event.clientY + document.documentElement.scrollTop : e.pageY;
   var l = ie ? event.clientX + document.documentElement.scrollLeft : e.pageX;
   tt.style.top = (u - h) + 'px';
   tt.style.left = (l + left) + 'px';
  },
  fade:function(d){
   var a = alpha;
   if((a != endalpha && d == 1) || (a != 0 && d == -1)){
	var i = speed;
   if(endalpha - a < speed && d == 1){
	i = endalpha - a;
   }else if(alpha < speed && d == -1){
	 i = a;
   }
   alpha = a + (i * d);
   tt.style.opacity = alpha * .01;
   tt.style.filter = 'alpha(opacity=' + alpha + ')';
  }else{
	clearInterval(tt.timer);
	 if(d == -1){tt.style.display = 'none'}
  }
 },
 hide:function(){
  clearInterval(tt.timer);
   tt.timer = setInterval(function(){tooltip.fade(-1)},timer);
  }
 };
}();