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


        /*
                const Http = new XMLHttpRequest();
        
                Http.open("POST", host + "/create_poll", true); // TODO вместо create_poll запрос на вход в аккаунт
                Http.setRequestHeader("Content-Type", "application/json");
                Http.send(jsonPollData);
        
                Http.onload = function () {
                    var response = JSON.parse(Http.response);
                    console.log('result: ', response);
                    if (response) {
                        alert(`Добро пожаловать,` + login)
                        window.location.href = '/'; // Перенаправление на домашнюю страницу
                    }
        */

    }
    else {
        console.log('логин и пароль не могут быть пустыми') // TODO в html выводить
    }

})