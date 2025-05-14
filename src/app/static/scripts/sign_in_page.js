// вход в аккаунт
import { getChallenge, findProof } from './/utils/POW.js';
import { sendRequest } from './api.js';
import { blockForm, unblockForm, showSuccessOverlay, showFailOverlay } from './utils/helpers.js';

$('#loginForm').on('submit', async function (event) {
    event.preventDefault(); // предотвращает стандартное поведение формы

    let [login, password,] = getLogInFormData()

    blockForm()

    // Находим nonce
    const challenge = await getChallenge();
    const nonce = await findProof(challenge);

    let data = {
        login: login,
        pow: nonce,
        password: password,
    }

    sendRequest('/log_in', 'POST', data)
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


function getLogInFormData() {
    // Получаем данные из формы
    let login = $('input[name="login"]').val();
    let password = $('input[name="password"]').val();
    return [login, password]
}