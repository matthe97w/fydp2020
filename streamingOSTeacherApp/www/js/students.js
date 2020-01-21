
(function($) {
    $(window).on('load', function() {
        
      /* Page Loader active
      ========================================================*/
      $('#preloader').fadeOut();
  
      $('[data-toggle="tooltip"]').tooltip()
  
      $('[data-toggle="popover"]').popover()
      populateOtherLogisticalData();
      getSessionInformation();
    });      
  
  }(jQuery));
  
  var applicationList = [];
  var applicationId = [];
  var studentData = [];
  var currStudentIndex = 0;
  
  var IPAddr = 'http://40.117.173.75:9090';
  //var IPAddr = 'http://rp:9090'; //Vidit Changes
  
  var oauth_token = window.localStorage.getItem('oauth_token');
      
  function studentNameChange(){
      currStudentIndex = getStudentIndexfromUserId();
      updateStatusTable();
  }
  
  function applicationNameChange(){
      toggleButtons();
  }
  
  function getSessionInformation(){  		
      // $.ajax({
      //   url: IPAddr + '/session/',
      //   // Sample output: {"users_with_sessions": ["6"]}
      //   type: 'GET',
      //   crossDomain: true,
      //   data:oauth_token,
      //   success: function(responseText) {
      //     var myData = JSON.parse(responseText);
      //     if(myData) {
      //         for(var i = 0; i < myData.users_with_sessions.length; i++){	
                // setTimeout(getSessionInformation, 5000);
                var studentScreen = document.createElement('div');
                document.getElementById('student-screens-container').appendChild(studentScreen);
                populateScreenshots(6, 0);
                populateStudentInformation(5, 0);

                // populateScreenshots(parseInt(myData.users_with_sessions[9]));
      //         }
      //     }
          
      //   },
      //   error: function(xhr){
      //     console.log('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
      //     alert('Retrieving session information failed, REEEE');
      //   }
      // });
  }
  
  function populateScreenshots(studentID, index) {
    var img = document.createElement('img'); 
    //     url: IPAddr + '/user/' + studentID + '/screen/snapshot/',
    img.src = "https://git.uwaterloo.ca/uploads/-/system/user/avatar/2957/avatar.png";
    img.id = "StudentImage" + index;
    document.getElementById('student-screens-container').appendChild(img);

  }

  function populateStudentInformation(studentID, index) {
    $.ajax({
      url: IPAddr + '/user/' + window.localStorage.getItem('userName') + '/info',
      type: 'GET',
      crossDomain: true,
      data:oauth_token,
      success: function(responseText) {
        var myData = JSON.parse(responseText);
        if(myData){
          var studentName= document.createTextNode(myData.user[0].first_name + " " + myData.user[0].last_name);
          document.getElementById('StudentImage' + index).appendChild(studentName);
        }	
      },
      error: function(xhr){
        console.log('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
        alert('Invalid username and password combination');
      }
    });	 
   

  }

  
  function populateSchoolName(schoolName){
      document.getElementById("schoolNameDiv").innerHTML = document.getElementById("schoolNameDiv").innerHTML.replace("{schoolName}",schoolName.toUpperCase());
      
  }
  
  
  function populateProfessorName(professorName){
      document.getElementById("professorNameDiv").innerHTML = document.getElementById("professorNameDiv").innerHTML.replace("{professorName}",professorName);
      
  }
  
  
  function getStudentIndexfromUserId(){
      index = 0;
      for(var i = 0; i < studentData.length; i++){
          if(studentData[i].studentId === parseInt(document.getElementById("studentDropdown").value)){
              index = i;
          }
      }
      
      return index;
  }
  

  
  function returnSuccessString(isGrant){
      var myStr = "Successfully revoked application access.";
      
      if(isGrant){
          myStr = myStr.replace("revoked","granted");
          return myStr;
      }
      
      return myStr;
  }
  
  function populateOtherLogisticalData(){
      $.ajax({
            url: IPAddr + '/user/' + window.localStorage.getItem('userName') + '/info',
            type: 'GET',
            crossDomain: true,
            data:oauth_token,
            success: function(responseText) {
              var myData = JSON.parse(responseText);
              if(myData){
                  populateSchoolName(myData.user[0].school_name);
                  populateProfessorName(myData.user[0].first_name + " " + myData.user[0].last_name);
              }	
            },
            error: function(xhr){
              console.log('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
              alert('Invalid username and password combination');
            }
      });	
  }
      
  function updateStatusTable(){
      while(document.getElementById("statusTable").rows.length > 1) {
              document.getElementById("statusTable").deleteRow(1);
      }
      
      populateStatusTable();
  }