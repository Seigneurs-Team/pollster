import { getChallenge, findProof } from './/utils/POW.js';
import { sendRequest } from './api.js';
import { blockForm, unblockForm, showSuccessOverlay, showFailOverlay } from './utils/authHelpers.js';
let errorMessage = $('#error-message');


$('#loginForm').on('submit', async function (event) {
    event.preventDefault()

    // Блокируем форму, Показываем индикатор загрузки
    blockForm()

    let [login, password, nickname] = getRegistrationFormData()

    // Находим nonce
    const challenge = await getChallenge();
    const nonce = await findProof(challenge);

    // Формируем JSON с данными для регистрации
    let data = {
        login: login,
        password: password,
        pow: nonce,
        nickname: nickname,
    }
    console.log('data', data);

    // Отправляем данные на сервер
    sendRequest('/register', 'POST', data)
        .then(() => {
            showSuccessOverlay()
        })
        .catch((error) => {
            showFailOverlay(error)
        })
        .finally(() => {
            unblockForm()
        })
});


function getRegistrationFormData() {
    // Получаем данные из формы
    let login = $('input[name="login"]').val();
    let password = $('input[name="password"]').val();
    let nickname = $('input[name="nickname"]').val();
    return [login, password, nickname]
}

// при вводе в поля "пароль" и "введите пароль" сразу проверяется, совпадают ли они, или выводится ошибка.
$('#password, #password-repeat').on('input', checkPasswords);

// Функция для проверки совпадения паролей TODO сделать debounce, чтобы раз в полсекунды где-то проверялось
function checkPasswords() {
    let password = $('input[name="password"]').val();
    let passwordRepeat = $('input[name="password-repeat"]').val();

    if (password === passwordRepeat) {
        errorMessage.text('');
    } else {
        errorMessage.text('Пароли не совпадают!');
    }
}
