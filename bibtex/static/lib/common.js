//Some useful general functions
"use strict";

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

function swalError(error) {
	swal({
		title: "Error!", 
		text: text, 
		type: "error", 
		confirmButtonText: "OK" 
	});
}

function swalWarn(title, text, confirmButtonText, okFunction) {
	swal({
			title: title,
			text: text,
			type: "warning",
			showCancelButton: true,
			confirmButtonColor: "#FF5B55",
			confirmButtonText: confirmButtonText
		}, 
		okFunction);
}
