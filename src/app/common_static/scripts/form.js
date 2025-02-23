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
$(document).ready(function() {
    $('.password-control').each(function() {
        $(this).css('background-image', 'url(' + $(this).data('no-view') + ')');
    });
});