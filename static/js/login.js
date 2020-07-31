$(document).ready(function(){
    // clientside validation for login form: username
     $("#username").on({
        focusout: function(){
            if ($(this).val().length < 5){
                $(this).removeClass("valid").addClass("invalid");
            }
        },
        keydown: function(e){
            if (e.key === "Backspace" || e.key === "Delete"){
                if ($(this).val().length <= 5 ) {
                    $(this).removeClass("valid").addClass("invalid");
                }
            }
        },
        keyup: function(e){
            if ($(this).val().length > 4){
                $(this).removeClass("invalid").addClass("valid");
            } else if ($(this).val().length == 0) {
                // works if user highlights and deletes whole value
                $(this).removeClass("valid").addClass("invalid");
            }
        }
    });
    // clientside validation for login form: password
     $("#password").on({
        focusout: function(){
            if (!$(this).val()){
                $(this).removeClass("valid").addClass("invalid").next().attr("data-error", "Please enter your password");
            } else if ($(this).val().length < 6 && $(this).hasClass("valid")) {
                $(this).removeClass("valid").addClass("invalid").next().attr("data-error", `Your password is longer than ${$(this).val().length} characters`);
            }
        },
        keydown: function(e){
            if (e.key === "Backspace" || e.key === "Delete"){
                if ($(this).val().length < 7) {
                    $(this).removeClass("valid").addClass("invalid").next().attr("data-error", `Your password is longer than ${$(this).val().length - 1} characters`);
                }
            } else if ($(this).val().length < 5 && $(this).hasClass("invalid")) {
                $(this).removeClass("valid").addClass("invalid").next().attr("data-error", `Your password is longer than ${$(this).val().length + 1} characters`);
            }
        }, 
        keyup: function(){
            if($(this).val().length > 5){
                $(this).removeClass("invalid").addClass("valid");
            } else if ($(this).val().length == 0){
                $(this).removeClass("valid").addClass("invalid").next().attr("data-error", "Please enter your password");
            }
        }
    });
     $('#login-signup-btn').click(function(e) {
    // validate form input before submitting form
        e.preventDefault();
        if ($("#username").hasClass("invalid") && $("#password").hasClass("invalid")){
            M.toast({html: 'Please make sure your username and password are valid', classes: 'flash'});
        } else if ($("#username").hasClass("invalid")) {
            M.toast({html: 'Please make sure your username is valid', classes: 'flash'});
        } else if ($("#password").hasClass("invalid")) {
            M.toast({html: 'Please make sure your password is valid', classes: 'flash'});
        } else {
            $("#login-form").submit();
        }
    });
});