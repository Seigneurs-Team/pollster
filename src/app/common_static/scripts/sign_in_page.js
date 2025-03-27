// вход в аккаунт
import {getChallenge, findProof} from './POW.js';


const host = 'http://127.0.0.1:8000';

$('#loginForm').on('submit', async function (event) {
    event.preventDefault(); // предотвращает стандартное поведение формы

    // Получаем данные из формы
    let login = $('input[name="login"]').val();
    let password = $('input[name="password"]').val();

    // проверка данных формы: логин и пароль не пустые
    if (login && password) {

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

            let dataJSON = JSON.stringify({
                login: login,
                pow: nonce,
                password: password,
            })
            console.log('dataJSON', dataJSON)
            // отправляем dataJSON на сервер. там проверяется существование аккаунта, правильность пароля, и возвращается соответструющий результат.

            const response = await sendSignInRequest(dataJSON)
            console.log('response:', response)
// Обработка ответа от сервера
            if (response.response === 'ok') {
                // Успешная регистрация
                $('#overlay-message').text(`Добро пожаловать`);
                $('#overlay-buttons').html('<button id="go-home">Вернуться на главную</button>').show();
            } else {
                console.log('Ошибка при входе в аккаунт')
                // Ошибка регистрации
                let errorText = 'Ошибка при входе в аккаунт';

                $('#overlay-message').text(errorText);
                $('#overlay-buttons').html('<button id="try-again">Попробовать снова</button>').show();
            }
        } catch (error) {
            console.error('Ошибка:', error);
            $('#overlay-message').text('Произошла ошибка. Пожалуйста, попробуйте снова.');
            $('#overlay-buttons').html('<button id="try-again">Попробовать снова</button>').show();
        } finally {
            // Разблокируем форму
            $('#loginForm').find('input, button').prop('disabled', false);
        }
    } else {
        console.log('логин и пароль не могут быть пустыми') // TODO в html выводить
    }
});

async function sendSignInRequest(dataJSON) {
    console.log('sending signing in data...');
    const response = await fetch('/log_in', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        credentials: 'include', // Отправляем куки
        body: dataJSON,
    });
    const responseData = await response.json();
    console.log('Ответ сервера:', responseData); // Выводим ответ сервера в консоль

    if (!response.ok) {
        console.error('Ошибка при входе в аккаунт:', responseData);
        throw new Error('Ошибка при входе в аккаунт');
    }

    return responseData;
}

// Обработка кнопки "Вернуться на главную"
$('#loading-overlay').on('click', '#go-home', function () {
    window.location.href = '/'; // Перенаправление на главную страницу
});

// Обработка кнопки "Попробовать позже"
$('#loading-overlay').on('click', '#try-again', function () {
    $('#loading-overlay').hide(); // Скрываем overlay
});
