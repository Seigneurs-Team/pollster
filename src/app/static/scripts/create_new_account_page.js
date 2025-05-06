import { getChallenge, findProof } from './/utils/POW.js';
import { sendRequest } from './api.js';
let errorMessage = $('#error-message');

async function sendRegistrationRequest(data) {
    return sendRequest('/register', 'POST', data);
}


$('#loginForm').on('submit', async function (event) {
    console.log('clicked')
    event.preventDefault(); // предотвращает стандартное поведение формы

    let [login, password, passwordRepeat, nickname] = getFormData()

    // Если пароли совпадают, очищаем сообщение об ошибке
    errorMessage.text('');

    // Блокируем форму
    $('#loginForm').find('input, button').prop('disabled', true);

    // Показываем индикатор загрузки
    $('#loading-overlay').show();
    $('#overlay-message').text('Выполняется проверка...');
    $('#overlay-buttons').hide(); // Скрываем кнопки

    try {
        // Шаг 1: Получаем challenge от бэкенда
        const challenge = await getChallenge();

        // Шаг 2: Находим nonce
        const nonce = await findProof(challenge);

        // Шаг 3: Формируем JSON с данными для регистрации
        let data = {
            login: login,
            password: password,
            pow: nonce,
            nickname: nickname,
        }
        console.log('data', data);

        // Шаг 4: Отправляем данные на сервер
        const response = await sendRegistrationRequest(data);

        // Обработка ответа от сервера
        responseProcessing(response)

    } catch (error) {
        console.error('Ошибка:', error);
        $('#overlay-message').text('Произошла ошибка. Пожалуйста, попробуйте снова.');
        $('#overlay-buttons').html('<button id="try-again">Попробовать снова</button>').show();
    } finally {
        // Разблокируем форму
        $('#loginForm').find('input, button').prop('disabled', false);
    }
});


// Функция для проверки совпадения паролей
function checkPasswords() {
    let password = $('input[name="password"]').val();
    let passwordRepeat = $('input[name="password-repeat"]').val();

    if (password === passwordRepeat) {
        errorMessage.text('');
    } else {
        errorMessage.text('Пароли не совпадают!');
    }
}

function getFormData() {
    // Получаем данные из формы
    let login = $('input[name="login"]').val();
    let password = $('input[name="password"]').val();
    let passwordRepeat = $('input[name="password-repeat"]').val();
    let nickname = $('input[name="nickname"]').val();
    return [login, password, passwordRepeat, nickname]
}

function responseProcessing(response) {
    console.log(response.status)
    if (response.status === 200) {
        $('#overlay-message').text(`Добро пожаловать!`);
        $('#overlay-buttons').html('<button id="go-home">Вернуться на главную</button>').show();
    } else {
        let errorText = `Ошибка при регистрации: ${response.message}`;

        $('#overlay-message').text(errorText);
        $('#overlay-buttons').html('<button id="try-again">Попробовать позже</button>').show();
    }
}

// "Вернуться на главную"
$('#loading-overlay').on('click', '#go-home', function () {
    window.location.href = '/';
});

// Обработка кнопки "Попробовать позже" после неудачной попытки регистрации
$('#loading-overlay').on('click', '#try-again', function () {
    $('#loading-overlay').hide(); // Скрываем overlay
});

// при вводе в поля "пароль" и "введите пароль" сразу проверяется, совпадают ли они, или выводится ошибка.
$('#password, #password-repeat').on('input', checkPasswords);
