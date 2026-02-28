/* Click handlers handler */
$(document).ready( function() {
	
	$("#datepicker").change(function () {
		var url = $("select option:selected").val();
		window.location.href = url;
	});

	$("a[rel='pop-up-share']").click(function () {
		var features = "height=500,width=550,scrollTo,resizable=0,scrollbars=0,location=0,top=100,left=100";
		newwindow=window.open(this.href, 'Share', features);
		return false;
	});

	$("a[rel='ext'],a[rel='external']").click( function() {
		window.open( $(this).attr('href') );
		return false;
	});


	$("#datepicker").change(function () {
		var url = $("select option:selected").val();
		window.location.href = url;
	});

	$("A[href*='/email-this']").fancybox({
		fitToView		: false,
		width			: 460,
		height			: 550,
		autoSize		: false,
		type			: 'iframe'
	});
	
	$("a[rel='lightbox']").fancybox({
		'width'				: 650,
		'height'			: 500,
		'autoScale'			: false,
		'transitionIn'		: 'none',
		'transitionOut'		: 'none',
		'type'				: 'iframe'
	});
	
	$("A[href*='.jpg'],[href*='.jpeg'],[href*='.png'],[href*='.gif']").fancybox({
		fixed : 'false',
		helpers : {
			title : {
				type : 'over'
			}
		}
	});
	
	
	$(".sid-photo-deprecated").fancybox({
		'padding'		: 0,
		'maxWidth'		: 630,
		'maxHeight'		: 420,
		'fitToView'		: false,
		'width'			: 630,
		'height'		: 420,
		'autoSize'		: false,
		'closeClick'	: false,
		'openEffect'	: 'none',
		'closeEffect'	: 'none'
	});
						
});