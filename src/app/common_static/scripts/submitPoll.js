// отправка опроса на сервер
const host = 'http://127.0.0.1:8000';


export function submitPoll(event) {
    // список вопросов будет при отправке формы формироваться посредством перебора всех элементов с классом .question и извлечения оттуда данных
    console.log('submitPollBtn clicked')

    event.preventDefault(); // Prevent default form submission behavior

    // Перебираем все элементы с классом .question и добавляем их данные в questions в виде js-объекта

    let questions = $('.question').map(function () {
        let type = $(this).attr('data-type')
        let options = []
        let rightAnswersId = []

        // если это вопрос с вариантами ответа, то извлекаем их. если нет, то options останется []
        if (type == 'radiobutton' | type == 'checkbox') {
            // id ответов начинаются с 0
            let counter = -1
            $(this).find('.option').each(function () {
                // Извлекаем значение из input.value, убираем пробелы в начале и в конце
                let value = $(this).find('.value').val().trim();
                // Если значение не пустое, добавляем его в массив options
                if (value) {
                    options.push(value);
                    counter++
                }
                if ($(this).find('.check').is(':checked')) {
                    rightAnswersId.push(counter);
                    // записывать буду порядковый номер правильных ответов, который возьму в качестве id. лучше использовать id, чем сравнение строк
                }
            });
        }


        return {
            id: $(this).attr('id'),
            type: type,
            text: $(this).find('.questionText').val(),
            options: options,
            rightAnswersId: rightAnswersId,
        }
    }).get() // Преобразуем результат в массив



    // Собираем данные
    let pollData = {
        name_of_poll: $('#pollTitle').val(),
        description: $('#pollDescription').val(),
        tags: $('#pollTags').val(),
        questions: questions,
    };
    console.log("pollData:", pollData)

    // если введенные данные корректны, отправляем опрос на сервер
    if (checkCorrectData(pollData)) { sendData(pollData); }
}


function sendData(pollData) {
    // данные  отправляются на сервер
    let jsonPollData = JSON.stringify(pollData)

    const Http = new XMLHttpRequest();

    Http.open("POST", host + "/create_poll", true);
    Http.setRequestHeader("Content-Type", "application/json");
    Http.send(jsonPollData);

    Http.onload = function () {
        var response = JSON.parse(Http.response);
        console.log('result: ', response);
        if (response) {
            alert('Опрос успешно создан')
            window.location.href = '/'; // Перенаправление на домашнюю страницу
        }
    };

    console.log("pollData в json:", jsonPollData)
}


function checkCorrectData(pollData) { // проверка на корректные данные в форме перед ее отправкой. пока что тут только проверка на пустое название. TODO сделать проверку на ненулевое количество вопросов, на ненулевое количество вариантов ответа в radio и checkbox. не непустой текст вопросов
    if (pollData.name_of_poll) {
        return true
    } else {
        // если поле имени опроса пустое, надо сообщить об этом пользователю. пока что в консоль
        console.log('имя опроса не может быть пустым!')
    }
}
