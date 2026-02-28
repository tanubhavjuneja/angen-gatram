/*global window */
'use strict';
function hasCookieSupport() {
	window.document.cookie = "cookieTester=1; expires=Tue, 01 Mar 2033 17:21:05 GMT; path=/";
	return window.document.cookie.indexOf("cookieTester=1") !== -1;
}

if (window.location.search.indexOf("nosso=1") === -1) {
	if (((window.navigator.appVersion.indexOf("Safari/") !== -1 && (window.navigator.appVersion.indexOf('Version/6') !== -1 || window.navigator.appVersion.indexOf('Version/7') !== -1)) && (window.navigator.appVersion.indexOf("Chrome") === -1 && window.navigator.appVersion.indexOf("CriOS") === -1 && window.navigator.appVersion.indexOf("iPad") === -1 && window.navigator.appVersion.indexOf("iPhone") === -1)) || window.navigator.appName === 'Microsoft Internet Explorer') {
		if (hasCookieSupport()) {
			if (window.document.cookie.indexOf("KinjaInit=1") === -1) {
				window.document.cookie = "KinjaInit=1; path=/";
				window.location.href = window.location.protocol + "//" + (window.location.port === "9000" ? "apilocal.kinja.com:9001" : "api.kinja.com")  + "/api/sso/getSession?redirect=" + window.encodeURIComponent(
					window.location.protocol + "//" + window.location.host + "/setsession?r=" + encodeURIComponent(window.location.href)
				);
			}
		}
	}
}
if (window.navigator.appVersion.indexOf("Safari/") !== -1 && window.navigator.appVersion.indexOf('Version/5') !== -1 && window.navigator.appVersion.indexOf("Chrome") === -1 && window.navigator.appVersion.indexOf("CriOS") === -1 && window.navigator.appVersion.indexOf("iPad") === -1 && window.navigator.appVersion.indexOf("iPhone") === -1) {
	// disable sso for safari 5
	if (window.document.cookie.indexOf("KinjaToken=") === -1) {
		window.KINJA_NO_SSO = true;
	}
}
