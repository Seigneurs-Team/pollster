import {getChallenge, findProof} from './POW.js';

let errorMessage = $('#error-message');
console.log(errorMessage);

$('#loginForm').on('submit', async function (event) {
    event.preventDefault(); // предотвращает стандартное поведение формы

    // Получаем данные из формы
    let login = $('input[name="login"]').val();
    let password = $('input[name="password"]').val();
    let passwordRepeat = $('input[name="password-repeat"]').val();
    let nickname = $('input[name="nickname"]').val();

    // проверка данных формы
    if (!(login && password)) {
        errorMessage.text('Логин и пароль не могут быть пустыми!');
    } else if (!isValidEmail(login)) {
        errorMessage.text('Некорректный формат почты!');
    } else if (password !== passwordRepeat) {
        errorMessage.text('Пароли не совпадают!');
    } else {
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
            let dataJSON = JSON.stringify({
                login: login,
                password: password,
                pow: nonce,
                nickname: nickname,
            });
            console.log('dataJSON', dataJSON);

            // Шаг 4: Отправляем данные на сервер
            const response = await sendRegistrationRequest(dataJSON);

            // Обработка ответа от сервера
            if (response.response === 200) {
                // Успешная регистрация
                $('#overlay-message').text(`Добро пожаловать, ${login}!`);
                $('#overlay-buttons').html('<button id="go-home">Вернуться на главную</button>').show();
            } else {
                // Ошибка регистрации
                let errorText = `Ошибка при регистрации: ${response.message}`;

                $('#overlay-message').text(errorText);
                $('#overlay-buttons').html('<button id="try-again">Попробовать позже</button>').show();
            }
        } catch (error) {
            console.error('Ошибка:', error);
            $('#overlay-message').text('Произошла ошибка. Пожалуйста, попробуйте снова.');
            $('#overlay-buttons').html('<button id="try-again">Попробовать снова</button>').show();
        } finally {
            // Разблокируем форму
            $('#loginForm').find('input, button').prop('disabled', false);
        }
    }
});

// Шаг 3: Отправить данные регистрации на сервер
async function sendRegistrationRequest(dataJSON) {
    console.log('sending registration data...');
    const response = await fetch('/register', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        credentials: 'include', // Отправляем куки
        body: dataJSON,
    });

    const responseData = await response.json();
    console.log('Ответ сервера:', responseData); // Выводим ответ сервера в консоль

    if (!response.ok) {
        console.error('Ошибка при регистрации:', responseData);
        throw new Error('Ошибка при регистрации');
    }

    return responseData;
}

// Функция для проверки совпадения паролей
function checkPasswords() {
    let password = $('input[name="password"]').val();
    let passwordRepeat = $('input[name="password-repeat"]').val();

    if (password === passwordRepeat) {
        // Если пароли совпадают, очищаем сообщение об ошибке
        errorMessage.text('');
    } else {
        // Если пароли не совпадают, показываем сообщение об ошибке
        errorMessage.text('Пароли не совпадают!');
    }
}

// Функция для проверки формата почты
function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

$(document).ready(function () {
    // Обработка кнопки "Вернуться на главную"
    $('#loading-overlay').on('click', '#go-home', function () {
        window.location.href = '/'; // Перенаправление на главную страницу
    });

// Обработка кнопки "Попробовать позже"
    $('#loading-overlay').on('click', '#try-again', function () {
        $('#loading-overlay').hide(); // Скрываем overlay
    });

    // Добавляем обработчики событий на поля ввода
    $('#password, #password-repeat').on('input', checkPasswords);

});