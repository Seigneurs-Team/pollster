$(document).ready(function () {
    // Функция для проверки совпадения паролей
    function checkPasswords() {
        var password = $('#password').val();
        var passwordRepeat = $('#password-repeat').val();
        var errorMessage = $('#error-message');

        if (password !== passwordRepeat) {
            // Если пароли не совпадают, показываем сообщение об ошибке
            errorMessage.text('Пароли не совпадают!');
        } else {
            // Если пароли совпадают, очищаем сообщение об ошибке
            errorMessage.text('');
        }
    }

    // Добавляем обработчики событий на поля ввода
    $('#password, #password-repeat').on('input', checkPasswords);
});

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
// Инициализация фона при загрузке страницы
$(document).ready(function() {
    $('.password-control').each(function() {
        $(this).css('background-image', 'url(' + $(this).data('no-view') + ')');
    });
});