// TODO добавление вопросов:
// изначально есть 1 опрос, 3 поля: текст вопроса, поле для загрузки картинки, кнопка выбора типа ответа. ниже их кнопка "добавить вопрос"

const modalType = $("#choose-question-type-modal");
const openModalBtn = $('.chooseQuestionType')
const closeModalBtn = $('.modal-close')

currentQuestionBtn = null
let currentQuestionContent = null // переменная хранит вопрос, для которого сейчас выбирается тип вопроса в модальном окне. модалка открывается по нажатию на кнопку, а в эту переменную записывается родитель этой кнопки

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

    console.log('currentQuestionContent: ', currentQuestionContent)
    currentQuestionContent.append($(content));

    $(currentQuestionBtn).hide()
    modalType.hide();


    currentQuestionBtn = null
    currentQuestionContent = null // после генерации содержимого вопроса обнуляем currentQuestionContent
})

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
        content = '<div class="option"><input type="radio" name="1" id="first"><label for="first">first</label></div><div class="option"><input type="radio" name="1" id="second"><label for="second">second</label></div><br><button class="addOption">+</button>'

    } else if (questionType == "checkbutton") {
        return 0

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
    questionsIds++

    // создаем новый вопрос
    let newQuestion = $('<div class="question" id="' + questionsIds + '"><span class="questionId">Вопрос #' + questionsIds + '</span><input type="text" maxlength="60" placeholder="Задайте вопрос"><button class="addQuestionImage">+ Картинка опроса (необязательно)</button>                        <button class="chooseQuestionType">Выберите тип ответа</button>                        <div class="questionContent"></div>                        <button class="deleteQuestion">Удалить вопрос</button> ');

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
    };
    console.log("pollData:", pollData)

    if (checkCorrectData(pollData)) {
        // отправляем опрос на сервер
        sendData();

        // Закрываем модальное окно
        modal.hide();

        // Сбрасываем форму
        resetForm();
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
