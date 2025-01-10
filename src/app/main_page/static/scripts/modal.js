// используется jquery (подключается через sdn в index.html)


// данные в pollData будут заноситься в обработчиках действий пользователя во время создания опроса: нажатие на кнопки которые создают вопросы, а также окончание редактирования таких полей, как название опроса, его описание и загрузка картинки опроса.

// Операции с модальным окном
var modal = $("#create-poll-modal");
var btn = $("#createPollBtn");
var span = $(".close").first();
var host = 'http://127.0.0.1:8000';

btn.on("click", function () {
    modal.css("display", "block");
    let pollData = {
        // TODO по умолчанию ставить None или ''? наверное лучше '' и сделать где надо проверки на пустые значения (которые обязательные: имя)
        name_of_poll: '',
        description: '',
        tags: '',
    };
});

span.on("click", function () {
    modal.hide();
});

$(window).on("click", function (event) {
    if (event.target == modal[0]) {
        modal.hide();
    }
});

const submitButton = $('#submitPollBtn');
submitButton.on('click', submitPoll);

function submitPoll(event) {
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

    Http.open("POST", host+"/create_poll", true);
    Http.setRequestHeader("Content-Type", "application/json");
    Http.send(jsonPollData);

    Http.onload = function() {
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
 
function resetForm() {
    // очистка формы
    $('#pollTitle').val('');
    $('#pollDescription').val('');
    $('#pollTags').val('');
}
