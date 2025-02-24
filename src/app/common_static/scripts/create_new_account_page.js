$('#loginForm').on('submit', async function (event) {
    event.preventDefault(); // предотвращает стандартное поведение формы

    // Получаем данные из формы
    let login = $('input[name="login"]').val();
    let password = $('input[name="password"]').val();
    let passwordRepeat = $('input[name="password-repeat"]').val();
    let nickname = $('input[name="nickname"]').val();
    let errorMessage = $('#error-message');

    // проверка данных формы
console.log('!(login && password)', !(login && password))
    console.log('password !== passwordRepeat', password !== passwordRepeat)
    if (!(login && password)) {
        // Если логин или пароль пустые, показываем сообщение об ошибке
        errorMessage.text('Логин и пароль не могут быть пустыми!')
    } else if (password !== passwordRepeat) {
        // Если пароли не совпадают, показываем сообщение об ошибке
        errorMessage.text('Пароли не совпадают!')
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
            // отправляем dataJSON на сервер. там проверяется, есть ли уже пользователь с таким логином: если да, то возвращается соответствующий код ошибки, и я в if его нахожу и пишу alert(`пользователь с таким логином уже существует`); если нет, то alert(`добро пожаловать, {login}`). если какая-то другая ошибка (т.е. два if, потом else), то пишу ошибка, попробуйте снова
            // Обработка ответа от сервера
            if (response.success) {
                // Успешная регистрация
                $('#overlay-message').text(`Добро пожаловать, ${login}!`);
                $('#overlay-buttons').html('<button id="go-home">Вернуться на главную</button>').show();
            } else {
                // Ошибка регистрации
                $('#overlay-message').text(response.message || 'Ошибка при регистрации');
                $('#overlay-buttons').html('<button id="try-again">Попробовать позже</button>').show();
            }
        } catch (error) {
            console.error('Ошибка:', error);
            $('#overlay-message').text('Произошла ошибка. Пожалуйста, попробуйте снова.');
            $('#overlay-buttons').html('<button id="try-again">Попробовать позже</button>').show();
        } finally {
            // Разблокируем форму
            $('#loginForm').find('input, button').prop('disabled', false);
        }
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


// Шаг 1: Получить challenge от бэкенда
async function getChallenge() {
    // Установка куки
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
            count ++;
        }
    }
}

// Шаг 3: Отправить данные регистрации на сервер
async function sendRegistrationRequest(dataJSON) {
    console.log('sending registration data...')
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
