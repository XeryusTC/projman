$(document).ready(function() {
	$('.login').click(function() {
		popup = $('#login-popup').clone();
		popup.attr('id', 'actual-login-popup');
		popup.show();
		mui.overlay('on', popup[0]);
	});
});
