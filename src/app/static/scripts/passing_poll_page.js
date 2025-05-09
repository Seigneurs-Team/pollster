import { sendRequest } from './api.js';


const questionsDiv = $("#questions");
let questionsList = []
// Инициализация при загрузке документа
$(document).ready(function () {
    renderAllQuestions();
    setupEventListeners();
});

// Отрисовка всех вопросов
function renderAllQuestions() {

    questionsList = JSON.parse(localStorage.getItem('questionsList'));

    questionsList.forEach(question => {
        const questionEl = $(`<div id="${question.id}" class="question"></div>`);
        const questionText = $(`<p class="question-text">${question.text}</p>`);
        const questionContent = answerType(question.type, question.id, question);

        questionEl.append(questionText, questionContent);
        questionsDiv.append(questionEl);
    });
}

// Настройка обработчиков событий
function setupEventListeners() {
    $(".start").on('click', handleStartButtonClick);
    $(".submit").on('click', (e) => {
        e.preventDefault();
        handleSubmitButtonClick(e)
    });
}

// Обработка клика на кнопку "Прохождение опроса"
function handleStartButtonClick() {
    $('form').show();
    $(this).hide();
}

// Генерация содержимого вопроса по типу
function answerType(questionType, questionId, question) {
    switch (questionType) {
        case "short text":
            return '<input class="answerShort" type="text" maxlength="60" placeholder="Короткий ответ">';

        case "long text":
            return '<textarea class="answerLong" type="text" rows="5" maxlength="700" placeholder="Развернутый ответ">';

        case "radio":
        case "checkbox":
            return renderOptions(questionType, questionId, question);

        case "radio img":
        case "checkbox img":
            // TODO: реализовать вопросы с изображениями
            return $();

        default:
            return $();
    }
}

// Отрисовка вариантов ответов
function renderOptions(type, questionId, question) {
    const options = $(`<div class="options"></div>`);
    let counter = 0;

    question.options.forEach(option => {
        options.append(addOption(type, questionId, option, counter));
        counter++;
    });

    return options;
}

// Генерация HTML для варианта ответа
function addOption(type, questionId, option, counter) {
    const inputType = type === "radio" ? "radio" : "checkbox";
    const id = `${questionId}_${counter}`;

    return $(`
        <div class="option">
            <input type="${inputType}" name="${questionId}" id="${id}" class="check">
            <label for="${id}">${option}</label>
        </div>
    `);
}

// Обработка отправки результатов
async function handleSubmitButtonClick(event) {
    console.log('hi from handleSubmitButtonClick')
    const poll_id = $(event.currentTarget).attr('data-poll-id');
    const results = {
        poll_id: poll_id,
        answers: collectAnswers()
    };

    sendPassedPoll(results)
}

// Сбор ответов со всех вопросов
function collectAnswers() {
    return questionsList.map(question => ({
        question_id: question.id,
        type: question.type,
        value: getAnswerValue(question)
    }));
}

// Получение значения ответа для конкретного вопроса
function getAnswerValue(question) {
    const questionEl = $(`#${question.id}`);

    switch (question.type) {
        case 'short text':
            return questionEl.find('.answerShort').val();

        case 'long text':
            return questionEl.find('.answerLong').val();

        case 'radio':
            return questionEl.find('input[type="radio"]:checked').next('label').text() || null;

        case 'checkbox':
            return questionEl.find('input[type="checkbox"]:checked')
                .map((i, el) => $(el).next('label').text()).get();

        default:
            return null;
    }
}

// Отправка данных на сервер
async function sendPassedPoll(data) {
    sendRequest('/post_pass_poll', 'POST', data)
        .then(() => {
            showSuccessOverlay()
        })
        .catch((error) => {
            showFailOverlay(error)
        })
}

function showSuccessOverlay() {
    $('#overlay-success').show();
}

$('.overlay').on('click', '.go-home', function () {
    window.location.href = `/profile/${localStorage.userId}`;
});