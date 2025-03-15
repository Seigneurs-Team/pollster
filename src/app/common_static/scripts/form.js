// общий код для sign_in и create_new_account

// переключение видимости пароля
$('body').on('click', '.password-control', function () {
    console.log('.password-control clicked')

    var $passwordInput = $(this).parent('.password-wrapper').find('.password')
    var $control = $(this);
    var viewIcon = $control.data('view');
    var noViewIcon = $control.data('no-view');
    console.log($control)

    if ($passwordInput.attr('type') === 'password') {
        $control.css('background-image', 'url(' + viewIcon + ')');

        $passwordInput.attr('type', 'text');
    } else {
        $control.css('background-image', 'url(' + noViewIcon + ')');
        $passwordInput.attr('type', 'password');
    }
    return false;
})

// Инициализация кнопки для показа пароля при загрузке страницы
// Фон страницы
$(document).ready(function() {
    $('.password-control').each(function() {
        $(this).css('background-image', 'url(' + $(this).data('no-view') + ')');
    });
    $('main').css('background-image', 'url(' + $('main').data('background') + ')');
    console.log("$('main').data('background'): ", $('main').data('background'))


});