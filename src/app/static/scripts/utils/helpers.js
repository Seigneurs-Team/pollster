
export function blockForm() {
    $('#loginForm').find('input, button').prop('disabled', true);
    $('#loading-overlay').show();
    $('#overlay-message').text('Выполняется проверка...');
    $('#overlay-buttons').hide();
}

export function unblockForm() {
    $('#loginForm').find('input, button').prop('disabled', false);
    $('#loading-overlay').hide();
}

export function showLoadingOverlay() {
    $('#loading-overlay').show()
}

export function hideLoadingOverlay() {
    $('#loading-overlay').hide()
}

export function showSuccessOverlay() {
    $('#overlay-message').text(`Добро пожаловать!`);
    $('#overlay-buttons').html('<button id="go-home">Вернуться на главную</button>').show();
}

export function showFailOverlay(error) {
    $('#overlay-message').text(`Ошибка: ${error.message}`);
    $('#overlay-buttons').html('<button id="try-again">Попробовать позже</button>').show();
}


export function showQR(url, qr_code) {
    // Создаем элемент <img> с jQuery и устанавливаем src
    const $qrCodeImage = $('<img>', {
        src: `data:image/png;base64,${qr_code}`,
        alt: 'QR-код опроса',
        class: 'qr-code'
    });

    // Вставляем изображение в контейнер
    $('.qr-code-container').append($qrCodeImage);
    $('.poll-link input').val(url)


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
$('#loading-overlay').on('click', '#go-home', function () {
    window.location.href = '/'; // Перенаправление на главную страницу
});

// Обработка кнопки "Попробовать позже"
$('#loading-overlay').on('click', '#try-again', function () {
    $('#loading-overlay').hide(); // Скрываем overlay
});

