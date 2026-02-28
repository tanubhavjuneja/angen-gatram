/* 
 * Mediaplex Flash template, flash_new
 * Maintained By: Christopher D. Robison (cdr@cdr2.com) and 
 * Heath Matthew Kornblum (heathkornblum@gmail.com) 
 * Last Modified: 1/15/2013 3:22 pm
 *
*/
(function(){
	var mojopro = window.location.protocol;
	if (mojopro == "https:") {
		mojopro = "https://secure.img-cdn.mediaplex.com/0/";
	}	else  {
		mojopro = "http://img-cdn.mediaplex.com/0/";
  	};  
	var mpvce = '<mpvce/>';
	mpenhanced = "",
	mpenhancedurl = "" || "http://www.mediaplex.com/ad-choices";
	if (mpvce == 1) {
		mpvclick = encodeURIComponent("");
		mpvc = mpvclick;
	}
	else if (mpvce == 2) {
		mpvclick2 = encodeURIComponent("");
		mpvc = encodeURIComponent(mpvclick2);
	}
	else
  	{
		mpvc = ("");
  	}
	var mpcke = '<mpcke/>';
	if (mpcke == 1) {
		mpcclick = encodeURIComponent("adfarm.mediaplex.com%2Fad%2Fck%2F10105-164702-2060-101%3Fmpt%3D%5B1929527938ER%5D");
		mpck = "http://" + mpcclick;
	}
	else if (mpcke == 2) {
		mpcclick2 = encodeURIComponent("adfarm.mediaplex.com%2Fad%2Fck%2F10105-164702-2060-101%3Fmpt%3D%5B1929527938ER%5D");
		mpck = "http://" + encodeURIComponent(mpcclick2);
	}
	else if (mpcke == -1) { 
		mpcclick = "adfarm.mediaplex.com/ad/ck/10105-164702-2060-101?mpt=[1929527938ER]"; 
		mpck = "http://" + mpcclick; 
	} 
	else
  	{
		mpck = ("http://adfarm.mediaplex.com%2Fad%2Fck%2F10105-164702-2060-101%3Fmpt%3D%5B1929527938ER%5D");
  	}
	var mp_swver = 0, mp_html = "", mp_crpv = 6 * 1;
	mp_html += "<div id='mp_wrapper25410067' style='position:relative;display:inline-block;width:300px;height:600px;'>";
	if( navigator.mimeTypes && navigator.mimeTypes["application/x-shockwave-flash"] && navigator.mimeTypes["application/x-shockwave-flash"].enabledPlugin ) {
  		if( navigator.plugins && navigator.plugins["Shockwave Flash"] ) {
    		mp_swver = (navigator.plugins["Shockwave Flash"].description.split( " " ))[2];
  		}
	} else if ( navigator.userAgent && navigator.userAgent.indexOf("MSIE") >= 0 && ( navigator.userAgent.indexOf("Windows") >= 0 ) ) {
		var mp_axo,e;
  		for( var mp_i = 11; mp_i > 6; mp_i-- ) {
			try {
				mp_axo = new ActiveXObject("ShockwaveFlash.ShockwaveFlash." + mp_i );
				mp_swver = mp_i;
				break;
			} catch (e) {}
		}
	}
	if( mp_swver >= mp_crpv ) {
  		mp_html +=  '<object classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000" ';
  		mp_html += ' codebase="https://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=6,0,40,0" id="25410067" name="movie25410067" width="300" height="600">';
  		if( mp_swver > 5 ) {
			mp_html += '<param name="FlashVars" value="clickTAG=' + mpvc + mpck +'&clickTag=' + mpvc + mpck + '&clickTag1=' + mpvc + mpck + '">';
			mp_html += '<param name="movie" value="' + mojopro + '10105/PF_Vday14_300x600_DODControl_12astrchocHgsksfrv12lsrrfrv.swf">';
			mp_html += '<param name="wmode" value="opaque">';
			mp_html += '<param name="allowscriptaccess" value="always">';
  		} 
  		else {
			mp_html += '<param name="movie" value="' + mojopro + '10105/PF_Vday14_300x600_DODControl_12astrchocHgsksfrv12lsrrfrv.swf?clickTAG=' + mpvc + mpck +'&clickTag=' + mpvc + mpck + '&clickTag1=' + mpvc + mpck + '">';
			mp_html += '<param name="wmode" value="opaque">';
			mp_html += '<param name="allowscriptaccess" value="always">';
  		}
  		if( mp_swver > 5 ) {
			mp_html += '<embed wmode="opaque" allowscriptaccess="always" name="PF_Vday14_300x600_DODControl_12astrchocHgsksfrv12lsrrfrv.swf" src="' + mojopro + '10105/PF_Vday14_300x600_DODControl_12astrchocHgsksfrv12lsrrfrv.swf" FlashVars="clickTAG=' + mpvc + mpck  +'&clickTag=' + mpvc + mpck  +'&clickTag1=' + mpvc + mpck  + '"';
		}
 		else {
    		mp_html += '<embed wmode="opaque" allowscriptaccess="always" NAME="PF_Vday14_300x600_DODControl_12astrchocHgsksfrv12lsrrfrv.swf" src="' + mojopro + '10105/PF_Vday14_300x600_DODControl_12astrchocHgsksfrv12lsrrfrv.swf?clickTAG=' + mpvc + mpck  +'&clickTag=' + mpvc + mpck  +'&clickTag1=' + mpvc + mpck  + '"';
		}
 		mp_html += ' swLiveConnect="false" width="300" height="600" type="application/x-shockwave-flash" pluginspage="">';
  		mp_html += '</embed>';
  		mp_html += '</object>';
  		mp_html += (mpenhanced) ? "<div style='position:absolute;z-index:10500;top:0px;right:1px;width:17px;height15px;z-index:999999;overflow:hidden;' onmouseover='this.style.width = \"75px\";document.getElementById(\"en_sm_25410067\").style.display=\"none\";document.getElementById(\"en_lg_25410067\").style.display=\"inline\";' onmouseout='this.style.width = \"17px\";document.getElementById(\"en_sm_25410067\").style.display=\"inline\";document.getElementById(\"en_lg_25410067\").style.display=\"none\";'><a href='" + mpenhancedurl + "' target='_blank'><img src='" + mojopro + "16179/109012/IconOnlyCollisionMarker.png' border='0'  id='en_sm_25410067'  style='display:inline'/><img src='" + mojopro + "16179/109012/CollisionAdMarker.png' border='0' id='en_lg_25410067'  style='display:none' /></a></div>" : "";
	
  		mp_html += '</div>';
    		document.write( mp_html );
	} else if( !( navigator.appName && navigator.appName.indexOf("Netscape") >= 0 && navigator.appVersion.indexOf("2.") >= 0 ) ) {

  		document.write('<a href="http://adfarm.mediaplex.com/ad/ck/10105-164702-2060-101?mpt=[1929527938ER]" target="_blank"><img src="' + mojopro + '10105/PF_Vday14_300x600_DODControl_12astrchocHgsksfrv12lsrrfrv.jpg" width="300" height="600" border="0" alt=""></a>');
	}
        document.close();
})();

   function mojo_clickthru() {
	     var OOBImg = new Image();
         if (typeof (mpOOBClickTrack) !== 'undefined') {
            try {
				OOBImg.src = mpOOBClickTrack;
			} catch (e) {
			  if (window.console && window.console.error) {
				   window.console.error(e.message);
			  }
			}
         }
   }

//-->

document.write( "<script type=\"text/javascript\" src=\"http://img-cdn.mediaplex.com/0/10105/Image-JSinclude_wrapper.js?imgurl=providecommerce.sp1.convertro.com/view/vt/v1/providecommerce/1/cvo.gif%3Fcvosrc%3Ddisplay.101051647022060101.25410067\"><"+"/script>");

