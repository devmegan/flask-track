$(document).ready(function(){
/* Edit Goal Validation */
    // clientside validation: goal name
    $("#goal_name").on({
        focusout: function(){
            if (!$(this).val()){
                $(this).removeClass("valid").addClass("invalid").next().attr("data-error", "Please enter a goal name");
            }
        },
        keydown: function(e){
            if (e.key === "Backspace" || e.key === "Delete"){
                if ($(this).val().length == 1 ) {
                    $(this).removeClass("valid").addClass("invalid").next().attr("data-error", "Please enter a goal name")
                }
            }
        },
        keyup: function(e){
            if ($(this).val().length > 1){
                $(this).removeClass("invalid").addClass("valid").next().attr("data-success", "Goal Name")
            }
        }
    })
    // clientside validation: img url
    $("#image_url").on({
        focusout: function(){
            if (!$(this).val()){
                $(this).removeClass("valid").addClass("invalid").next().attr("data-error", "Please enter an image url");
            }
        },
        keydown: function(e){
            if (e.key === "Backspace" || e.key === "Delete"){
                if ($(this).val().length == 1 ) {
                    $(this).removeClass("valid").addClass("invalid").next().attr("data-error", "Please enter an image url")
                }
            }
        },
        keyup: function(e){
            if ($(this).val().length > 0){
                $(this).removeClass("invalid").next().text("Goal Image Url")
            }
        }
    })
    // clientside validation: end total
    $("#end_total").on({
        focusout: function(){
            if (!$(this).val()){
                $(this).removeClass("valid").addClass("invalid").next().attr("data-error", "Please enter a goal total");
            }
        },
        keydown: function(e){
            if (e.key === "Backspace" || e.key === "Delete"){
                if ($(this).val().length == 1 ) {
                    $(this).removeClass("valid").addClass("invalid").next().attr("data-error", "Please enter a goal total")
                }
            } else if (!(e.keyCode>= 48 && e.keyCode <= 57)){
                 M.toast({html: 'Please enter a number', classes: 'flash'});
            }
        },
        keyup: function(e){
            if ($(this).val().length > 0){
                $(this).removeClass("invalid").addClass(valid)
            }
        }
    })
    
/* Delete Goal Form Validation */
    // clientside validation: delete user 
    $("#password_delete").on({
        focusout: function(){
             if (!$(this).val()){
                $(this).removeClass("valid").addClass("invalid").next().attr("data-error", "Please enter your password");
            } else if ($(this).val().length < 6) {
                $(this).removeClass("valid").addClass("invalid").next().attr("data-error", `Your password is longer than ${$(this).val().length} characters`);
            }
        },
        keydown: function(e){
            if (e.key === "Backspace" || e.key === "Delete"){
                if ($(this).val().length < 7) {
                    $(this).removeClass("valid").addClass("invalid").next().attr("data-error", `Your password is longer than ${$(this).val().length - 1} characters`)
                }
            } else if ($(this).val().length < 5 && $(this).hasClass("invalid")) {
                $(this).removeClass("valid").addClass("invalid").next().attr("data-error", `Your password is longer than ${$(this).val().length + 1} characters`)
            }
        }, 
        keyup: function(){
            if($(this).val().length > 5){
                $(this).removeClass("invalid").addClass("valid")
            } else if ($(this).val().length == 0){
                $(this).removeClass("valid").addClass("invalid").next().attr("data-error", "Please enter your password")
            }
        }
    });
    $(".edit-goal-link").click(function(){
        $("#edit-goal-card").removeClass("display-none");
        $(".card:not('#edit-goal-card'), #deposit-btn, #deposit-btn-sm, #withdraw-btn-sm, #withdraw-btn").addClass("display-none")
    })
    $("#delete-goal-link").click(function(){
        $("#delete-goal-card").removeClass("display-none");
        $("#edit-goal-card").addClass("display-none");
    })
    $("#deposit-btn, #deposit-btn-sm").click(function(){
    $("#deposit-card").removeClass("display-none")
    $(".card:not('#deposit-card'), #deposit-btn, #deposit-btn-sm, #withdraw-btn-sm, #withdraw-btn").addClass("display-none")
 })
  $("#withdraw-btn, #withdraw-btn-sm").click(function(){
    $("#withdraw-card").removeClass("display-none")
    $(".card:not('#withdraw-card'), #deposit-btn, #deposit-btn-sm, #withdraw-btn-sm, #withdraw-btn").addClass("display-none")
 })

 $(".goal-card-back").click(function(){
    $(".card:not('#withdraw-card, #edit-goal-card, #delete-goal-card'), #deposit-btn, #deposit-btn-sm, #withdraw-btn-sm, #withdraw-btn").removeClass("display-none")
    $("#withdraw-card, #deposit-card, #edit-goal-card, #delete-goal-card").addClass("display-none")
 })
$("#time-stats-card").hover(function() {
    $("#time-stats-one, #time-stats-two").toggleClass("display-none");
});


 $("#withdraw-5").click(function(){
            $("#withdraw_value").val("5.00")
        });
        $("#withdraw-10").click(function(){
            $("#withdraw_value").val("10.00")
        });
        $("#withdraw-25").click(function(){
            $("#withdraw_value").val("25.00")
        });
        $("#withdraw-50").click(function(){
            $("#withdraw_value").val("50.00")
        });
        $("#deposit-5").click(function(){
            $("#deposit_value").val("5.00")
        });
        $("#deposit-10").click(function(){
            $("#deposit_value").val("10.00")
        });
        $("#deposit-25").click(function(){
            $("#deposit_value").val("25.00")
        });
        $("#deposit-50").click(function(){
            $("#deposit_value").val("50.00")
        });
        $('#edit-goal-submit-btn').click(function(e) {
            e.preventDefault();
            given_url = $('#image_url').val()
            given_url_extension = given_url.split('.').pop();
            if (given_url_extension == "jpeg" || given_url_extension == "png" || given_url_extension == "jpg"){
                $("#edit-goal-form").submit();
            } else if (given_url.slice(0,28) == "https://images.unsplash.com/"){
                //if url was fetched from unsplash by keyword, doesn't have .jpg/.png at end of url, but still needs to submit
                $("#edit-goal-form").submit();
            } else {
                M.toast({html: 'That doesn\'t look like an image URL', classes: 'flash'});
            }
        })
        $('.datepicker').datepicker({
            // set default date to goal end date
            setDefaultDate: '{{ goal.end_date.strftime("%b %d, %Y") }}',
            // prevent selecting end date before todays date
            minDate: new Date(),
            // only allow years to be current/future years
            yearRange: [2020, 2100]
        });
    //open datepicker on focusing on date field 
    $("#end_date").focus(function(){
        $('#end_date').click();
    })
});
