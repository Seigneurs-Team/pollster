$('#loginForm').on('submit', async function (event) {
    event.preventDefault(); // предотвращает стандартное поведение формы

    // Получаем данные из формы
    let login = $('input[name="login"]').val();
    let password = $('input[name="password"]').val();
    let passwordRepeat = $('input[name="password-repeat"]').val();
    let nickname = $('input[name="nickname"]').val();
    let errorMessage = $('#error-message');

    // проверка данных формы

    if (!(login && password)) {
        // Если логин или пароль пустые, показываем сообщение об ошибке
        errorMessage.text('Логин и пароль не могут быть пустыми!')
    } else if (password != passwordRepeat) {
        // Если пароли не совпадают, показываем сообщение об ошибке
        errorMessage.text('Пароли не совпадают!')
    } else {
        // Если пароли совпадают, очищаем сообщение об ошибке
        errorMessage.text('');
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
// отправляем dataJSON на сервер. там проверяется, есть ли уже пользователь с таким логином: если да, то возвращается соответствующий код ошибки, и я в if его нахожу и пишу alert(`пользователь с таким логином уже существует`); если нет, то alert(`добро пожаловать, {login}`). если какая-то другая ошибка (т.е. два if, потом else), то пишу ошибка, попробуйте снова
            // Обработка ответа от сервера
            if (response.success) {
                alert(`Добро пожаловатьЫ, ${login}`);
                // window.location.href = '/'; // Перенаправление на домашнюю страницу
            } else {
                alert(response.message || 'Ошибка при регистрации');
            }
        } catch (error) {
            console.error('Ошибка:', error);
            alert('Произошла ошибка. Пожалуйста, попробуйте снова.');
        }
    }
});

// Шаг 1: Получить challenge от бэкенда
async function getChallenge() {
    // Установка куки
    document.cookie = "auth_sessionid=some_random_value; path=/;";
    console.log('getting challenge...');

    const response = await fetch('/get_challenge', {
        method: 'GET',
        credentials: 'include', // Отправляем куки
    });

    if (!response.ok) {
        throw new Error('Ошибка при получении challenge');
    }

    const data = await response.json();
    console.log('Challenge received:', data);
    return data;
}

// Шаг 2: Найти nonce
async function findProof(challenge) {
    let count = 0;
    const difficulty = challenge.count_of_bits;

    while (true) {
        const stringForHash = `${challenge.version}:${challenge.count_of_bits}:${challenge.timestamp}:${challenge.resource}:${challenge.extension}:${challenge.random_string}:${count}`;
        const hashValue = sha256(stringForHash); // Используй библиотеку для SHA-256

        if (hashValue.startsWith('0'.repeat(difficulty))) {
            console.log('Nonce found:', count);
            return count;
        } else {
            count++;
            await new Promise(resolve => setTimeout(resolve, 0)); // Асинхронная задержка
        }
    }
}

// Шаг 3: Отправить данные регистрации на сервер
async function sendRegistrationRequest(dataJSON) {
    const response = await fetch('/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'include', // Отправляем куки
        body: dataJSON,
    });

    if (!response.ok) {
        throw new Error('Ошибка при отправке данных регистрации');
    }

    return await response.json();
}

$(document).ready(function () {
    let errorMessage = $('#error-message');

    // Функция для проверки совпадения паролей
    function checkPasswords() {
        let password = $('input[name="password"]').val();
        let passwordRepeat = $('input[name="password-repeat"]').val();

        if (password === passwordRepeat) {
            // Если пароли совпадают, очищаем сообщение об ошибке
            errorMessage.text('')
        } else {
            // Если пароли не совпадают, показываем сообщение об ошибке
            errorMessage.text('Пароли не совпадают!')
        }
    }

    // Добавляем обработчики событий на поля ввода
    $('#password, #password-repeat').on('input', checkPasswords);
});