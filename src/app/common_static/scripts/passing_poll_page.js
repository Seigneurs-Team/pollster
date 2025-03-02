const questionsDiv = $("#questions");

// отрисовка вопросов
questionsList.forEach(question => {
    const questionEl = $(`<div id="${question.id}" class="question"></div>`)

    // <p> текст впороса
    const questionText = $(`<p class="question-text">${question.text}</p>`)
    const questionContent = answerType(question.type, question.id, question);

    questionEl.append(questionText);
    questionEl.append(questionContent);
    questionsDiv.append(questionEl);

})

// нажатие на кнопку "прохождение опроса"
$(".start").on('click', function () {
    questionsDiv.show();
    $(this).hide()
});

// отрисовка содержимого вопросов
function answerType(questionType, questionId, question) {
    // отрисовка вопросов: возвращает соответствующий контент:
    //текст вопроса выводится в любом случае, поэтому он не в этой функции, т.к. не зависит от типа
    //  - вопрос с развернутым ответом - поле для ввода ответа textarea
    //  - вопрос с кратким текстовым ответом - поле для ввода ответа input:text
    //  - checkbox: ul со всеми вариантами: checkbox, p
    //  - radiobutton: ul со всеми вариантами: radio, p

    if (questionType == "short text") {
        return '<input class="answerShort" type="text" maxlength="60" placeholder="Короткий ответ">';
    } else if (questionType == "long text") {
        return '<textarea class="answerLong" type="text" rows="5" maxlength="700" placeholder="Развернутый ответ">';

    } else if (questionType == "radiobutton" | questionType == "checkbox") {
        // name равно индексу question, id должно быть уникально как в каждой радиокнопке/чекбоксе, так и в каждом вопросе, поэтому оно будет составляться из id вопроса и номера кнопки {question_id}-{radiobutton_id}. номер кнопки из counter считаем, просто по порядку
        let optionsCounter = 0

        let options = $(`<div class="options"></div>`)

        question.options.forEach(option => {
            options.append(addOption(questionType, questionId, option, optionsCounter))
            optionsCounter++
        })

        return options
        // TODO вопросы с изображениями
    } else if (questionType == "radiobutton img") {
        return 0

    } else if (questionType == "checkbox img") {
        return 0

    }
}
// отрисовка вариантов ответов
function addOption(type, questionId, option, counter) {
    // Создаем новый вариант ответа

    // id варианта ответа составляется из id вопроса и порядкового номера варианта ответа (передается аргументом counter)
    const id = questionId + "_" + counter

    return $(`<div class="option">
        <input type="${type == "radiobutton" ? "radio" : type}" name="${questionId}" id=${id} class="check">
        <label type="text" for=${id}>${option}</label>
    </div>`)
}


// TODO отправка результатов опроса на сервер: 1) извлечение из тэгов 2) отправка
// Извлечение и отправка результатов
$(".submit").on('click', function () {
    const results = {
        poll_id: "{{ poll.id_of_poll }}",
        answers: []
    };

    questionsList.forEach(question => {
        const answer = {
            question_id: question.id,
            type: question.type,
            value: null
        };

        // Обработка разных типов вопросов
        const questionEl = $(`#${question.id}`);
        switch (question.type) {
            case 'short text':
                answer.value = questionEl.find('.answerShort').val();
                break;

            case 'long text':
                answer.value = questionEl.find('.answerLong').val();
                break;

            case 'radiobutton':
                const selectedRadio = questionEl.find('input[type="radio"]:checked');
                answer.value = selectedRadio.length ? selectedRadio.next('label').text() : null;
                break;

            case 'checkbox':
                const checkedBoxes = questionEl.find('input[type="checkbox"]:checked');
                answer.value = checkedBoxes.map(function() {
                    return $(this).next('label').text();
                }).get();
                break;
        }

        results.answers.push(answer);
    });
console.log(results)
    // Отправка на сервер
    // $.ajax({
    //     url: '/submit-poll/',  // Указать правильный URL
    //     method: 'POST',
    //     contentType: 'application/json',
    //     data: JSON.stringify(results),
    //     success: function(response) {
    //         alert('Ответы успешно отправлены!');
    //         window.location.href = '/';  // Перенаправление после успеха
    //     },
    //     error: function(xhr) {
    //         alert('Ошибка отправки: ' + xhr.responseText);
    //     }
    // });
});