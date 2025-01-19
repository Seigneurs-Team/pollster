// добавление вопросов:
// изначально есть 1 опрос, 3 поля: текст вопроса, поле для загрузки картинки, кнопка выбора типа ответа. ниже их кнопка "добавить вопрос"
const host = 'http://127.0.0.1:8000';


// import *  as modalQuestionType from './modalQuestionType.js';
import {showModal} from './modalQuestionType.js';


let questionsIds = 0 // увеличивается при добавлении нового вопроса, не уменьшается никогда. нужна для создания уникального id каждому вопросу

const deleteQuestion = function (target) {
    console.log('deleteQuestion activated')
    $(target).parent('.question').remove(); // Удаляем родительский элемент .question
}

let addQuestionButton = $(".addQuestion");
addQuestionButton.on('click', addQuestion);

function addQuestion(event) {
    questionsIds++ // увеличиваем счетчик ID

    // создаем новый вопрос
    let newQuestion = $('<div class="question" id="' + questionsIds + '"><span class="questionId">Вопрос #' + questionsIds + '</span><input type="text" maxlength="60" placeholder="Задайте вопрос"><button class="questionImage">+ Картинка опроса (необязательно)</button>                        <button class="chooseQuestionType">Выберите тип ответа</button>                        <div class="questionContent"></div>                        <button class="deleteQuestion">Удалить вопрос</button> ');

    $(".questions").append(newQuestion);

    //назначаем обработчики событий
    $(".deleteQuestion").on('click', function (event) {
        deleteQuestion(this)
    });
    
    $('.chooseQuestionType').on('click', function () {showModal(this) })

    // добавляются поле для ввода текста вопроса, поле для загрузки картинки, кнопка выбора типа ответа.
}

$(".deleteQuestion").on('click', function (event) {
    deleteQuestion(this)
});


let submitButton = $("#submitPollBtn");
submitButton.on('click', submitPoll);

function submitPoll(event) {
    // список вопросов будет при отправке формы формироваться посредством перебора всех элементов с классом .question и извлечения оттуда данных

    console.log('submitPollBtn clicked')
    event.preventDefault(); // Prevent default form submission behavior
    // Собираем данные
    pollData = {
        name_of_poll: $('#pollTitle').val(),
        description: $('#pollDescription').val(),
        tags: $('#pollTags').val(),
        questions: [
            {
                'type': 'checkbox',
                'text': 'question1',
                'options': ['option1', 'option2', 'option3'],
                'right-answers': ['option1', 'option2']
            },
            {
                'type': 'checkbox',
                'text': 'question2',
                'options': ['option1', 'option2'],
                'right-answers': null,
            },
            {
                'type': 'short',
                'text': 'question3',
                'options': null,
                'right-answer': 'this is right answer',
            },
            {
                'type': 'long',
                'text': 'question4',
                'options': null,
                'right-answer': null,
            },
        ],
    };
    console.log("pollData:", pollData)

    if (checkCorrectData(pollData)) {
        // отправляем опрос на сервер
        sendData();
    }

}


function sendData() { // данные  отправляются на сервер
    jsonPollData = JSON.stringify(pollData)

    const Http = new XMLHttpRequest();

    Http.open("POST", host + "/create_poll", true);
    Http.setRequestHeader("Content-Type", "application/json");
    Http.send(jsonPollData);

    Http.onload = function () {
        var response = JSON.parse(Http.response);
        console.log('result: ', response);
    };

    console.log("pollData в json:", jsonPollData)
}

function checkCorrectData(pollData) { // проверка на корректные данные в форме перед ее отправкой. пока что тут только проверка на пустое название
    if (pollData.name_of_poll) {
        return true
    } else {
        // если поле имени опроса пустое, надо сообщить об этом пользователю. пока что в консоль
        console.log('имя опроса не может быть пустым!')
    }
}
