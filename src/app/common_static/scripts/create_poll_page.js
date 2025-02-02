// добавление вопросов:

import {submitPoll} from './submitPoll.js';


let questionsId = 0 // увеличивается при добавлении нового вопроса, не уменьшается никогда. нужна для создания уникального id каждому вопросу
const modalType = $("#choose-question-type-modal");
let content = null


// удаление вопроса
$(".deleteQuestion").on('click', function (event) { deleteQuestion(this)});
const deleteQuestion = function (target) {
    console.log('deleteQuestion activated')
    $(target).parent('.question').remove(); // Удаляем родительский элемент .question
}


// по нажатию на "добавить вопрос" открываем модальное окно для выбора типа вопроса
$(".addQuestion").on('click', function () { modalType.show();});

// закрытие модального окна
$('.modal-close').on('click', function () { modalType.hide();})


// после выбора типа вопроса
$(".answerType").on('click', function () {
    questionsId++ // увеличиваем счетчик ID
    let questionType = $(this).attr('name') // тип вопроса


    // получаем контент в зависимости от выбранного типа ответа (нажатая кнопка автоматически передается в функцию как this)
    content = answerType(questionType, questionsId)

    // сам вопрос, в который вставляется content
    let newQuestion = $(`
<div class="question" id="` + questionsId + `" data-type="` + questionType + `">
    <span class="questionId">Вопрос #` + questionsId + `</span>
    <input class="questionText" type="text" maxlength="60" placeholder="Задайте вопрос">
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
    $(".deleteQuestion").on('click', function (event) { deleteQuestion(this) });

    /* назначаем обработчики событий на button которая добавляет option в checkbox и radiobutton) */
    if (questionType == "radiobutton") {
        $('#' + questionsId).find('.addOptionRadio').on('click', function () { addOption(this, 'radio', questionsId) })
    }
    if (questionType == "checkbox") {
        $('#' + questionsId).find('.addOptionCheckbox').on('click', function () { addOption(this, 'checkbox', questionsId) })
    }
    modalType.hide();
    content = null

})


function answerType(questionType, questionId) {
    // обработка нажатия на кнопку выбора того или иного типа вопроса: возвращает соответствующий контент:
    //  - вопрос с развернутым ответом - добавляется надпись "вопрос с развернутым ответом"
    //  - вопрос с кратким текстовым ответом - input для ввода правильного ответа (если пользователь ничего не напишет, то правильного ответа нет. placeholder="введите правильный ответ (необязательно)")
    //  - checkbox: ul (минимум 2 li), после него кнопка "+" для добавления варианта ответа. выбранный(е) вариант(ы) считаются правильными
    //  - radiobutton:  тож самое. если картинки, то в ul добавляем поля для загрузки изображений. если не во все поля загружены изображения, будет выходить предупреждение

    if (questionType == "short text") {
        return '<input class="right-answer" type="text" maxlength="60" placeholder="введите правильный ответ (необязательно)">';
    } else if (questionType == "long text") {
        return '<p>Это вопрос с развернутым ответом</p>';

    } else if (questionType == "radiobutton") {
        // name равно индексу question, id должно быть уникально как в кажодой радиокнопке, так и в каждом вопросе, поэтому оно будет составляться из номера вопроса и номера кнопки {question_id}-{radiobutton_id}. пока что question_id по умолчанию 1. в checkbox то же самое
        // TODO добавить кнопку "удалить" для option (и в checkbox тоже)
        return `
    <div class="options">
        <div class="option"><input type="radio" name="1" id="${questionId}_1" class="check"> 
        <input type="text" for="1_1" id="${questionId}_1-input" class="value"></input>
        </div>
        <div class="option"><input type="radio" name="1" id="${questionId}_2" class="check"> 
        <input type="text" for="1_2" id="${questionId}_2-input" class="value"></input></div>
    </div>
    <br><button class="addOptionRadio">+</button>
    `
    } else if (questionType == "checkbox") {
        return `
    <div class="options">
        <div class="option"><input type="checkbox" name="1" id="${questionId}_1" class="check"> 
        <input type="text" for="${questionId}_1" id="${questionId}_1-input" class="value">
        </div>
        <div class="option"><input type="checkbox" name="1" id="${questionId}_2" class="check"> 
        <input type="text" for="${questionId}_2" id="${questionId}_2-input" class="value"></div>
    </div>
    <br><button class="addOptionCheckbox">+</button>
    `
        // TODO загрузка изображений
    } else if (questionType == "radiobutton img") {
        return 0

    } else if (questionType == "checkbox img") {
        return 0

    }
}


function addOption(target, type, questionsId) {
    let options = $(target).closest('.question').find('.options'); // closest находит ближайший элемент .question. отличие от метода parent в том, что parent ищет только родительский элемент, а closest - также выше по иерархии.

    let optionsCount = options.find('.option').length;

    // Создаем новый вариант ответа
    optionsCount++; // Увеличиваем счетчик для нового варианта
    const id = questionsId + "_" + optionsCount
    options.append($(`<div class="option">
        <input type="${type}" name="${questionsId}" id=${id} class="check">
        <input type="text" for=${id} id="${id}-input" class="value">
    </div>`));
    $(`#${id}-input`).focus()
}


// отправка опроса на сервер
$("#submitPollBtn").on('click', submitPoll);