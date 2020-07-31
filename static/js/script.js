$(document).ready(function(){
    /* index.html */
    $('.carousel.carousel-slider').carousel({
        fullWidth: true,
        indicators: true
    });
    setInterval(function(){
        $('.carousel').carousel('next');
    }, 10000);
});