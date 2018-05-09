/* Custom code for the fancybox lightbox */
jQuery(document).ready(function($) {

	/* 在所有img标签外面加上一层a标签 */
	/* 顺便加上一层 div，对 img 进行居中显示 */
	$("img").each(function(){
		if(this.id=="") {
            var strA = "<div style='text-align:center' ><a style='background:transparent' href='" + this.src + "'></a></div>";
            $(this).wrapAll(strA);
        }
	});

	/* Apply fancybox to multiple items */
	$("a[href$='.jpg'],a[href$='.jpeg'],a[href$='.png'],a[href$='.gif']").attr('class', 'group').attr('rel', 'group1');
	
	/* Apply fancybox to multiple items */
	$("dt.gallery-icon a").attr('class', 'group').attr('rel', 'group1');

	$("a.group").fancybox({
		'transitionIn'	:	'elastic',
		'transitionOut'	:	'elastic',
		'speedIn'		:	300, 
		'speedOut'		:	200,
		'autoScale'		:	true,
		'overlayShow'	:	true,
		'showNavArrows' :	false,
		'enableEscapeButton' :	true
	});
});
