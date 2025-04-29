// отправка опроса на сервер
const host = 'http://127.0.0.1:8000';
import { hasHTMLTags } from './create_poll_page.js';
import { sendRequest } from './api.js';


export function createPoll() {
    let questions = getQuestions()

    let tags = getTags()

    let pollData = {
        name_of_poll: $('#pollTitle').val(),
        description: $('#pollDescription').val(),
        tags: tags,
        private: $('#private').is(':checked'),
        questions: questions,
    };

    const coverImage = $('.addPollImage').data('base64') || null
    const defaultImage = $('input[name=default-image]:checked').val()

    if (coverImage) { // если пользователь загрузил картинку
        pollData.cover = coverImage.split(',')[1] // отделяем metadata
    } else if (defaultImage == 'no-image') { // если не выбран .default-image отправляем 0 - это значит что будет рандом картинка
        pollData.coverDefault = 0 
    }else if (defaultImage != 'no-image') { // если выбран .default-image
        pollData.coverDefault = defaultImage
    } 

    console.log("pollData:", pollData)

    // если введенные данные корректны, отправляем опрос на сервер
    if (checkCorrectData(pollData)) {
        sendCreatePollRequest(pollData);
    }
}

function getQuestions() {

    // Перебираем все элементы с классом .question и добавляем их данные в questions в виде js-объекта
    let questions = $('.question').map(function () {
        let type = $(this).attr('data-type')

        // если это вопрос с вариантами ответа, то извлекаем их. если нет, то options останется []
        if (type === 'radio' || type === 'checkbox') {
            return makeQuestionWithOptions(type)

        } else if (type === 'short text') { // если это вопрос с коротким ответом, то в rightAnswersId заносится единственный правильный ответ, если он был введен пользователем
            return makeShortTextQuestion(type, this)

        } else if (type === 'long text') { // если это вопрос с коротким ответом, то в rightAnswersId заносится единственный правильный ответ, если он был введен пользователем
            return makeLongTextQuestion(type, this)
        }

    }).get() // Преобразуем результат в массив

    return questions

}

function makeQuestionWithOptions(type) {
    let options = []

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
}

function makeShortTextQuestion(type, question) {
    let answer = $(question).find('.right-answer').val()

    return {
        id: $(question).attr('id'),
        type: type,
        text: $(question).find('.questionText').val(),
        rightAnswer: answer,
    }
}

function makeLongTextQuestion(type, question) {
    return {
        id: $(question).attr('id'),
        type: type,
        text: $(question).find('.questionText').val(),
    }
}

function getTags() {
    let tags = [];

    // Перебираем все элементы, у которых id начинается с "tag-"
    $('.selected-tags [id^="tag-"]').each(function () {
        tags.push($(this).text().trim()); // получаем текст тэга
    });

    console.log('tags: ', tags);
    return tags
}

function checkCorrectData(pollData) { // проверка на корректные данные в форме перед ее отправкой. 
    let isInvalid = false;
    let msg = ''
    if (!pollData.name_of_poll) {
        // если поле имени опроса пустое
        msg = 'Некорректно заполнена форма: Название опроса не может быть пустым!'
        isInvalid = true;

    } else if (!(pollData.tags.length)) {
        // если нет ни одного тэга
        msg = 'Некорректно заполнена форма: Вы не добавили ни одного тэга!'
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

async function sendCreatePollRequest(data) {
    const response = await sendRequest('/create_poll', 'POST', data);

    const responseJson = await response.json()
    console.log('responseJson:', responseJson)


    // Обработка ответа от сервера
    if (response.status === 200) {
        // Успешное создание опроса
        if ($('#private').is(':checked')) {
            showQR(responseJson.url, responseJson.qr_code)

        } else {
            alert('Опрос успешно создан')
            window.location.href = '/'; // Перенаправление на домашнюю страницу
        }
    }
}

function showQR(url, qr_code) {

    // Создаем элемент <img> с jQuery и устанавливаем src
    const $qrCodeImage = $('<img>', {
        src: `data:image/png;base64,${qr_code}`,
        alt: 'QR-код опроса',
        css: {
            maxWidth: '100%',
            height: 'auto'
        }
    });

    // Вставляем изображение в контейнер
    $('#qr-code-container').append($qrCodeImage);

    const $link = $('<a>', {
        href: `${url}`,
        text: url
    });
    $('#poll-link').append($link);

    $('#overlay-share-poll').show();
}