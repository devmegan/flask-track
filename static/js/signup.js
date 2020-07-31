$(document).ready(function(){
     // change currency colours on switch
    $("#currency").on("click", function(){
        $("#switch-off, #switch-on").toggleClass("header-blue");
    });
    // clientside validation for signup form: first/last name
     $("#fname, #lname").on({
        focusout: function(){
            if (!$(this).val()){
                $(this).addClass("invalid");
            } else if ($(this).val().length == 1) {
                $(this).removeClass("valid").addClass("invalid").next().attr("data-error", "Please don't use initials");

            }
        },
        keydown: function(e){
            if (e.key === "Backspace" || e.key === "Delete"){
                if ($(this).val().length == 2 ) {
                    $(this).removeClass("valid").addClass("invalid");
                    $(this).next().attr("data-error", "Please don't use initials");
                } else if($(this).val().length == 1) {
                    $(this).removeClass("valid").addClass("invalid");
                    if ($(this).is("#fname")) {
                        $(this).next().attr("data-error", "Please enter your first name");
                    } else {
                        $(this).next().attr("data-error", "Please enter your last name");
                    }
                }
            }
        },
        keyup: function(e){
            if ($(this).val().length > 1){
                $(this).removeClass("invalid").addClass("valid");
            } else if ($(this).val().length == 0) {
                // works if user highlights and deletes whole value
                $(this).removeClass("valid").addClass("invalid");
                if ($(this).is("#fname")) {
                    $(this).next().attr("data-error", "Please enter your first name");
                } else {
                    $(this).next().attr("data-error", "Please enter your last name");
                }

            }
        }
    });
    //clientside validation for signup form: username
    $("#username").on({
        focusout: function(){
            if (!$(this).val()){
                $(this).addClass("invalid");
            } else if ($(this).val().length < 5) {
                $(this).removeClass("valid").addClass("invalid").next().attr("data-error", "Username needs to be 5-10 characters");
            }
        },
        keydown: function(e){
            if (e.key === "Backspace" || e.key === "Delete"){
                if ($(this).val().length == 5){
                    $(this).removeClass("valid").addClass("invalid").next().attr("data-error", "Username needs to be 5-10 characters");
                }
                if($(this).val().length == 1) {
                    $(this).next().attr("data-error", "Please enter a username");
                }
            }
        },
        keyup: function(){
            if ($(this).val().length > 4) {
                $(this).removeClass("invalid").addClass("valid");
            } else if ($(this).val().length == 0) {
                $(this).removeClass("valid").addClass("invalid").next().attr("data-error", "Please enter a username");
            }
        }
    });
    //clientside validation for signup form: email 
    $("#email").on({
        focusout: function(){
            if (!$(this).val()){
                $(this).addClass("invalid");
            } else if (!$(this).val().includes("@")) {
                $(this).removeClass("valid").addClass("invalid").next().attr("data-error", "Please enter a valid email address");
            }
        },
        keydown: function(e){
            if (e.key === "Backspace" || e.key === "Delete"){
                if ($(this).val().length == 1) {
                    $(this).removeClass("valid").addClass("invalid").next().attr("data-error", "Please enter an email address");
                } else if ($(this).val().slice(-1) == "@") {
                    $(this).removeClass("valid").addClass("invalid").next().attr("data-error", "Please use a valid email address");
                }
            }
        }, 
        keyup: function(){
            if ($(this).val().includes("@") && $(this).val().charAt(0) != "@" && !$(this).val().endsWith("@")){
                $(this).removeClass("invalid").addClass("valid");
            } else if ($(this).val().length == 0) {
                $(this).removeClass("valid").addClass("invalid").next().attr("data-error", "Please enter an email address");
            }
        }
    });
    // clientside signup form validation: password
    $("#password").on({
        focusout: function(){
            if (!$(this).val()){
                $(this).addClass("invalid");
            }
        },
        keydown: function(e){
            if (e.key === "Backspace" || e.key === "Delete"){
                $("#passwordcheck").removeClass("valid");
                if ($(this).val().length == 6) {
                    $(this).removeClass("valid").addClass("invalid").next().attr("data-error", "Password must be 6+ characters");
                }
            }
        }, 
        keyup: function(){
            if($(this).val().length > 5){
                $(this).removeClass("invalid").addClass("valid");
                if ($("#passwordcheck").val().length == $(this).val().length) {
                    $("#passwordcheck").removeClass("invalid").addClass("valid");
                }
            } else if ($(this).val().length == 0){
                $(this).removeClass("valid").addClass("invalid").next().attr("data-error", "Please enter a password");
            }
        }
    });
    // clientside signup form validation: password check
    $("#passwordcheck").on("keyup", function(e) {
        if ($(this).val().length > 4 && $(this).val() != $("#password").val()) {
            $(this).removeClass("valid").addClass("invalid");
            $("#password").removeClass("valid").addClass("invalid").next().attr("data-error", "Passwords don't match");
        } else if ($(this).val().length > 5 && $(this).val() == $("#password").val()){
            $(this).removeClass("invalid").addClass("valid");
            $("#password").removeClass("invalid").addClass("valid").next().attr("data-success", "Passwords match");
        }
    });
    // clientside signup form validation: submit
    $('#signup-btn').click(function(e) {
    // validate form input before submitting form
        e.preventDefault();
        if ($("#fname, #lname, #username, #email, #password, #passwordcheck").hasClass("invalid")){
            M.toast({html: 'It looks like some fields don\'t have a valid input'});
        } else {
            $("#register-user-form").submit();
        }
    });
});