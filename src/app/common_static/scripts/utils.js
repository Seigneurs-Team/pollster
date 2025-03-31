console.log('hello from utils.js')
function setFooterBackground() {
    console.log('hello from setFooterBackground()')
    console.log("$('.cloud-1')", $('.cloud-1'))
    // Фон страницы
    $(document).ready(function () {
        $('.cloud-1').css('background-image', 'url(' + $('.footer-wrapper').data('cloud-1') + ')');
        $('.cloud-2').css('background-image', 'url(' + $('.footer-wrapper').data('cloud-2') + ')');

        // $('.footer-wrapper').css('background-image', 'url(' + $('.footer-wrapper').data('background') + ')');
        console.log("$('.footer-wrapper').data('cloud-1'): ", $('.footer-wrapper').data('cloud-1'))
    });
}

export { setFooterBackground }