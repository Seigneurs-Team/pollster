import { sendRequest } from './api.js';
import { showFailOverlay } from './utils/authHelpers.js';


let tagsErrorMessage = $('#tags-error-message');
let errorMessage = $('.error-message');

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

    // по умолчанию открыта вкладка "ваши опросы"
    $("#your-polls-btn").addClass("active");
    $("#your-polls").show()
});


$(".log-out").on('click', async function () {
    sendRequest('/log_out', 'POST').then(() => {
        window.location.href = '/sign_in';
    }).catch((error) => {
        showFailOverlay(error)
    })
});

$(".delete-account").on('click', async function () {
    sendRequest('/delete_account', 'DELETE').then(() => {
        window.location.href = '/sign_in';
    }).catch((error) => {
        showFailOverlay(error)
    })
});

$(".delete-poll").on('click', async function () {
    // Останавливаем всплытие события, чтобы предотвратить переход по ссылке
    event.stopPropagation();
    event.preventDefault();
    console.log('deleting poll...');

    const id = $(this).attr('data-poll');

    sendRequest(`/delete_poll/${id}`, 'DELETE')
        .then(() => {
            // если опрос успешно удален - скрываем его
            $(this).closest('.poll-item').hide()
        })
        .catch((error) => {
            showFailOverlay(error)
        })

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


$('.save-changes').on('click', async function (event) {
    event.preventDefault();
    const errorMessages = [];

    // Собираем текущие данные
    const currentData = getFormData()

    // Валидация обязательных полей
    if (!currentData.nickname) errorMessages.push('Имя пользователя обязательно');
    if (!currentData.email) errorMessages.push('Email обязателен');
    if (!isValidEmail(currentData.email)) errorMessages.push('Неверный формат email');
    // if (currentData.number_of_phone && !isValidPhone(currentData.number_of_phone)) errorMessages.push('Неверный формат телефона');

    if (errorMessages.length > 0) {
        alert(errorMessages.join('\n'));
        errorMessage.text(errorMessages.join('\n'));
        return;
    } else {
        // Определяем измененные поля
        const changes = findChanges(initialUserData, currentData)

        changeDataRequests(changes)
    }

})

function getFormData() {
    return {
        nickname: $('input[name="edit_name_input"]').val().trim(),
        email: $('#email').val().trim(),
        number_of_phone: $('#phone').val().trim(),
        dateOfBirth: $('#date-of-birth').val().trim(),
        tags_of_user: $('.selected-tags .tag').map(function () {
            return $(this).text().trim();
        }).get()
    };
}

function findChanges(initialUserData, currentData) {
    const changes = {};
    if (currentData.nickname !== initialUserData.nickname) changes.nickname = currentData.nickname;
    if (currentData.email !== initialUserData.email) changes.email = currentData.email;
    if (currentData.number_of_phone !== initialUserData.number_of_phone) changes.number_of_phone = currentData.number_of_phone;
    if (currentData.dateOfBirth !== initialUserData.dateOfBirth) changes.date_of_birth = currentData.dateOfBirth;
    if (!arraysEqual(currentData.tags_of_user, initialUserData.tags_of_user)) changes.tags_of_user = currentData.tags_of_user;
    return changes
}

function changeDataRequests(changes) {

    // Отправка изменений для каждого поля
    for (const [field, value] of Object.entries(changes)) {

        const data = { [field]: value }

       sendRequest(`/change_user_data/${field}`, 'POST', data).then(() => {
            initialUserData[field] = value; // Обновляем исходные данные
            console.log(`'${field}: ${value}' changed successfully!`)
            alert('Изменения сохранены!'); // TODO сделать вывод где-то под div-ом с данными
        })
            .catch((error) => {
                showFailOverlay(error)
            })
    }
}


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

$("#your-polls-btn").on('click', (e) => openTab(e, 'your-polls'))

$("#completed-polls-btn").on('click', (e) => openTab(e, 'completed-polls'))

function openTab(event, tabName) {
    // Hide all elements with class "tabcontent"
    $(".tabcontent").hide();

    // Remove "active" class from all elements with class "tablinks"
    $(".tablinks").removeClass("active");

    // Show the current tab, and add an "active" class to the button that opened the tab
    $(`#${tabName}`).show();
    $(event.currentTarget).addClass("active");
}