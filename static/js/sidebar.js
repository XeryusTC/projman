$(document).ready(function() {
	$('.js-hide-sidebar').on('click', function() {
		$('body').toggleClass('hide-sidebar');
	});

	$('.js-show-sidebar').on('click', function() {
		var sidebar = $('#sidebar');
		var options = {
			onclose: function() {
				sidebar.removeClass('active').appendTo(document.body);
			}
		};

		var overlayEl = $(mui.overlay('on', options));

		sidebar.appendTo(overlayEl);
		setTimeout(function() {
			sidebar.addClass('active');
		}, 20);
	});
});
