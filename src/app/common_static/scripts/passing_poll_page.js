const questionsDiv = $("#questions");

// временный список вопросов
// const questionsList = [
//     {
//         "id": "1",
//         "type": "short text",
//         "text": "ваше имя",
//         "rightAnswer": ""},
//     {
//         "id": "2",
//         "type": "long text",
//         "text": "расскажите о себе"
//     }, {
//         "id": "3",
//         "type": "radiobutton",
//         "text": "ваш пол",
//         "options": ["м", "ж", "другое"],
//         "rightAnswersId": []
//     }, {
//         "id": "4",
//         "type": "checkbox",
//         "text": "домашние животные",
//         "options": ["нет", "кошка❤️❤️❤️", "собака", "попугай🤔"],
//         "rightAnswersId": []
//     }]
console.log(questionsList)
questionsList.forEach(question => {

    const questionEl = $(`<div id="${question.id}" class="question"></div>`)


    // <p> текст впороса
    const questionText = $(`<p class="question-text">${question.text}</p>`)
    // const questionInput = $(`<input type="text" placeholder="Введите ответ">`) //временно
    const questionContent = answerType(question.type, question.id, question);


    questionEl.append(questionText);
    questionEl.append(questionContent);
    questionsDiv.append(questionEl);

})


$(".start").on('click', function () {
    questionsDiv.show();
    $(this).hide()
});


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


function addOption(type, questionId, option, counter) {
    // Создаем новый вариант ответа

    // id варианта ответа составляется из id вопроса и порядкового номера варианта ответа (передается аргументом counter)
    const id = questionId + "_" + counter

    return $(`<div class="option">
        <input type="${type == "radiobutton" ? "radio" : type}" name="${questionId}" id=${id} class="check">
        <label type="text" for=${id}>${option}</label>
    </div>`)
}
