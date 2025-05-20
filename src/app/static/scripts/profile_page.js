import { sendRequest } from './api.js';
import { showLoadingOverlay, hideLoadingOverlay, showFailOverlay } from './utils/helpers.js';


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

    // Настройки toastr для всплывающих окон при удалении аккаунта/опросов
    toastr.options = {
        positionClass: 'toast-top-center',
        closeButton: true,
        progressBar: true,
        newestOnTop: true,
        timeOut: 5000, // 5 секунд
        extendedTimeOut: 500,
        preventDuplicates: false,
        showMethod: 'fadeIn',
        hideMethod: 'fadeOut',
        tapToDismiss: false
    };
});


$(".log-out").on('click', async function () {
    sendRequest('/log_out', 'POST').then(() => {
        window.location.href = '/sign_in';
    }).catch((error) => {
        showFailOverlay(error)
    })
});


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

$(".share-poll").on('click', function () {
    const id = $(this).attr('data-poll');
    console.log('id', id)

    // Инициализируем хранилище, если его нет
    if (!localStorage.urlsQRs) {
        localStorage.urlsQRs = "{}";
    }
    const urlsQRs = JSON.parse(localStorage.urlsQRs);

    if (!urlsQRs[id]) {
        console.log('dont have', id, 'in cache')
        // Получаем данные и обрабатываем их асинхронно
        getUrlAndQR(id).then(res => {
            if (res) { // Проверяем, что res не undefined (если был catch)
                urlsQRs[id] = res;
                localStorage.urlsQRs = JSON.stringify(urlsQRs);
                showExistingQR(urlsQRs[id]);

            }
        });
    } else showExistingQR(urlsQRs[id]);

})

function showExistingQR(args) {
    const [url, qr_code] = args
    console.log('showing existing qr')
    // Создаем элемент <img> с jQuery и устанавливаем src
    const $qrCodeImage = $('<img>', {
        src: `data:image/png;base64,${qr_code}`,
        alt: 'QR-код опроса',
        class: 'qr-code'
    });

 // очищаем контейнер
    $('.qr-code-container').empty()

    // Вставляем изображение в контейнер
    $('.qr-code-container').append($qrCodeImage);
    $('.poll-link input').val(url)

    $('#overlay-share-poll').show();
}

// закрытие всплывающего окна по клику на overlay
$('#overlay-share-poll').click(function (e) {
    // Проверяем, был ли клик именно на overlay (а не на его дочерние элементы)
    if (e.target === this) {
        $(this).hide();
    }
});

// закрытие всплывающего окна по ESC
$(document).keyup(function (e) {
    if (e.key === "Escape") {
        $('#overlay-share-poll').hide();
    }
});

function getUrlAndQR(id) {
    showLoadingOverlay();
    return sendRequest(`/get_qr_code/${id}`, 'GET')
        .then((responseJSON) => {
            return [responseJSON.url_on_poll, responseJSON.qr_code];
        })
        .catch((error) => {
            console.log(error);
            showFailOverlay(error);
            return null; // Возвращаем null при ошибке
        })
        .finally(() => {
            hideLoadingOverlay();
        });
}

$(".delete-poll").on('click', async function () {
    // Останавливаем всплытие события, чтобы предотвратить переход по ссылке
    event.stopPropagation();
    event.preventDefault();

    const id = $(this).attr('data-poll');
    const pollItem = $(this).closest('.poll-item')

    // скрываем опрос
    pollItem.hide()

    delayedDeleting(() => {
        deletePoll(id, pollItem)
    }, 'Опрос будет удален', 3, pollItem);

})

function deletePoll(id, pollItem) {
    console.log('deleting poll...');

    sendRequest(`/delete_poll/${id}`, 'DELETE')
        .catch((error) => {
            showFailOverlay(error)
        })
}

$(".delete-account").on('click', async function () {
    delayedDeleting(deleteAccount, 'Ваш аккаунт будет удален', 5);
});

function deleteAccount() {
    console.log('deleting account...')
    sendRequest('/delete_account', 'DELETE').then(() => {
        window.location.href = '/sign_in';
    }).catch((error) => {
        showFailOverlay(error)
    })
}

// показать всплывающее окно "... будет удалено через ...с"
function delayedDeleting(fn, message, secondsLeft, pollItem = null) {

    // Генерируем уникальный ID для каждого toast
    const toastId = 'toast-' + Date.now() + '-' + Math.floor(Math.random() * 1000);

    // Создаем сообщение "Ваш аккаунт/опрос будет удален через ...с"
    const toastInner = genToastHtml(toastId, message, secondsLeft)

    showToast(toastId, toastInner, secondsLeft, fn, pollItem)
}

function genToastHtml(toastId, msg, secondsLeft) {
    return `
        <div id="${toastId}" class="toast-content">
            <img class="warning-img" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAGYSURBVEhL5ZSvTsNQFMbXZGICMYGYmJhAQIJAICYQPAACiSDB8AiICQQJT4CqQEwgJvYASAQCiZiYmJhAIBATCARJy+9rTsldd8sKu1M0+dLb057v6/lbq/2rK0mS/TRNj9cWNAKPYIJII7gIxCcQ51cvqID+GIEX8ASG4B1bK5gIZFeQfoJdEXOfgX4QAQg7kH2A65yQ87lyxb27sggkAzAuFhbbg1K2kgCkB1bVwyIR9m2L7PRPIhDUIXgGtyKw575yz3lTNs6X4JXnjV+LKM/m3MydnTbtOKIjtz6VhCBq4vSm3ncdrD2lk0VgUXSVKjVDJXJzijW1RQdsU7F77He8u68koNZTz8Oz5yGa6J3H3lZ0xYgXBK2QymlWWA+RWnYhskLBv2vmE+hBMCtbA7KX5drWyRT/2JsqZ2IvfB9Y4bWDNMFbJRFmC9E74SoS0CqulwjkC0+5bpcV1CZ8NMej4pjy0U+doDQsGyo1hzVJttIjhQ7GnBtRFN1UarUlH8F3xict+HY07rEzoUGPlWcjRFRr4/gChZgc3ZL2d8oAAAAASUVORK5CYII=">
            <div class="toast-message">
                ${msg} через <span class="countdown">${secondsLeft}</span>с
            </div>
            <button class="cancel-btn">Отменить</button>
        </div>
    `
}

function showToast(toastId, toastInner, secondsLeft, fn, pollItem) {

    toastr.warning(toastInner, '', {
        timeOut: secondsLeft * 1000,
        extendedTimeOut: 0, // Отключаем продление при наведении
        onShown: function () {
            // Запускаем обратный отсчет
            const countdownInterval = setInterval(function () {
                secondsLeft--;
                $(`#${toastId} .countdown`).text(secondsLeft);

                if (secondsLeft <= 0) {
                    clearInterval(countdownInterval);
                    fn(); // Вызываем функцию удаления
                    console.log('удаление прошло успешно!');
                }
            }, 1000);

            // Вешаем обработчик на кнопку "Отменить" конкретного toast
            $(`#${toastId} .cancel-btn`).on('click', function () {
                clearInterval(countdownInterval);
                // Получаем элемент toast через toastr API
                toastr.remove($(`#${toastId}`).closest('.toast')[0]);
                console.log('Удаление отменено');

                // если удалялся опрос, то снова показываем его
                if (pollItem) pollItem.show()
            });
        }
    });
}