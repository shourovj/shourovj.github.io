if (!VanillaZotero) {
	VanillaZotero = {};
}
VanillaZotero.Util = {
	randomString: function(len, chars) {
		if (!chars) {
			chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';
		}
		if (!len) {
			len = 8;
		}
		var randomstring = '';
		for (var i=0; i<len; i++) {
			var rnum = Math.floor(Math.random() * chars.length);
			randomstring += chars.substring(rnum,rnum+1);
		}
		return randomstring;
	},
	readCookie: function(name) {
		var nameEQ = name + '=';
		var ca = document.cookie.split(';');
		for(var i=0;i < ca.length;i++) {
			var c = ca[i];
			while (c.charAt(0)==' ') c = c.substring(1,c.length);
			if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length,c.length);
		}
		return null;
	},
	
	getDiscussionID: function() {
		//TODO
	},

	getUserID: function() {
		const userInfo = JSON.parse(decodeURIComponent(VanillaZotero.Util.readCookie('zoteroUserInfoJ')));
		if(userInfo){
			return parseInt(userInfo['userID']);
		}
		return false;
	},
};

jQuery(document).ready(function($) {
	let userInfoCookieJ = VanillaZotero.Util.readCookie('zoteroUserInfoJ');
	let userInfoCookie = VanillaZotero.Util.readCookie('zoteroUserInfo');
	if(userInfoCookie && !userInfoCookieJ) {
		fetch(`${VanillaZotero.config.baseUrl}/user/vanillarefresh`, {
			credentials: 'include'
		});
	}
});
