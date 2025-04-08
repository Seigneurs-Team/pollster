// общий код для sign_in и create_new_account

// переключение видимости пароля
$('body').on('click', '.password-control', function () {
    console.log('.password-control clicked')

    var $passwordInput = $(this).parent('.password-wrapper').find('.password')
    var $control = $(this);
    console.log($control)

    if ($passwordInput.attr('type') === 'password') {
        $control.addClass('view')

        $passwordInput.attr('type', 'text');
    } else {
        $control.removeClass('view')
        $passwordInput.attr('type', 'password');
    }
    return false;
})