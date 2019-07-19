$(document).ready(function(){
	if($('#tableDiv').length){
		checkHeightWindow()
	}
		$(window).resize(function(){checkHeightWindow()})
		$('div').on('change',function(){
			checkHeightWindow();
		})
})

function checkHeightWindow(){
	var tableDiv = $('#tableDiv')
	/*var toChange = tableDiv.offset().top + tableDiv.outerHeight(true) + $('#bottomMessage').outerHeight(true) + $('#downloadMethod').outerHeight(true) +  50*/
	/*var toChange = 900*/
	var toChange = $('#page').outerHeight(true) + 160
	if($(window).height() < toChange){
                $('#bottomMessage').css('position','relative');
                }
        else{
                $('#bottomMessage').css('position','absolute');     
	}
}
