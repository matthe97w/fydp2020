(function($) {
  $(window).on('load', function() {

    /* Page Loader active
    ========================================================*/
    $('#preloader').fadeOut();

    $('[data-toggle="tooltip"]').tooltip()

	$('[data-toggle="popover"]').popover()

	// Clean local storage
	window.localStorage.clear();

  });

}(jQuery));

var IPAddr = 'http://40.117.173.75:9090';
sessionStorage.setItem("IPAddr", "http://40.117.173.75:9090");
//var IPAddr = 'http://rp:9090'; //Vidit Changes

function login(){
	window.localStorage.clear();
	var userName = document.getElementById("inputUserId").value;
	var pwd = document.getElementById("inputPassword").value;
	$.ajax({
		url: IPAddr + '/user/' + userName + "/scope",
		type: 'GET',
		crossDomain: true,
		success: function(response) {
			var obj = JSON.parse(response);
			var userType = obj["user"][0].user_type;
			var scopingVar;
			// TODO: Fix this awful response formatting in RP
			if (userType == "teacher") 
				scopingVar = "teacherStreamingOS studentTeacherStreamingOS"
			else if (userType == "student")
				scopingVar = "studentStreamingOS studentTeacherStreamingOS"
			else {
				alert("Unknown user type!");
				return;
			}
			window.localStorage.setItem('scope', userType);
			
			myParams = {
				client_id: userType,
				grant_type:"password",
				username: userName,
				password: pwd,
				scope: scopingVar
			};

			$.ajax({
				url: IPAddr + '/token',
				type: 'POST',
				crossDomain: true,
				data:myParams,
				success: function(response) {
					window.localStorage.setItem('userName', userName);
					window.localStorage.setItem('oauth_token', response);
					//"access_token=NMJI5qp2igpgxtimYb28i23tWb8Cc1&expires_in=3600&token_type=Bearer&scope=teacherStreamingOS%20studentTeacherStreamingOS&refresh_token=bZM0a3Jtp4tdhMu6nPFxoqyB6USdR1"
					// window.localStorage.setItem()
					window.location.href = "master.html";
				},
				error: function(xhr){
				  console.log('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
				  alert('Invalid username and password combination');
				}
			  });
		},
		error: function(xhr){
		  console.log('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
		  alert('Invalid username and password combination');
		}
	  });
}
