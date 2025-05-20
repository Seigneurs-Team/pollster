import { sendRequest } from "./api.js"
import { showLoadingOverlay, hideLoadingOverlay, showFailOverlay } from './utils/helpers.js';

$('#ban').click(() => {
    const userId = $('#ban-input').val()
    if (userId) {
        sendRequest(`/admin_panel/ban/${userId}`, 'POST').then(responseJson => {
            console.log('responseJson', responseJson)
            $('#ban-result').text(responseJson['responses'])
            $('#ban-result').removeClass('fail')

        }).catch(e => {
            $('#ban-result').text(e)
            $('#ban-result').addClass('fail')
        })
    } else {
        $('#ban-result').text('Введите id')
        $('#ban-result').addClass('fail')

    }
})

$('#unban').click(() => {
    const userId = $('#ban-input').val()
    if (userId) {
        sendRequest(`/admin_panel/unban/${userId}`, 'POST').then(responseJson => {
            console.log('responseJson', responseJson)
            $('#ban-result').text(responseJson['response'])
            $('#ban-result').removeClass('fail')

        }).catch(e => {
            $('#ban-result').text(e)
            $('#ban-result').addClass('fail')
        })
    } else {
        $('#ban-result').text('Введите id')
        $('#ban-result').addClass('fail')

    }
})


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
