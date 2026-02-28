
function render(stageName){
    var that = {};
    var gsFrame = document.createElement("iframe");
    gsFrame.id=stageName + "_frame";
    gsFrame.style.border = "0px";
    gsFrame.style.padding = "0px";
    gsFrame.style.margin = "0px";
    gsFrame.style.width = "300px";
    gsFrame.style.height = "250px";
    document.getElementById(stageName + "_stage").appendChild(gsFrame);

    function embed(width, height, contents){
        gsFrame.style.width = width+"px";
        gsFrame.style.height = height+"px";
        gsFrame.contentDocument.open();
        gsFrame.contentDocument.write(contents);
        gsFrame.contentDocument.close();

        // check visibility on load
        checkVisibility();
        window.addEventListener('load', checkVisibility, true);

        // recheck on each scroll event
        window.addEventListener('scroll', checkVisibility, true);
        window.addEventListener('resize', checkVisibility, true);
    }
    that.embed = embed;

    // Visibility stuff
    var iFrameVisible = function() {
        gsFrame.contentWindow.postMessage('displayed', '*');
    };

    var isVisible = function(el) {
        if(!el){
            return false;
        }
        var wX = window['pageXOffset'];
        var wY = window['pageYOffset'];
        var wW = window['innerWidth'];
        var wH = window['innerHeight'];

        var eX = el['offsetLeft'];
        var eY = el['offsetTop'];
        var eW = el['offsetWidth'];
        var eH = el['offsetHeight'];

        function isPixelVisible(x, y) {
            return ((x >= wX) && (x <= wX + wW) && (y >= wY) && (y <= wY + wH));
        }
        return (isPixelVisible(eX, eY) || isPixelVisible(eX, eY + eH) || isPixelVisible(eX + eW, eY) || isPixelVisible(eX + eW, eY + eH));
    };

    var visible = false;
    var checkVisibility = function() {
        if (isVisible(gsFrame)){
            visible = true;
            iFrameVisible();
        }
    };

    // Used by child iFrame to tell the parent to stop sending messages
    var messageHandlerName = stageName+"_handler";
    window[messageHandlerName] = function(event) {
        // Check the type of the message
        if (event.data === stageName+'_ad_ready') {
            window.removeEventListener("message", window[messageHandlerName], false);
            // dispatch displayed event
            displayed = true;
            checkVisibility();
        }
    };
    window.addEventListener("message", window[messageHandlerName], false);
    return that;
}
window['finished_loading'] = true;
