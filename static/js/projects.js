$(document).ready(function() {
	$('.action-item').click(function() {
		$(this).children('form').submit();
	});
});
