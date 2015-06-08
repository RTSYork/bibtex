//Some useful general functions

if(!String.prototype.startsWith){
	String.prototype.startsWith = function (str) {
		return !this.indexOf(str);
	}
}

function reenableSubmitButtons() {
	$(".submit").each(function(index) {
		$(this).removeClass("submitdisabled");
	});
}
