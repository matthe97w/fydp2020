
(function($) {
    $(window).on('load', function() {

      /* Page Loader active
      ========================================================*/
      $('#preloader').fadeOut();

      $('[data-toggle="tooltip"]').tooltip();

      $('[data-toggle="popover"]').popover();

      $("#footer").load("footer.html");
      $("#header").load("header.html");
      $("#navBar").load("navBar.html");

      populateOtherLogisticalData();
      getSessionInformation();
      setInterval(getSessionInformation, 5000);
    });

  }(jQuery));

  var applicationList = [];
  var applicationId = [];
  var studentData = [];
  var currStudentIndex = 0;
  var dictionary = {};

  var IPAddr = 'http://40.117.173.75:9090';
  //var IPAddr = 'http://rp:9090'; //Vidit Changes

  var oauth_token = window.localStorage.getItem('oauth_token');
  
  function applicationNameChange(){
      toggleButtons();
  }

  async function getSessionInformation(){
    $.ajax({
        url: IPAddr + '/sessions',
        // Sample output: {"users_with_sessions": ["6"]}
        type: 'GET',
        crossDomain: true,
        data:oauth_token,
        success: function(responseText) {
          var myData = JSON.parse(responseText);
          if(myData) {
              for(var i = 0; i < myData.users_with_sessions.length; i++){
              var studentID = parseInt(myData.users_with_sessions[i].userID);
              var firstName = myData.users_with_sessions[i].first_name;
              var lastName = myData.users_with_sessions[i].last_name;
              var studentInfoContainerID = "SingleStudent" + studentID;
              // Add a new container if one with this student ID doesn't exist
              if(!document.getElementById(studentInfoContainerID)) {
                var studentScreen = document.createElement('div');
                studentScreen.style = 'padding: 20px; display: inline-block;';
                studentScreen.id = studentInfoContainerID;
                document.getElementById('student-screens-container').appendChild(studentScreen);
                dictionary[studentID] = studentScreen;
              }
              populateScreenshots(studentID, studentInfoContainerID);
              populateStudentInformation(studentID, firstName, lastName, studentInfoContainerID);
            }

            // Search through all students believed to be active, and verify if they still are
            // If not, remove them
            for(var studentKey in dictionary) {
              var isStillActive = false;
              for(var i = 0; i < myData.users_with_sessions.length; i++){
                if (myData.users_with_sessions[i].userID == studentKey) {
                  isStillActive = true;
                  break;
                }
              }

              if (!isStillActive) { // Actually remove the div
                var studentDiv = dictionary[studentKey];
                document.getElementById(studentDiv.id).outerHTML = "";
                delete dictionary[studentKey];
              }
            }
          }

        },
        error: function(xhr){
          console.log('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
          alert('Retrieving session information failed, REEEE');
        }
      });

  }

  function populateScreenshots(studentID, studentScreenID) {
    let id = "Image" + studentID;
    if(!document.getElementById(id)){
      var section = document.createElement('div');
      section.id = id;
      var img = document.createElement('img');
      img.id = "StudentImage" + studentID;
      img.style = "width: 350px; height: 175px;";
      document.getElementById(studentScreenID).appendChild(section).appendChild(img);
    }
    var img = document.getElementById("StudentImage" + studentID);
    img.src = IPAddr + '/user/' + studentID + '/screen/snapshot?rand=' + Math.random();

    // img.src = "https://git.uwaterloo.ca/uploads/-/system/user/avatar/2957/avatar.png";
  }

  function populateStudentInformation(studentID, firstName, lastName, studentScreenID) {
    let id = "NameDiv" + studentID;
    if(!document.getElementById("StudentName" + studentID)){
      var section = document.createElement('div');
      section.id = id;

      var studentName= document.createElement("span");
      studentName.innerText = firstName + " " + lastName;
      studentName.setAttribute("id","StudentName" + studentID);
      document.getElementById(studentScreenID).appendChild(section).appendChild(studentName);
    }
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
