$('#loginForm').on('submit', function (event) {
    event.preventDefault(); // предотвращает стандартное поведение формы

    // Получаем данные из формы
    let login = $('input[name="login"]').val();
    let password = $('input[name="password"]').val();
    
    // проверка данных формы: логин и пароль не пустые
    if (login & password) {

        let dataJSON = JSON.stringify({
            login: login,
            password: password,
        })
        console.log('dataJSON', dataJSON)
        // отправляем dataJSON на сервер. там проверяется, есть ли уже пользователь с таким логином: если да, то возвращается соответствующий код ошибки, и я в if его нахожу и пишу alert(`пользователь с таким логином уже существует`); если нет, то alert(`добро пожаловать, {login}`). если какая-то другая ошибка (т.е. два if, потом else), то пишу ошибка, попробуйте снова

        

        /*
                const Http = new XMLHttpRequest();
        
                Http.open("POST", host + "/create_poll", true); // TODO вместо create_poll запрос на создание аккаунта
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
        console.log('логин и пароль не могут быть пустыми') // TODO пока что не alert. да и вообще лучше не alert, а в html выводить
    }

})