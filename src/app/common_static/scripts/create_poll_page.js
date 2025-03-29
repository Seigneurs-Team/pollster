// добавление вопросов:

import {submitPoll} from './submitPoll.js';


let questionsId = 0 // увеличивается при добавлении нового вопроса, не уменьшается никогда. нужна для создания уникального id каждому вопросу
const modalType = $("#choose-question-type-modal");
let content = null


// удаление вопроса
$(".deleteQuestion").on('click', function (event) {
    deleteQuestion(this)
});
const deleteQuestion = function (target) {
    console.log('deleteQuestion activated')
    $(target).parent('.question').remove(); // Удаляем родительский элемент .question
}


// по нажатию на "добавить вопрос" открываем модальное окно для выбора типа вопроса
$(".addQuestion").on('click', function () {
    modalType.show();
});

// закрытие модального окна
$('.modal-close').on('click', function () {
    modalType.hide();
})


// после выбора типа вопроса
$(".answerType").on('click', function () {
    questionsId++ // увеличиваем счетчик ID
    let questionType = $(this).attr('name') // тип вопроса


    // получаем контент в зависимости от выбранного типа ответа (нажатая кнопка автоматически передается в функцию как this)
    content = answerType(questionType, questionsId)

    // сам вопрос, в который вставляется content
    let newQuestion = $(`
<div class="question" id="${questionsId}" data-type="${questionType}">
    <span class="questionId">Вопрос #` + questionsId + `</span>
    <div class="input-wrapper">
        <input class="questionText" type="text" maxlength="200" placeholder="Задайте вопрос">
        <div class="error-message">Недопустимые символы (например, &lt; или &gt;)!</div>
    </div>
    <button class="questionImage">+ Картинка опроса (необязательно)</button>
    <div class="questionContent">` + content + `</div>
    <button class="deleteQuestion">Удалить вопрос</button>
</div>
    `)

    // добавляем новый вопрос
    $(".questions").append(newQuestion);

    // фокус на поле ввода вопроса
    $(`.questionText`).focus()

    //назначаем обработчики событий
    $(".deleteQuestion").on('click', function (event) {
        deleteQuestion(this)
    });

    /* назначаем обработчики событий на button которая добавляет option в checkbox и radiobutton) */
    if (questionType === "radiobutton") {
        $('#' + questionsId).find('.addOptionRadio').on('click', function () {
            addOption(this, 'radio', questionsId)
        })
    }
    if (questionType === "checkbox") {
        $('#' + questionsId).find('.addOptionCheckbox').on('click', function () {
            addOption(this, 'checkbox', questionsId)
        })
    }

    // удаление варианта ответа
    $('#' + questionsId).on('click', '.delOption', function (event) {
        delOption(this);
    });

    // Проверяем все текстовые поля
    $('#' + questionsId).find(`input[type="text"], textarea`).each(function () {
        $(this).on("input", function (e) {
            showHasHTMLTagsMessage(e)
        })
    })

// Проверяем все текстовые поля на наличие html тэгов (защита от xss)
    $('#' + questionsId).on('input', `input[type="text"], textarea`, function (event) {
        showHasHTMLTagsMessage(event)
    });


    modalType.hide();
    content = null

})


function answerType(questionType, questionId) {
    // обработка нажатия на кнопку выбора того или иного типа вопроса: возвращает соответствующий контент:
    //  - вопрос с развернутым ответом - добавляется надпись "вопрос с развернутым ответом"
    //  - вопрос с кратким текстовым ответом - input для ввода правильного ответа (если пользователь ничего не напишет, то правильного ответа нет. placeholder="введите правильный ответ (необязательно)")
    //  - checkbox: ul (минимум 2 li), после него кнопка "+" для добавления варианта ответа. выбранный(е) вариант(ы) считаются правильными
    //  - radiobutton:  тож самое. если картинки, то в ul добавляем поля для загрузки изображений. если не во все поля загружены изображения, будет выходить предупреждение

    if (questionType === "short text") {
        return `
            <div class="input-wrapper">
                <input class="right-answer" type="text" maxlength="100" placeholder="введите правильный ответ (необязательно)">
                <div class="error-message">Недопустимые символы (например, &lt; или &gt;)!</div>
            </div>`;
    } else if (questionType === "long text") {
        return '<p>Это вопрос с развернутым ответом</p>';
    } else if (questionType === "radiobutton" || questionType === "checkbox") {
        const type = questionType === "checkbox" ? "checkbox" : "radio"
        return `
    <div class="options">
        ${renderOption(type, questionsId, 1)}
        ${renderOption(type, questionsId, 2)}
    </div>
    <button class="addOption${questionType === "checkbox" ? "Checkbox" : "Radio"}">+</button>
`
        // TODO загрузка изображений
    }
else
    if (questionType === "radiobutton img") {
        return 0

    } else if (questionType === "checkbox img") {
        return 0

    }
}


function renderOption(type, questionId, optionId) {
    console.log("$('main').data('deloption'): ", $('main').data('deloption'))
    return `<div class="option">
        <input type="${type}" name="${questionId}" id="${questionId}_${optionId}" class="check">
            <div class="input-wrapper">
                <input type="text" for="${questionId}_${optionId}" id="${questionId}_${optionId}-input" class="value" placeholder="Вариант ответа" maxlength="100"><button class="delOption"><img src="${$('main').data('deloption')}" alt="удалить вариант ответа"></button>
                    <div class="error-message">Недопустимые символы (например, &lt; или &gt;)!</div>
            </div>
    </div>`
}

function addOption(target, type, questionsId) {
    let options = $(target).closest('.question').find('.options'); // closest находит ближайший элемент .question. отличие от метода parent в том, что parent ищет только родительский элемент, а closest - также выше по иерархии.

    let optionsCount = options.find('.option').length;

    // Создаем новый вариант ответа
    optionsCount++; // Увеличиваем счетчик для нового варианта
    // const id = questionsId + "_" + optionsCount
    options.append($(`${renderOption(type, questionsId, optionsCount)}`));
    $(`#${questionsId + "_" + optionsCount}-input`).focus()
}

function delOption(target) {
    console.log('deleteOption activated')

    // Создаем новый вариант ответа
    // console.log('target.id:', target.id)
    $(target).closest('.option').remove(); // Удаляем родительский элемент .option
}

// отправка опроса на сервер
$("#submitPollBtn").on('click', submitPoll);

// Функция для проверки на HTML-теги
export function hasHTMLTags(input) {
    const htmlPattern = /<[^>]*>/; // Ищет любые HTML-теги
    return htmlPattern.test(input);
}

function showHasHTMLTagsMessage(e) {
    const target = e.target;
    const value = $(target).val();
    if (hasHTMLTags(value)) {
        $(target).parent().find('.error-message').first().css('display', 'inline-block')
    } else {
        $(target).parent().find('.error-message').first().hide()

    }
}

// Проверяем все текстовые поля на наличие html кода
$(`input[type="text"], textarea`).each(function () {
    $(this).on("input", function (e) {
        showHasHTMLTagsMessage(e)
    })

})

$(document).ready(function () {
    $(`.error-message`).each(function () {
        $(this).hide()
    })

    // крести
    $('.delOption').css('background-image', 'url(' + $('main').data('deloption') + ')');

})

$('.tag').click(function() {
    // Проверяем, где находится текущий элемент
    if ($(this).parent().hasClass('not-selected-tags') && $('.selected-tags').children().length < 4) {
        // Если элемент в .not-selected-tags и выбрано менее 4х тэгов, перемещаем его в .selected-tags
        $(this).appendTo('.selected-tags');
    } else if ($(this).parent().hasClass('selected-tags')) {
        // Если элемент в .selected-tags, перемещаем его в .not-selected-tags
        $(this).appendTo('.not-selected-tags');
    }
});

// Фон шапки
$(document).ready(function() {
    $('header').css('background-image', 'url(' + $('header').data('background') + ')');
});