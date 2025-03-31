// вход в аккаунт
import {getChallenge, findProof} from './POW.js';
import {sendRequest} from './api.js';
import { setFooterBackground } from './utils.js';
setFooterBackground()

async function sendSignInRequest(data) {
    console.log('отправка даннных регистрации...')
    const response = await sendRequest('/log_in', 'POST', data);
console.log('response', response);
    // Обработка ответа от сервера
    if (response.status === 200) {
        // Успешная регистрация
        $('#overlay-message').text(`Добро пожаловать!`);
        $('#overlay-buttons').html('<button id="go-home">Вернуться на главную</button>').show();
    } else {
        // Ошибка регистрации
        let errorText = `Ошибка при регистрации: ${response.response}`;

        $('#overlay-message').text(errorText);
        $('#overlay-buttons').html('<button id="try-again">Попробовать позже</button>').show();
    }
}

const host = 'http://127.0.0.1:8000';

$('#loginForm').on('submit', async function (event) {
    event.preventDefault(); // предотвращает стандартное поведение формы

    // Получаем данные из формы
    let login = $('input[name="login"]').val();
    let password = $('input[name="password"]').val();


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

        let data = {
            login: login,
            pow: nonce,
            password: password,
        }

        await sendSignInRequest(data)
    } catch (error) {
        console.error('Ошибка:', error);
        $('#overlay-message').text('Произошла ошибка. Пожалуйста, попробуйте снова.');
        $('#overlay-buttons').html('<button id="try-again">Попробовать снова</button>').show();
    } finally {
        // Разблокируем форму
        $('#loginForm').find('input, button').prop('disabled', false);
    }

});

// Обработка кнопки "Вернуться на главную"
$('#loading-overlay').on('click', '#go-home', function () {
    window.location.href = '/'; // Перенаправление на главную страницу
});

// Обработка кнопки "Попробовать позже"
$('#loading-overlay').on('click', '#try-again', function () {
    $('#loading-overlay').hide(); // Скрываем overlay
});
