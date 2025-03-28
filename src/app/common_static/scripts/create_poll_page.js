import { submitPoll } from './submitPoll.js';

// Глобальные переменные
let questionsId = 0;
const modalType = $("#choose-question-type-modal");
let content = null;

// Инициализация при загрузке документа
$(document).ready(function () {
    $(`.error-message`).each(function () {
        $(this).hide();
    });

    // Стили для кнопок удаления
    $('.delOption').css('background-image', 'url(' + $('main').data('deloption') + ')');

    // Фон шапки
    $('header').css('background-image', 'url(' + $('header').data('background') + ')');
});

// Удаление вопроса
$(".deleteQuestion").on('click', function (event) {
    deleteQuestion(this);
});

function deleteQuestion(target) {
    console.log('deleteQuestion activated');
    $(target).parent('.question').remove();
}

// Открытие модального окна для выбора типа вопроса
$(".addQuestion").on('click', function () {
    modalType.show();
});

// Закрытие модального окна
$('.modal-close').on('click', function () {
    modalType.hide();
});

// Обработка выбора типа вопроса
$(".answerType").on('click', function () {
    questionsId++;
    let questionType = $(this).attr('name');
    content = answerType(questionType, questionsId);

    // Создание нового вопроса
    let newQuestion = $(`
        <div class="question" id="${questionsId}" data-type="${questionType}">
            <span class="questionId">Вопрос #${questionsId}</span>
            <div class="input-wrapper">
                <input class="questionText" type="text" maxlength="200" placeholder="Задайте вопрос">
                <div class="error-message">Недопустимые символы (например, &lt; или &gt;)!</div>
            </div>
            <button class="questionImage">+ Картинка опроса (необязательно)</button>
            <div class="questionContent">${content}</div>
            <button class="deleteQuestion">Удалить вопрос</button>
        </div>
    `);

    // Добавление вопроса в DOM
    $(".questions").append(newQuestion);
    $(`.questionText`).focus();

    // Назначение обработчиков
    setupQuestionHandlers(questionType, questionsId);
    modalType.hide();
    content = null;
});

// Настройка обработчиков для вопроса
function setupQuestionHandlers(questionType, questionId) {
    $(`#${questionId} .deleteQuestion`).on('click', function (event) {
        deleteQuestion(this);
    });

    if (questionType === "radiobutton") {
        $(`#${questionId} .addOptionRadio`).on('click', function () {
            addOption(this, 'radio', questionId);
        });
    }
    if (questionType === "checkbox") {
        $(`#${questionId} .addOptionCheckbox`).on('click', function () {
            addOption(this, 'checkbox', questionId);
        });
    }

    $(`#${questionId}`).on('click', '.delOption', function (event) {
        delOption(this);
    });

    $(`#${questionId}`).on('input', `input[type="text"], textarea`, function (event) {
        showHasHTMLTagsMessage(event);
    });
}

// Функция для определения контента вопроса
function answerType(questionType, questionId) {
    if (questionType === "short text") {
        return `
            <div class="input-wrapper">
                <input class="right-answer" type="text" maxlength="100" placeholder="введите правильный ответ (необязательно)">
                <div class="error-message">Недопустимые символы (например, &lt; или &gt;)!</div>
            </div>`;
    } else if (questionType === "long text") {
        return '<p>Это вопрос с развернутым ответом</p>';
    } else if (questionType === "radiobutton" || questionType === "checkbox") {
        const type = questionType === "checkbox" ? "checkbox" : "radio";
        return `
            <div class="options">
                ${renderOption(type, questionId, 1)}
                ${renderOption(type, questionId, 2)}
            </div>
            <button class="addOption${questionType === "checkbox" ? "Checkbox" : "Radio"}">+</button>
        `;
    } else if (questionType === "radiobutton img") {
        return '';
    } else if (questionType === "checkbox img") {
        return '';
    }
}

// Генерация HTML для варианта ответа
function renderOption(type, questionId, optionId) {
    return `
        <div class="option">
            <input type="${type}" name="${questionId}" id="${questionId}_${optionId}" class="check">
            <div class="input-wrapper">
                <input type="text" for="${questionId}_${optionId}" id="${questionId}_${optionId}-input" 
                       class="value" placeholder="Вариант ответа" maxlength="100">
                <button class="delOption">
                    <img src="${$('main').data('deloption')}" alt="удалить вариант ответа">
                </button>
                <div class="error-message">Недопустимые символы (например, &lt; или &gt;)!</div>
            </div>
        </div>
    `;
}

// Добавление варианта ответа
function addOption(target, type, questionsId) {
    let options = $(target).closest('.question').find('.options');
    let optionsCount = options.find('.option').length + 1;

    options.append($(renderOption(type, questionsId, optionsCount)));
    $(`#${questionsId}_${optionsCount}-input`).focus();
}

// Удаление варианта ответа
function delOption(target) {
    console.log('deleteOption activated');
    $(target).closest('.option').remove();
}

// Обработка выбора тегов
$('.tag').click(function() {
    if ($(this).parent().hasClass('not-selected-tags') && $('.selected-tags').children().length < 4) {
        $(this).appendTo('.selected-tags');
    } else if ($(this).parent().hasClass('selected-tags')) {
        $(this).appendTo('.not-selected-tags');
    }
});

// Функция для проверки на HTML-теги
function hasHTMLTags(input) {
    const htmlPattern = /<[^>]*>/; // Ищет любые HTML-теги
    return htmlPattern.test(input);
}

// Отображение сообщения об ошибке
function showHasHTMLTagsMessage(e) {
    const target = e.target;
    const value = $(target).val();
    if (hasHTMLTags(value)) {
        $(target).parent().find('.error-message').first().css('display', 'inline-block');
    } else {
        $(target).parent().find('.error-message').first().hide();
    }
}

// Проверка всех текстовых полей на HTML-теги
$(`input[type="text"], textarea`).each(function () {
    $(this).on("input", function (e) {
        showHasHTMLTagsMessage(e);
    });
});

// Отправка опроса
$("#submitPollBtn").on('click', submitPoll);

// Экспорт функции для проверки HTML-тегов
export { hasHTMLTags };