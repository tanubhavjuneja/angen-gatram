(function() {
    var req = window['gsad'];
    if (req) {
        // set a version identifier
        req['v'] = 1;

        // set a cache buster
        req['z'] = (+ new Date);

        // get or generate the ad div if any (and clear out the param to avoid sending to the svr)
        var divId = req['ad_id'];
        if (divId == undefined) {
            if (! window['gsadId']) {
                window['gsadId'] = 1;
            }
            else {
                window['gsadId'] += 1;
            }
            divId = req['ad_id'] = "gsad" + window['gsadId'];
        }

        if (! document.getElementById(divId)) {
            document.write('<div id="' + divId + '" style="text-align:center;margin:0;width:100%"></div>');
        }

        // join the sizes
        if (req['sizes']) {
            req['sizes'] = req['sizes'].join(",");
        }

        // build the ad request using parameters from the request and from the normalized list
        var url = "http://adsx.greystripe.com/openx/www/delivery/mw2.php?";
        var first = true;
        for (var param in req) {
            var val = req[param];
            if (param && val != undefined && val != "") {
                url = [ url, 
                        first ? "" : "&", 
                        param, "=", encodeURIComponent(String(val)) 
                      ].join("");
                first = false;
            }
        }

        document.write('<div id="gs_'+divId+'_stage" style="overflow:hidden;">\n');
        document.write('  <script type="text/javascript">window.finished_loading = false;</script>\n');
        document.write('  <script type="text/javascript" src="http://c.greystripe.com/js/render-mw-host-0.18.js" ></script>\n');
        document.write('  <script src="' + url + '"></script>\n');
        document.write('</div>\n');
    }
})()