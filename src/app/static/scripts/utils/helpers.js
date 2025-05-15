
export function blockForm() {
    $('#loginForm').find('input, button').prop('disabled', true);
}

export function unblockForm() {
    $('#loginForm').find('input, button').prop('disabled', false);
    $('#overlay-loading').hide();
}

export function showLoadingOverlay() {
    $('#overlay-loading').show()
}

export function hideLoadingOverlay() {
    $('#overlay-loading').hide()
}

export function showSuccessOverlay() {
    $('#overlay-result').show()
    $('#overlay-message').text(`Добро пожаловать!`);
    $('#overlay-buttons').html('<button id="go-home">На главную</button>').show();
}

export function showFailOverlay(error) {
    $('#overlay-result').show()
    $('#overlay-message').text(`Ошибка: ${error.message}`);
    $('#overlay-buttons').html('<button id="try-again">Попробовать позже</button>').show();
}


export function showCreatedQR(url, qr_code) {
    console.log('showing created qr')

    if (!$('.qr-code-container').children().length) {

        // Создаем элемент <img> с jQuery и устанавливаем src
        const $qrCodeImage = $('<img>', {
            src: `data:image/png;base64,${qr_code}`,
            alt: 'QR-код опроса',
            class: 'qr-code'
        });

        // Вставляем изображение в контейнер
        $('.qr-code-container').append($qrCodeImage);
        $('.poll-link input').val(url)
    }


    $('#overlay-share-poll').show();
}


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


// Обработка кнопки "Вернуться на главную"
$('#overlay-result').on('click', '#go-home', function () {
    window.location.href = '/'; // Перенаправление на главную страницу
});

// Обработка кнопки "Попробовать позже"
$('#overlay-result').on('click', '#try-again', function () {
    $('#overlay-result').hide(); // Скрываем overlay
});

