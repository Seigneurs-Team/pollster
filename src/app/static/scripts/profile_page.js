import {sendRequest} from './api.js';


async function sendChangeDataRequest(data, url) {
    return sendRequest(`/change_user_data/${url}`, 'POST', data);
}


async function sendDeletePollRequest( id) {
    return sendRequest(`/delete_poll/${id}`, 'GET');
}


let tagsErrorMessage = $('#tags-error-message');
let errorMessage = $('.error-message');

$("#your-polls-btn").on('click', function (event) {
    openTab(event, 'your-polls');
});
$("#completed-polls-btn").on('click', function (event) {
    openTab(event, 'completed-polls');
});
$(".log-out").on('click', async function () {
    console.log('sending log out request...');
    const response = await fetch('/log_out', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        credentials: 'include', // Отправляем куки
    });
    const responseData = await response.json();
    console.log('Ответ сервера:', responseData); // Выводим ответ сервера в консоль

    if (response.status!== 200) {
        alert('Ошибка при выходе из аккаунта:', responseData)
        console.error('Ошибка при выходе из аккаунта:', responseData);
        throw new Error('Ошибка при выходе из аккаунта');
    } else {
        window.location.href = '/sign_in';
    }
});

$(".delete-account").on('click', async function () {
    console.log('sending delete account request...');
    const response = await fetch('/delete_account', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        credentials: 'include', // Отправляем куки
    });
    const responseData = await response.json();
    console.log('Ответ сервера:', responseData); // Выводим ответ сервера в консоль

    if (response.status!== 200) {
        alert('Ошибка при удалении аккаунта:', 'responseData')
        console.error('Ошибка при удалении аккаунта:', responseData);
        throw new Error('Ошибка при удалении аккаунта');
    } else {
        window.location.href = '/sign_in';
    }
});


function openTab(event, tabName) {
    // Hide all elements with class "tabcontent"
    $(".tabcontent").hide();

    // Remove "active" class from all elements with class "tablinks"
    $(".tablinks").removeClass("active");

    // Show the current tab, and add an "active" class to the button that opened the tab
    $(`#${tabName}`).show();
    $(event.currentTarget).addClass("active");
}

$(document).ready(function () {
    // по умолчанию вкладка "ваши опросы"
    $("#your-polls-btn").addClass("active");
    $("#your-polls").show()
})

$(".delete-poll").on('click', async function () {
    // Останавливаем всплытие события, чтобы предотвратить переход по ссылке
    event.stopPropagation();
    event.preventDefault();
    console.log('deleting poll...');
    const id = $(this).attr('data-poll');
    

    const response = await sendDeletePollRequest(id)
    const responseData = await response.json();
    console.log('Ответ сервера:', responseData); // Выводим ответ сервера в консоль

    if (response.status!== 200) {
        console.error('Ошибка при удалении опроса:', responseData);
        throw new Error('Ошибка при удалении опроса');
    } else {
        // если опрос успешно удален - скрываем его
        $(this).closest('.poll-item').hide()
    }

    return responseData;
})

$('.tag').click(function () {
    // Проверяем, где находится текущий элемент
    if ($(this).parent().hasClass('selected-tags')) {
        // Если элемент в .selected-tags, перемещаем его в .not-selected-tags
        $(this).appendTo('.not-selected-tags');
        tagsErrorMessage.hide()
    } else if ($('.selected-tags').children().length > 3) {
        console.log('>4 тэгов нельзя')
        tagsErrorMessage.show()
    } else if ($(this).parent().hasClass('not-selected-tags')) {
        // Если элемент в .not-selected-tags, перемещаем его в .selected-tags
        $(this).appendTo('.selected-tags');
        tagsErrorMessage.hide()
    }
});

let initialUserData = {};

$(document).ready(function () {
    // Сохраняем исходные данные при загрузке
    initialUserData = {
        nickname: $('input[name="edit_name_input"]').val().trim(),
        email: $('#email').val().trim(),
        number_of_phone: $('#phone').val().trim(),
        dateOfBirth: $('#date-of-birth').val().trim(),
        tags_of_user: $('.selected-tags .tag').map(function () {
            return $(this).text().trim();
        }).get()
    };

    $('.about-you input').removeAttr('disabled')

    
});

$('.save-changes').on('click', async function (event) {
    event.preventDefault();
    const errorMessages = [];

    // Собираем текущие данные
    const currentData = {
        nickname: $('input[name="edit_name_input"]').val().trim(),
        email: $('#email').val().trim(),
        number_of_phone: $('#phone').val().trim(),
        dateOfBirth: $('#date-of-birth').val().trim(),
        tags_of_user: $('.selected-tags .tag').map(function () {
            return $(this).text().trim();
        }).get()
    };

    // Валидация обязательных полей
    if (!currentData.nickname) errorMessages.push('Имя пользователя обязательно');
    if (!currentData.email) errorMessages.push('Email обязателен');
    if (!isValidEmail(currentData.email)) errorMessages.push('Неверный формат email');
    // if (currentData.number_of_phone && !isValidPhone(currentData.number_of_phone)) errorMessages.push('Неверный формат телефона');

    if (errorMessages.length > 0) {
        alert(errorMessages.join('\n'));
        errorMessage.text(errorMessages.join('\n'));
        return;
    }

    // Определяем измененные поля
    const changes = {};
    if (currentData.nickname !== initialUserData.nickname) changes.nickname = currentData.nickname;
    if (currentData.email !== initialUserData.email) changes.email = currentData.email;
    if (currentData.number_of_phone !== initialUserData.number_of_phone) changes.number_of_phone = currentData.number_of_phone;
    if (currentData.dateOfBirth !== initialUserData.dateOfBirth) changes.date_of_birth = currentData.dateOfBirth;
    if (!arraysEqual(currentData.tags_of_user, initialUserData.tags_of_user)) changes.tags_of_user = currentData.tags_of_user;

    // Отправка изменений для каждого поля
    for (const [field, value] of Object.entries(changes)) {
        try {
            console.log(`{${field}: ${value}}`)
            const data = {[field]: value}

            const response = await sendChangeDataRequest(data, field);
            console.log('response: ', response)
            if (response.status === 200) {
                initialUserData[field] = value; // Обновляем исходные данные
                console.log(`${field}: ${value} successfully!`)

            } else {
                throw new Error(response.message || 'Ошибка сохранения');
            }
        } catch (error) {
            console.error(`Ошибка при сохранении ${field}:`, error);
            alert(`Ошибка: ${error.message}`);
            return;
        }
    }

    alert('Изменения сохранены!');
});

// Вспомогательные функции
function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function isValidPhone(phone) {
    return /^(\+7|8)?[\d]{10}$/.test(phone);
}

function arraysEqual(a, b) {
    return a.length === b.length && a.every((v, i) => v === b[i]);
}
