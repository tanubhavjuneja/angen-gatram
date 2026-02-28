mybuys.setClient("BARCODESINC");
mybuys.enableZones();
	
//zone styles
	mybuys.setStyleByPageType('HOME','.mbzone','width','925px');
	mybuys.setStyleByPageType('PRODUCT_DETAILS','.mbzone','width','700px','border','1px solid #B6BCBF','border-radius','5px','-moz-border-radius','5px','-webkit-border-radius','5px');

	
//slot styles
	mybuys.setStyleByPageType('HOME','.mbitem','width','213px','height','173px','text-align','center','border','1px solid #B6BCBF','margin-right','16px',
	                          'padding','20px 0px 20px 0px','border-radius','4px','-moz-border-radius','4px','-webkit-border-radius','4px',
							  'box-shadow','inset -5px -5px 5px #E9E9E9','-moz-box-shadow','inset -5px -5px 5px #E9E9E9','-webkit-box-shadow','inset -5px -5px 5px #E9E9E9');
	mybuys.setStyleByPageType('HOME','.mbitem:hover','width','213px','height','173px','text-align','center','border','1px solid #3B619F','margin-right','16px',
	                          'padding','20px 0px 20px 0px','border-radius','4px','-moz-border-radius','4px','-webkit-border-radius','4px',
							  'box-shadow','inset -5px -5px 10px #FDE5CC','-moz-box-shadow','inset -5px -5px 10px #FDE5CC','-webkit-box-shadow','inset -5px -5px 10px #FDE5CC');
	
	mybuys.setStyleByPageType('PRODUCT_DETAILS','.mbitem','width','160px','padding','13px 5px 10px 5px');

//link styles
	mybuys.setStyleByPageType('HOME','.mbnamerowspan','margin','0px 0px 10px 17px','width','175px','float','none','height','32px','overflow','hidden');
	mybuys.setStyleByPageType('HOME','.mbpricerowspan','margin','15px 0px');

	mybuys.setStyleByPageType('HOME','.mbnamelink','font-family','Arial,Helvetica,sans-serif','font-size','13px','color','#3B619F','font-weight','700');
	mybuys.setStyleByPageType('HOME','.mbnamelink:link','font-family','Arial,Helvetica,sans-serif','font-size','13px','color','#3B619F','font-weight','700');
	mybuys.setStyleByPageType('HOME','.mbnamelink:visited','font-family','Arial,Helvetica,sans-serif','font-size','13px','color','#3B619F','font-weight','700');
	mybuys.setStyleByPageType('HOME','.mbnamelink:hover','font-family','Arial,Helvetica,sans-serif','font-size','13px','color','#3B619F','font-weight','700');
	
	mybuys.setStyleByPageType('HOME','.mbpricelink','font-family','Arial,Helvetica,sans-serif','font-size','14px','color','#F68819','font-weight','700');
	mybuys.setStyleByPageType('HOME','.mbpricelink:link','font-family','Arial,Helvetica,sans-serif','font-size','14px','color','#F68819','font-weight','700');
	mybuys.setStyleByPageType('HOME','.mbpricelink:visited','font-family','Arial,Helvetica,sans-serif','font-size','14px','color','#F68819','font-weight','700');
	mybuys.setStyleByPageType('HOME','.mbpricelink:hover','font-family','Arial,Helvetica,sans-serif','font-size','14px','color','#F68819','font-weight','700');
	
	mybuys.setStyleByPageType('PRODUCT_DETAILS','.mbnamerowspan','width','150px','margin','10px 0px 5px 0px');
	mybuys.setStyleByPageType('PRODUCT_DETAILS','.mbpricerowspan','width','150px');
	
	mybuys.setStyleByPageType('PRODUCT_DETAILS','.mbnamelink','font-family','Arial,Helvetica,sans-serif','font-size','12px','color','#3B619F','font-weight','700');
	mybuys.setStyleByPageType('PRODUCT_DETAILS','.mbnamelink:link','font-family','Arial,Helvetica,sans-serif','font-size','12px','color','#3B619F','font-weight','700');
	mybuys.setStyleByPageType('PRODUCT_DETAILS','.mbnamelink:visited','font-family','Arial,Helvetica,sans-serif','font-size','12px','color','#3B619F','font-weight','700');
	mybuys.setStyleByPageType('PRODUCT_DETAILS','.mbnamelink:hover','font-family','Arial,Helvetica,sans-serif','font-size','12px','color','#3B619F','font-weight','700','text-decoration','underline');
	
	mybuys.setStyleByPageType('PRODUCT_DETAILS','.mbpricelink','font-family','Arial,Helvetica,sans-serif','font-size','13px','color','#333333','font-weight','700');
	mybuys.setStyleByPageType('PRODUCT_DETAILS','.mbpricelink:link','font-family','Arial,Helvetica,sans-serif','font-size','13px','color','#333333','font-weight','700');
	mybuys.setStyleByPageType('PRODUCT_DETAILS','.mbpricelink:visited','font-family','Arial,Helvetica,sans-serif','font-size','13px','color','#333333','font-weight','700');
	mybuys.setStyleByPageType('PRODUCT_DETAILS','.mbpricelink:hover','font-family','Arial,Helvetica,sans-serif','font-size','13px','color','#333333','font-weight','700');

//image styles
	mybuys.setStyleByPageType('HOME','.mbimgspan','margin','0px 56px 0px 56.5px');
	mybuys.setStyleByPageType('PRODUCT_DETAILS','.mbimgspan','margin','0px 0px 0px 25px');
	mybuys.setStyle('.mbimgcenter','height','100px','width','100px','display','table-cell','vertical-align','middle');
	
	if (/MSIE (\d+\.\d+);/.test(navigator.userAgent)){ //test for MSIE x.x;
		var ieversion=new Number(RegExp.$1) // capture x.x portion and store as a number
		if (ieversion>=7 && ieversion < 8) {
		mybuys.setStyle('.mbimgcenter','line-height','100px','padding-right','125px');
			//mybuys.setStyleByPageType('PRODUCT_DETAILS','#mybuyspagezone2 .bestSellerF','margin','3px 0px 3px 0px');
		}
	}
	
//zone-title styles
	mybuys.setStyleByPageType('PRODUCT_DETAILS','.mblegend','text-align','left','padding','5px 0px 0px 5px');
	mybuys.setStyleByPageType('PRODUCT_DETAILS','.mbtitle','color','#333333','font-family','Arial,Helvetica,sans-serif','font-size','14px');


mybuys.applyStyles();

mybuys.setFailOverMsecs(5000);
