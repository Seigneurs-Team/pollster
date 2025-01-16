// TODO добавление вопросов:
// изначально есть 1 опрос, 3 поля: текст вопроса, поле для загрузки картинки, кнопка выбора типа ответа. ниже их кнопка "добавить вопрос"
import "1.js"
currentQuestionBtn = null
let currentQuestionContent = null // переменная хранит вопрос, для которого сейчас выбирается тип вопроса в модальном окне. модалка открывается по нажатию на кнопку, а в эту переменную записывается родитель этой кнопки
const modalType = $("#choose-question-type-modal");
const openModalBtn = $('.chooseQuestionType')
const closeModalBtn = $('.modal-close')
const host = 'http://127.0.0.1:8000';


$(window).on("click", function (event) {
    if (event.target == modalType[0]) {
        modalType.hide();
    }
});

const showModal = function (target) {
    // кнопка "выберите тип вопроса", на которую только что нажали и контент соответствующего вопроса
    currentQuestionBtn = target
    console.log('target: ', target)
    currentQuestionContent = $(target).parent('.question').find('.questionContent');
    console.log("$(target).parent('.question'): ", $(target).parent('.question'))

    console.log('currentQuestionContent defining: ', currentQuestionContent)

    modalType.show();
}

openModalBtn.on('click', function () { showModal(this) })

closeModalBtn.on('click', function () {
    modalType.hide();
})

$(".answerType").on('click', function () {
    questionType = $(this).attr('name')

    // после выбора типа ответа кнопка "тип ответа" скрывается, добавляется соответствующие интерфейс
    content = questionContents(questionType)

    currentQuestionContent.append($(content));


    /* назначаем обработчики событий (как правило это нужно на button которая добавляет option в checkbox и radiobutton). тут надо поставить проверку на questionType */

    
    
    $('.addOptionRadio').on('click', function() {
        addOptionRadio()
    })
    
    $('.addOptionCheckbox').on('click', function() {
        addOptionCheckbox()
    })
    
    // if (questionType == "radiobutton") {

    // } else if (questionType == "checkbutton") {

    // }
    

    $(currentQuestionBtn).hide()
    modalType.hide();


    currentQuestionBtn = null
    currentQuestionContent = null // после генерации содержимого вопроса обнуляем currentQuestionContent
})



function addOptionRadio () {
    console.log('addOptionRadio clicked')

}


function addOptionCheckbox () {
    console.log('addOptionCheckbox clicked')

}

function questionContents(questionType) {
    //  - вопрос с развернутым ответом - добавляется надпись "вопрос с развернутым ответом"
    //  - вопрос с кратким текстовым ответом - input для ввода правильного ответа (если пользователь ничего не напишет, то правильного ответа нет. placeholder="введите правильный ответ (необязательно)")
    //  - checkbox: ul (минимум 2 li), после него кнопка "+" для добавления варианта ответа. выбранный(е) вариант(ы) считаются правильными
    //  - radiobutton:  тож самое. если картинки, то в ul добавляем поля для загрузки изображений. если не во все поля загружены изображения, будет выходить предупреждение

    if (questionType == "short text") {
        console.log('hi there')
        content = '<input type="text" maxlength="60" placeholder="введите правильный ответ (необязательно)">';
    } else if (questionType == "long text") {
        content = '<p>Это вопрос с развернутым ответом</p>';

    } else if (questionType == "radiobutton") {
        content = '<div class="option"><input type="radio" name="1" id="first"><label for="first">first</label></div><div class="option"><input type="radio" name="1" id="second"><label for="second">second</label></div><br><button class="addOptionRadio">+</button>'

    } else if (questionType == "checkbutton") {
        content = '<div class="option"><input type="checkbox" name="1" id="first"><label for="first">first</label></div><div class="option"><input type="checkbox" name="1" id="second"><label for="second">second</label></div><br><button class="addOptionCheckbox">+</button>'

    } else if (questionType == "radiobutton img") {
        return 0

    } else if (questionType == "checkbutton img") {
        return 0

    }

    return content;
}



let questionsIds = 1 // увеличивается при добавлении нового вопроса, не уменьшается никогда. нужна для создания уникального id каждому вопросу

const deleteQuestion = function (target) {
    console.log('deleteQuestion activated')
    $(target).parent('.question').remove(); // Удаляем родительский элемент .question
}

addQuestionButton = $(".addQuestion");
addQuestionButton.on('click', addQuestion);

function addQuestion(event) {

    
    questions123 = $('.question')
    questions123.each(function(index, element) {
        console.log('text:', $(element).find('.questionText').val())
        console.log('content:', $(element).find('.questionContent').val())
    })
    

    questionsIds++

    // создаем новый вопрос
    let newQuestion = $('<div class="question" id="' + questionsIds + '"><span class="questionId">Вопрос #' + questionsIds + '</span><input type="text" maxlength="60" placeholder="Задайте вопрос"><button class="questionImage">+ Картинка опроса (необязательно)</button>                        <button class="chooseQuestionType">Выберите тип ответа</button>                        <div class="questionContent"></div>                        <button class="deleteQuestion">Удалить вопрос</button> ');

    $(".questions").append(newQuestion);

    //назначаем обработчики событий
    $(".deleteQuestion").on('click', function (event) {
        deleteQuestion(this)
    });
    $('.chooseQuestionType').on('click', function () { showModal(this) })

    // добавляются поле для ввода текста вопроса, поле для загрузки картинки, кнопка выбора типа ответа.
}

$(".deleteQuestion").on('click', function (event) {
    deleteQuestion(this)
});


submitButton = $("#submitPollBtn");
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
