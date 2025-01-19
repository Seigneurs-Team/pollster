// добавление вопросов:

import { showModal } from './modalQuestionType.js';
import { submitPoll } from './submitPoll.js';


let questionsIds = 0 // увеличивается при добавлении нового вопроса, не уменьшается никогда. нужна для создания уникального id каждому вопросу


// удаление вопроса
$(".deleteQuestion").on('click', function (event) { deleteQuestion(this) });
const deleteQuestion = function (target) {
    console.log('deleteQuestion activated')
    $(target).parent('.question').remove(); // Удаляем родительский элемент .question
}


// добавление вопроса
$(".addQuestion").on('click', addQuestion);
function addQuestion(event) {
    // создаем новый вопрос

    questionsIds++ // увеличиваем счетчик ID

    // добавляются поле для ввода текста вопроса, поле для загрузки картинки, кнопка выбора типа ответа.
    let newQuestion = $(`
<div class="question" id="` + questionsIds + `">
    <span class="questionId">Вопрос #` + questionsIds + `</span>
    <input class="questionText" type="text" maxlength="60" placeholder="Задайте вопрос">
    <button class="questionImage">+ Картинка опроса (необязательно)</button>
    <button class="chooseQuestionType">Выберите тип ответа</button>
    <div class="questionContent"></div>
    <button class="deleteQuestion">Удалить вопрос</button>
</div>
`);

    // добавляем новый вопрос
    $(".questions").append(newQuestion);

    //назначаем обработчики событий
    $(".deleteQuestion").on('click', function (event) {
        deleteQuestion(this)
    });
    $('.chooseQuestionType').on('click', function () { showModal(this) })
}



// отправка опроса на сервер
let submitButton = $("#submitPollBtn");
submitButton.on('click', submitPoll);