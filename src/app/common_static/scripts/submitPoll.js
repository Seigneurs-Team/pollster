// отправка опроса на сервер
const host = 'http://127.0.0.1:8000';


export function submitPoll(event) {
    // список вопросов будет при отправке формы формироваться посредством перебора всех элементов с классом .question и извлечения оттуда данных
    console.log('submitPollBtn clicked')

    event.preventDefault(); // Prevent default form submission behavior
/*
    let questions = [
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
    ]
*/
// Перебираем все элементы с классом .question и добавляем их данные в questions в виде js-объекта

    let questions = $('.question').map(function() {
        return {
            id: $(this).attr('id'),
            type: '',
            text: $(this).find('.questionText').val(),
            // options: [option1, option2, option3], от типа будет зависеть. в if засунуть, в тернарный оператор прямо здесь
            // rightAnswers: [option1, option2], тоже от типа зависит. если long text, то '', если short text, то содержимое инпута .right-answer. если checkbox или radio, то находим .option с правильным ответом, если такового нет, то '' нверное. лучше не '', а какой-нибудь null, а то можно же создать опрос, где реально правильным ответом будет '', тогда будет иметь место двузначность
        }
    }).get()



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
