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

        // отправляем dataJSON на сервер. там проверяется, есть ли уже пользователь с таким логином: если да, то возвращается соответствующий код ошибки, и я в if его нахожу и пишу alert(`пользователь с таким логином уже существует`); если нет, то alert(`добро пожаловать, {login}`). если какая-то другая ошибка (т.е. два if, потом else), то пишу ошибка, попробуйте снова
        console.log('data', data)
    }
    else {
        console.log('логин и пароль не могут быть пустыми') // TODO пока что не alert. да и вообще лучше не alert, а в html выводить
    }

})