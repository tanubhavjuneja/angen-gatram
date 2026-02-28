$(document).ready(function() {
	/*------------------------------------*\
		show all
	\*------------------------------------*/
	$('#theft-id-show-all').click(function() {
		$('#theft-id-list-1').show('fast', function() {
		  $('#theft-id-arrow-1').html('<img src="/criminal/fraud/images/up-arrow.png" width="8" height="8" alt="Up Arrow" border="0" />');
		});
		$('#theft-id-list-2').show('fast', function() {
		  $('#theft-id-arrow-2').html('<img src="/criminal/fraud/images/up-arrow.png" width="8" height="8" alt="Up Arrow" border="0" />');
		});
		$('#theft-id-list-3').show('fast', function() {
		  $('#theft-id-arrow-3').html('<img src="/criminal/fraud/images/up-arrow.png" width="8" height="8" alt="Up Arrow" border="0" />');
		});
		$('#theft-id-list-4').show('fast', function() {
		  $('#theft-id-arrow-4').html('<img src="/criminal/fraud/images/up-arrow.png" width="8" height="8" alt="Up Arrow" border="0" />');
		});
		$('#theft-id-list-5').show('fast', function() {
		  $('#theft-id-arrow-5').html('<img src="/criminal/fraud/images/up-arrow.png" width="8" height="8" alt="Up Arrow" border="0" />');
		});
		$('#theft-id-list-6').show('fast', function() {
		  $('#theft-id-arrow-6').html('<img src="/criminal/fraud/images/up-arrow.png" width="8" height="8" alt="Up Arrow" border="0" />');
		});
		$('#theft-id-list-7').show('fast', function() {
		  $('#theft-id-arrow-7').html('<img src="/criminal/fraud/images/up-arrow.png" width="8" height="8" alt="Up Arrow" border="0" />');
		});
	});
	/*------------------------------------*\
		hide all
	\*------------------------------------*/
	$('#theft-id-hide-all').click(function() {
		$('#theft-id-list-1').hide('fast', function() {
		  $('#theft-id-arrow-1').html('<img src="/criminal/fraud/images/down-arrow.png" width="8" height="8" alt="Down Arrow" border="0" />');
		});
		$('#theft-id-list-2').hide('fast', function() {
		  $('#theft-id-arrow-2').html('<img src="/criminal/fraud/images/down-arrow.png" width="8" height="8" alt="Down Arrow" border="0" />');
		});
		$('#theft-id-list-3').hide('fast', function() {
		  $('#theft-id-arrow-3').html('<img src="/criminal/fraud/images/down-arrow.png" width="8" height="8" alt="Down Arrow" border="0" />');
		});
		$('#theft-id-list-4').hide('fast', function() {
		  $('#theft-id-arrow-4').html('<img src="/criminal/fraud/images/down-arrow.png" width="8" height="8" alt="Down Arrow" border="0" />');
		});
		$('#theft-id-list-5').hide('fast', function() {
		  $('#theft-id-arrow-5').html('<img src="/criminal/fraud/images/down-arrow.png" width="8" height="8" alt="Down Arrow" border="0" />');
		});
		$('#theft-id-list-6').hide('fast', function() {
		  $('#theft-id-arrow-6').html('<img src="/criminal/fraud/images/down-arrow.png" width="8" height="8" alt="Down Arrow" border="0" />');
		});
		$('#theft-id-list-7').hide('fast', function() {
		  $('#theft-id-arrow-7').html('<img src="/criminal/fraud/images/down-arrow.png" width="8" height="8" alt="Down Arrow" border="0" />');
		});
	});
	/*------------------------------------*\
		theft id toggle 1
	\*------------------------------------*/
	$('#theft-id-row-1').mouseover(function() {
		$('#theft-id-row-1').css('cursor', 'pointer');
	});
	$('#theft-id-row-1').click(function() {
		var theftidList1isVisible = $('#theft-id-list-1').is(":visible");
		//alert(statutesList1isVisible);
		$('#theft-id-list-1').toggle('fast', function() {
		  if (theftidList1isVisible == true) {
			  $('#theft-id-arrow-1').html('<img src="/criminal/fraud/images/down-arrow.png" width="8" height="8" alt="Down Arrow" border="0" />');
		  } else {
			  $('#theft-id-arrow-1').html('<img src="/criminal/fraud/images/up-arrow.png" width="8" height="8" alt="Up Arrow" border="0" />');
		  }
		});
	});
	/*------------------------------------*\
		theft id toggle 2
	\*------------------------------------*/
	$('#theft-id-row-2').mouseover(function() {
		$('#theft-id-row-2').css('cursor', 'pointer');
	});
	$('#theft-id-row-2').click(function() {
		var theftidList1isVisible = $('#theft-id-list-2').is(":visible");
		//alert(statutesList1isVisible);
		$('#theft-id-list-2').toggle('fast', function() {
		  if (theftidList1isVisible == true) {
			  $('#theft-id-arrow-2').html('<img src="/criminal/fraud/images/down-arrow.png" width="8" height="8" alt="Down Arrow" border="0" />');
		  } else {
			  $('#theft-id-arrow-2').html('<img src="/criminal/fraud/images/up-arrow.png" width="8" height="8" alt="Up Arrow" border="0" />');
		  }
		});
	});
	/*------------------------------------*\
		theft id toggle 3
	\*------------------------------------*/
	$('#theft-id-row-3').mouseover(function() {
		$('#theft-id-row-3').css('cursor', 'pointer');
	});
	$('#theft-id-row-3').click(function() {
		var theftidList1isVisible = $('#theft-id-list-3').is(":visible");
		//alert(statutesList1isVisible);
		$('#theft-id-list-3').toggle('fast', function() {
		  if (theftidList1isVisible == true) {
			  $('#theft-id-arrow-3').html('<img src="/criminal/fraud/images/down-arrow.png" width="8" height="8" alt="Down Arrow" border="0" />');
		  } else {
			  $('#theft-id-arrow-3').html('<img src="/criminal/fraud/images/up-arrow.png" width="8" height="8" alt="Up Arrow" border="0" />');
		  }
		});
	});
	/*------------------------------------*\
		theft id toggle 4
	\*------------------------------------*/
	$('#theft-id-row-4').mouseover(function() {
		$('#theft-id-row-4').css('cursor', 'pointer');
	});
	$('#theft-id-row-4').click(function() {
		var theftidList1isVisible = $('#theft-id-list-4').is(":visible");
		//alert(statutesList1isVisible);
		$('#theft-id-list-4').toggle('fast', function() {
		  if (theftidList1isVisible == true) {
			  $('#theft-id-arrow-4').html('<img src="/criminal/fraud/images/down-arrow.png" width="8" height="8" alt="Down Arrow" border="0" />');
		  } else {
			  $('#theft-id-arrow-4').html('<img src="/criminal/fraud/images/up-arrow.png" width="8" height="8" alt="Up Arrow" border="0" />');
		  }
		});
	});
	/*------------------------------------*\
		theft id toggle 5
	\*------------------------------------*/
	$('#theft-id-row-5').mouseover(function() {
		$('#theft-id-row-5').css('cursor', 'pointer');
	});
	$('#theft-id-row-5').click(function() {
		var theftidList1isVisible = $('#theft-id-list-5').is(":visible");
		//alert(statutesList1isVisible);
		$('#theft-id-list-5').toggle('fast', function() {
		  if (theftidList1isVisible == true) {
			  $('#theft-id-arrow-5').html('<img src="/criminal/fraud/images/down-arrow.png" width="8" height="8" alt="Down Arrow" border="0" />');
		  } else {
			  $('#theft-id-arrow-5').html('<img src="/criminal/fraud/images/up-arrow.png" width="8" height="8" alt="Up Arrow" border="0" />');
		  }
		});
	});
	/*------------------------------------*\
		theft id toggle 6
	\*------------------------------------*/
	$('#theft-id-row-6').mouseover(function() {
		$('#theft-id-row-6').css('cursor', 'pointer');
	});
	$('#theft-id-row-6').click(function() {
		var theftidList1isVisible = $('#theft-id-list-6').is(":visible");
		//alert(statutesList1isVisible);
		$('#theft-id-list-6').toggle('fast', function() {
		  if (theftidList1isVisible == true) {
			  $('#theft-id-arrow-6').html('<img src="/criminal/fraud/images/down-arrow.png" width="8" height="8" alt="Down Arrow" border="0" />');
		  } else {
			  $('#theft-id-arrow-6').html('<img src="/criminal/fraud/images/up-arrow.png" width="8" height="8" alt="Up Arrow" border="0" />');
		  }
		});
	});
	/*------------------------------------*\
		theft id toggle 7
	\*------------------------------------*/
	$('#theft-id-row-7').mouseover(function() {
		$('#theft-id-row-7').css('cursor', 'pointer');
	});
	$('#theft-id-row-7').click(function() {
		var theftidList1isVisible = $('#theft-id-list-7').is(":visible");
		//alert(statutesList1isVisible);
		$('#theft-id-list-7').toggle('fast', function() {
		  if (theftidList1isVisible == true) {
			  $('#theft-id-arrow-7').html('<img src="/criminal/fraud/images/down-arrow.png" width="8" height="8" alt="Down Arrow" border="0" />');
		  } else {
			  $('#theft-id-arrow-7').html('<img src="/criminal/fraud/images/up-arrow.png" width="8" height="8" alt="Up Arrow" border="0" />');
		  }
		});
	});
});