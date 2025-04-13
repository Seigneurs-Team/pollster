import { sendRequest } from './api.js';

// тестовые данные
const statistics = {
    "count_of_users": 1,
    "questions": [
        {
            "id": 93047,
            "type_of_question": "radio",
            "text_of_question": "Вопрос1",
            "serial_number": 1,
            "num_of_right_answers": 1,
            "num_of_wrong_answers": 0,
            "options": [
                {
                    "1": {
                        "count_of_selected": 0,
                        "is_right_answer": false
                    }
                },
                {
                    "2": {
                        "count_of_selected": 1,
                        "is_right_answer": true
                    }
                }
            ]
        },
        {
            "id": 66667,
            "type_of_question": "checkbox",
            "text_of_question": "Вопрос2",
            "serial_number": 2,
            "num_of_right_answers": 1,
            "num_of_wrong_answers": 2,
            "options": [
                {
                    "1": {
                        "count_of_selected": 1,
                        "is_right_answer": false
                    }
                },
                {
                    "2": {
                        "count_of_selected": 3,
                        "is_right_answer": true
                    }
                },
                {
                    "3": {
                        "count_of_selected": 2,
                        "is_right_answer": true
                    }
                }
            ]
        },
        {
            "id": 77777,
            "right_text_answer": "great",
            "type_of_question": "short text",
            "text_of_question": "how are you doing?",
            "serial_number": 3,
            "num_of_right_answers": 3,
            "num_of_wrong_answers": 2
        }
    ]
}
const questions = statistics.questions

async function sendStatisticslRequest(id) {
    const response = await sendRequest(`/get_statistics/${id}`, 'GET');
    // Обработка ответа от сервера
    if (response.status === 200) {
        alert('Статистика успешно получена')
    }
    return await response.json();

}

$(document).ready(function () {
    // отрисовываем графики
    for (let i = 0; i < questions.length; i++) {
        // у каждого вопроса,который есть в statistics (т.е. все, кроме long text) будет график соотношения правильных и неправильных ответов
        drawRightAnswersChart(i)

        // а у вопросов с вариантами ответа будет второй график - количество выбора каждого варианта
        if (questions[i].type_of_question == "radio" || questions[i].type_of_question == "checkbox") {

            const [options, countOfSelected] = getOptions(i)
            drawOprionsChart(i, options, countOfSelected)
        }
    }
})

$('#get-statistics').on('click', async function () {
    console.log('getting statistics...')
    const pollID = $('#get-statistics').data('poll-id') 

    const response = await sendStatisticslRequest(pollID)
    console.log('Ответ сервера:', response);

})


function drawRightAnswersChart(i) {
    // количество выбранных правильных вариантов ответа: в labels всегда "right/wrong", в data 1й элемент - количество правльных, 2й - неправильных ответов. в вопросах с коротким ответом то же самое (но это для графика. а так все ответы будут списком выводиться)

    new Chart($(`#${questions[i].id} .chart.right-answers`), {
        type: 'doughnut',
        data: {
            labels: [
                'right',
                'wrong'
            ],
            datasets: [{
                label: 'right/wrong ansers',
                data: [questions[i].num_of_right_answers, questions[i].num_of_wrong_answers],
                backgroundColor: [
                    'rgb(255, 99, 132)',
                    'rgb(54, 162, 235)',
                    'rgb(255, 205, 86)'
                ],
                hoverOffset: 4
            }]
        },
    });
}

function drawOprionsChart(i, options, countOfSelected) {
    // количество выбранных вариантов ответа: нужно получить список вариантов ответа и список количества выбора каждого из них
/// можно использовать типы bar, polarArea, pie, doughnut
    new Chart($(`#${questions[i].id} .chart.options`), {
        type: 'bar',
        data: {
            labels: options,
            datasets: [{
                label: 'right/wrong ansers',
                data: countOfSelected,
                backgroundColor: [
                    'rgb(255, 99, 132)',
                    'rgb(54, 162, 235)',
                    'rgb(255, 205, 86)'
                ],
                hoverOffset: 4
            }]
        },
    });
}

function getOptions(i) {
    // возвращает списки вариантов ответа и количества выбора каждого из них
    const options = []
    const countOfSelected = []

    for (let j = 0; j < statistics.questions[i].options.length; j++) {

        const option = statistics.questions[i].options[j];
        const key = Object.keys(option)[0]; // получаем ключ (текст варианта ответа)
        options.push(key);
        countOfSelected.push(option[key].count_of_selected);
    }
    return [options, countOfSelected]
}