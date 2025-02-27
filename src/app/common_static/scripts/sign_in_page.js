// вход в аккаунт

const host = 'http://127.0.0.1:8000';

$('#loginForm').on('submit', function (event) {
    event.preventDefault(); // предотвращает стандартное поведение формы

    // Получаем данные из формы
    let login = $('input[name="login"]').val();
    let password = $('input[name="password"]').val();

    // проверка данных формы: логин и пароль не пустые
    if (login && password) {

        let dataJSON = JSON.stringify({
            login: login,
            password: password,
        })
        console.log('dataJSON', dataJSON)
        // отправляем dataJSON на сервер. там проверяется существование аккаунта, правильность пароля, и возвращается соответструющий результат.

        const response = sendSignInRequest(dataJSON)
        console.log('response:', response)
// Обработка ответа от сервера
        if (response.response === 'ok') {
            // Успешная регистрация
            $('#overlay-message').text(`Добро пожаловать, ${login}!`);
            $('#overlay-buttons').html('<button id="go-home">Вернуться на главную</button>').show();
        } else {
            // Ошибка регистрации
            let errorText = 'Ошибка при входе в аккаунт';

            $('#overlay-message').text(errorText);
            $('#overlay-buttons').html('<button id="try-again">Попробовать снова</button>').show();
        }
    } else {
        console.log('логин и пароль не могут быть пустыми') // TODO в html выводить
    }

})

async function sendSignInRequest(dataJSON) {
    console.log('sending registration data...');
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