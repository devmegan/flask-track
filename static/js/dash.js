$(document).ready(function(){
/*fire tooltips*/
    $('.tooltipped').tooltip();
/* fire datepicker with default dates*/
    $('.datepicker').datepicker({
     // set default date to goal end date
        setDefaultDate: new Date(),
        // prevent selecting end date before todays date
        minDate: new Date(),
        // only allow years to be current/future years
        yearRange: [2020, 2030]
    });
    //open datepicker on focusing on date field 
    $("#end_date").focus(function(){
        $('#end_date').click();
    });
/* nav to add goal card*/
    $('#create-goal-btn').click(function(){
        if ($("#create-goal-name").val()){
            $("#goal_name").val($("#create-goal-name").val());
            $("#create-goal-card").removeClass("display-none");
            $("#main-card").addClass("display-none");
        } else {
            $("#create-goal-name").addClass("invalid");
        }
    });

/* set img url input type */ 
    $('input:radio[name="img-method"]').change(function () {
        $("#image_url").removeAttr("disabled");
        if ($(this).val() == "keyword") {
            $("#image_url").attr("placeholder", "Enter Your Keyword").attr("type", "text").next().text('Enter Your Keyword (i.e. "beach", "car", "birthday")');
        } 
        else { 
            $("#image_url").attr("placeholder", "Enter Your Image URL").attr("type", "url").next().text('Enter Image Url ("https://...")');
        }  
    });

/* clientisde validation of create goal form */
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
                    $(this).removeClass("valid").addClass("invalid").next().attr("data-error", "Please enter a goal name");
                }
            }
        },
        keyup: function(e){
            if ($(this).val().length > 1){
                $(this).removeClass("invalid").addClass("valid").next().attr("data-success", "Goal Name");
            }
        }
    });
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
                    $(this).removeClass("valid").addClass("invalid").next().attr("data-error", "Please enter an image url");
                }
            }
        },
        keyup: function(e){
            if ($(this).val().length > 0){
                $(this).removeClass("invalid").next().text("Goal Image Url");
            }
        }
    });
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
                    $(this).removeClass("valid").addClass("invalid").next().attr("data-error", "Please enter a goal total");
                }
            } else if (e.keyCode>= 65 && e.keyCode <= 90){
                 M.toast({html: 'Please enter a number', classes: 'flash'});
            }
        },
        keyup: function(e){
            if ($(this).val().length > 0){
                $(this).removeClass("invalid").addClass(valid);
            }
        }
    });
    //fetch image by url and validate create goal input
    $('#create-goal-submit').click(function(e) {
        e.preventDefault();
        // flash error message if form fields empty/invalid
        if ($("#goal_name, #img_url, #end_total").hasClass("invalid")) {
            M.toast({html: 'It looks like some fields don\'t have a valid input', classes: 'flash'});
        } else if ($("#goal_name, #img_url, #end_total").val().length == 0) {
            M.toast({html: 'Please make sure you\'ve filled in all the fields', classes: 'flash'});
        } else {
            if ($('input:radio[name="img-method"]:checked').val() == "keyword") {
                // display loading spinner to until promise completes
                $("#create-goal-card").addClass("display-none");
                $("#spinner-col").removeClass("display-none");
                // fetch url of image related to keyword
                var search_keyword = $('input:text[name="image_url"]').val();
                fetch(`https://source.unsplash.com/1600x900/?${search_keyword}`).then((response)=> { 
                    var fetched_url = response.url;
                    if (fetched_url == "https://images.unsplash.com/source-404?fit=crop&fm=jpg&h=800&q=60&w=1200"){
                        /* if the fetch returns an "image not found" url, going to use a placeholder savings image instead */
                        fetched_url = "https://images.unsplash.com/photo-1579621970795-87facc2f976d?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=1950&q=80";
                    }
                    $('#image_url').val(fetched_url);
                    /* save keyword in hidden form input - keyword and image url will be stored as anonymised array in mongo*/ 
                    $('#search_keyword').val(search_keyword);
                    $("#create-goal-form").submit();
                });
            }  else {
                /* check if it looks like an image url - basic client side security*/
                given_url = $('#image_url').val();
                given_url_extension = given_url.split('.').pop();
                if (given_url_extension == "jpeg" || given_url_extension == "png" || given_url_extension == "jpg"){
                    // display loading spinner to user during validation
                    $("#create-goal-card").addClass("display-none");
                    $("#spinner-col").removeClass("display-none");
                    $("#create-goal-form").submit();
                } else {
                    M.toast({html: 'That doesn\'t look like an image URL', classes: 'flash'});
                }
            }
        }
    });
});