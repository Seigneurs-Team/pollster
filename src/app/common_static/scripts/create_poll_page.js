// TODO добавление вопросов:
// изначально 3 поля: текст вопроса, поля для загрузки картинки, выбор типа ответа. ниже их кнопка "добавить вопрос"
// после выбора типа ответа кнопка "тип ответа" скрывается, добавляется соответствующие интерфейс:
//  - вопрос с развернутым ответом - ничего не добавляется
//  - вопрос с кратким текстовым ответом - input для ввода правильного ответа (если пользователь ничего не напишет, то правильного ответа нет)
//  - чекбоксы: ul (минимум 2 li), после него кнопка "+" для добавления варианта ответа. интерфейс выбора правлиьного ответа???
//


const modalType = $("#choose-question-type-modal");
const openModalBtn = $('.chooseQuestionType')
const closeModalBtn = $('.modal-close')


$(window).on("click", function (event) {
    if (event.target == modalType[0]) {
        modalType.hide();
    }
});

openModalBtn.on('click', function() {
    modalType.show();
})

closeModalBtn.on('click', function() {
    modalType.hide();
})

$(".answerType").on('click', function () {
    console.log($(this).text())
    modalType.hide();
})



submitButton = $("#submitPollBtn");
submitButton.on('click', submitPoll);
console.log(submitButton)
function submitPoll(event) {
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


function sendData() { // тут данные просто отправляются на сервер, и всё. Т.к. сейчас они создаются модалкой, то на странице список опросов обновляться не будет, но это не проблема, т.к. в конечной версии опросы будут создаваться на отдельной страинице, а списки опросов на других страницах будут подгружаться уже из БД.
    jsonPollData = JSON.stringify(pollData)

    // тут надо отправить jsonPollData (json нового опроса) на сервер
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
