// вход в аккаунт
import { getChallenge, findProof } from './/utils/POW.js';
import { sendRequest } from './api.js';


async function sendSignInRequest(data) {
    console.log('отправка даннных регистрации...')
    const response = await sendRequest('/log_in', 'POST', data);
    const responseData = await response.json();
    console.log('Ответ сервера:', responseData);
    // Обработка ответа от сервера
    if (responseData.response == 'ok') {
        // Успешная регистрация
        $('#overlay-message').text(`Добро пожаловать!`);
        $('#overlay-buttons').html('<button id="go-home">Вернуться на главную</button>').show();
    } else {
        let errorText = `Ошибка при входе в аккаунт: ${responseData.response}`;

        $('#overlay-message').text(errorText);
        $('#overlay-buttons').html('<button id="try-again">Попробовать позже</button>').show();
    }
}

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
