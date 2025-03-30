// отправка опроса на сервер
const host = 'http://127.0.0.1:8000';
import {hasHTMLTags} from './create_poll_page.js';
import { sendRequest } from './api.js';

async function sendCreatePollRequest(data) {
    const response = await sendRequest('/create_poll', 'POST', data);
    console.log('response:', response)
    console.log('response.status === 200', response.status === 200)
    // Обработка ответа от сервера
    if (response.status === 200) {
        // Успешное создание опроса
        alert('Опрос успешно создан')
        window.location.href = '/'; // Перенаправление на домашнюю страницу
    }
}


export function createPoll() {

    // Перебираем все элементы с классом .question и добавляем их данные в questions в виде js-объекта
    let questions = $('.question').map(function () {
        let type = $(this).attr('data-type')
        let options = []

        // если это вопрос с вариантами ответа, то извлекаем их. если нет, то options останется []
        if (type === 'radiobutton' || type === 'checkbox') {
            let rightAnswersId = []

            // id ответов начинаются с 0
            let counter = -1
            $(this).find('.option').each(function () {
                // Извлекаем значение из input.value, убираем пробелы в начале и в конце
                let value = $(this).find('.value').val().trim();
                // Если значение не пустое, добавляем его в массив options
                if (value) {
                    options.push(value);
                    counter++
                }
                if ($(this).find('.check').is(':checked')) {
                    rightAnswersId.push(counter);
                    // записывать буду порядковый номер правильных ответов, который возьму в качестве id. лучше использовать id, чем сравнение строк
                }
            });

            return {
                id: $(this).attr('id'),
                type: type,
                text: $(this).find('.questionText').val(),
                options: options,
                rightAnswersId: rightAnswersId,
            }
        } else if (type === 'short text') { // если это вопрос с коротким ответом, то в rightAnswersId заносится единственный правильный ответ, если он был введен пользователем
            let answer = $(this).find('.right-answer').val()
            
            return {
                id: $(this).attr('id'),
                type: type,
                text: $(this).find('.questionText').val(),
                rightAnswer: answer,
            }
        } else if (type === 'long text') { // если это вопрос с коротким ответом, то в rightAnswersId заносится единственный правильный ответ, если он был введен пользователем

            return {
                id: $(this).attr('id'),
                type: type,
                text: $(this).find('.questionText').val(),
            }
        }


    }).get() // Преобразуем результат в массив

    let tags = [];

    // Перебираем все элементы, у которых id начинается с "tag-"
    $('.selected-tags [id^="tag-"]').each(function () {
        tags.push($(this).text().trim()); // получаем текст тэга
    });

    // Выводим массив tags в консоль для проверки
    console.log('tags: ', tags);
    // Собираем данные
    let pollData = {
        name_of_poll: $('#pollTitle').val(),
        description: $('#pollDescription').val(),
        tags: tags,
        questions: questions,
    };
    console.log("pollData:", pollData)

    // если введенные данные корректны, отправляем опрос на сервер
    if (checkCorrectData(pollData)) {
        sendCreatePollRequest(pollData);
    }
}

function checkCorrectData(pollData) { // проверка на корректные данные в форме перед ее отправкой. пока что тут только проверка на пустое название. TODO сделать проверку на ненулевое количество вопросов, на ненулевое количество вариантов ответа в radio и checkbox. не непустой текст вопросов
    let isInvalid = false;
    let msg = ''
    if (!pollData.name_of_poll) {
        // если поле имени опроса пустое
        msg = 'Некорректно заполнена форма: Название опроса не может быть пустым!'
        isInvalid = true;

    } else if (!(pollData.questions.length)) {
        // если нет ни одного вопроса
        msg = 'Некорректно заполнена форма: Вы не добавили ни одного вопроса!'
        isInvalid = true;

    } else {
        // Проверяем все текстовые поля на 1) не пустоту 2) наличие html тэгов
        $(`.questions input[type="text"], .questions textarea`).each(function () {
            const value = $(this).val();
            if (!value.trim() && $(this).attr('class') !== 'right-answer') {
                isInvalid = true;
                msg = 'Некорректно заполнена форма: Пустые поля!'
                return false;
            }
        })

        $(`input[type="text"], textarea`).each(function () {
            const value = $(this).val();
            if (hasHTMLTags(value)) {
                isInvalid = true;
                msg = 'Некорректно заполнена форма: Недопустимые символы (например, < или >)!'
                return false;
            }
        });
    }

    if (isInvalid) {
        $('.error-message.submit').text(msg).show()
        console.log(msg)
        return false

    } else {
        $('.error-message.submit').hide()
        return true
    }
}
