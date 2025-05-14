// отправка опроса на сервер
const host = 'http://127.0.0.1:8000';
import { hasHTMLTags } from './create_poll_page.js';
import { sendRequest } from './api.js';
import { showLoadingOverlay, hideLoadingOverlay, showFailOverlay, showCreatedQR } from './utils/helpers.js';

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
    } else if (defaultImage != 'no-image') { // если выбран .default-image
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
    const questions = $('.question').map((idx, question) => {
        const type = $(question).attr('data-type')

        // если это вопрос с вариантами ответа, то извлекаем их. если нет, то options останется []
        if (type === 'radio' || type === 'checkbox') {
            return makeQuestionWithOptions(type, question)

        } else if (type === 'short text') { // если это вопрос с коротким ответом, то в rightAnswersId заносится единственный правильный ответ, если он был введен пользователем
            return makeShortTextQuestion(type, question)

        } else if (type === 'long text') {
            return makeLongTextQuestion(type, question)
        }

    }).get() // Преобразуем результат в массив

    return questions

}

function makeQuestionWithOptions(type, question) {
    let options = []

    let rightAnswersId = []

    // id ответов начинаются с 0
    let counter = -1
    $(question).find('.option').each((idx, option) => {
        // Извлекаем значение из input.value, убираем пробелы в начале и в конце
        let value = $(option).find('.value').val().trim();
        // Если значение не пустое, добавляем его в массив options
        if (value) {
            options.push(value);
            counter++
        }
        if ($(option).find('.check').is(':checked')) {
            rightAnswersId.push(counter);
        }
    });

    return {
        id: $(question).attr('id'),
        type: type,
        text: $(question).find('.questionText').val(),
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
    $('.selected-tags [id^="tag-"]').each((idx, tag) => {
        tags.push($(tag).text().trim()); // получаем текст тэга
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
        $(`.questions input[type="text"], .questions textarea`).each((idx, input) => {
            const value = $(input).val();
            if (!value.trim() && $(input).attr('class') !== 'right-answer') {
                isInvalid = true;
                msg = 'Некорректно заполнена форма: Пустые поля!'
                return false;
            }
        })

        $(`input[type="text"], textarea`).each((idx, input) => {
            const value = $(input).val();
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

    showLoadingOverlay()
    sendRequest('/create_poll', 'POST', data)
        .then((responseJSON) => {
            if ($('#private').is(':checked')) {
                showCreatedQR(responseJSON.url, responseJSON.qr_code)

                // кэширование qr кода. пока закомментировано, т.к. responseJSON.id не существует
                /*
                const urlsQRs = JSON.parse(localStorage.urlsQRs);

                urlsQRs[id] = [responseJSON.url, responseJSON.qr_code];
                localStorage.urlsQRs = JSON.stringify(urlsQRs);
                showExistingQR(urlsQRs[responseJSON.id]);
                */
            } else {
                showSuccessOverlay()
            }
        })
        .catch((error) => {
            showFailOverlay(error)
        })
        .finally(() => {
            hideLoadingOverlay()
        })
}

function showSuccessOverlay() {
    $('#overlay-success').show();
}