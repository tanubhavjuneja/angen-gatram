var protocol = window.location.protocol;

function getScriptQuery(identifier) {
  var scripts = document.getElementsByTagName('script'), i, curScript;
   for (i = 0; i < scripts.length; ++i) {
    curScript = scripts[i];
    if (curScript.src.match(identifier)) {
     return (curScript.src.match(/\?.*/) || [undefined])[0];
    }
   }
 }

var qs = getScriptQuery('Image-JSinclude_wrapper.js');
var query = qs.substring(qs.indexOf("?imgurl=")+8)

document.write("<img src=\"" + protocol + "//" + decodeURIComponent(query) + "\" width=\"1\" height=\"1\" border=\"0\">");