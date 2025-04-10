import { sendRequest } from './api.js';

let statistics = {}


async function sendStatisticslRequest(id) {
    console.log('getting statistics...');
    try {
        const response = await sendRequest(`/get_statistics/${id}`, 'GET');
        return await response.json(); // Парсим JSON и возвращаем результат
    } catch (error) {
        console.error('Ошибка:', error);
        throw error; // Пробрасываем ошибку
    }
}

$(document).ready(async function () {
    const pollID = $('#get-statistics').data('poll-id')
    statistics = await sendStatisticslRequest(pollID)
    console.log('statistics',statistics)
    const questions = statistics.questions
    console.log('questions: ', questions)

    // отрисовываем графики
    for (let i = 0; i < questions.length; i++) {
        // у каждого вопроса,который есть в statistics (т.е. все, кроме long text) будет график соотношения правильных и неправильных ответов
        drawRightAnswersChart(questions, i)

        // а у вопросов с вариантами ответа будет второй график - количество выбора каждого варианта
        if (questions[i].type_of_question == "radio" || questions[i].type_of_question == "checkbox") {

            const [options, countOfSelected] = getOptions(i)
            drawOptionsChart(questions, i, options, countOfSelected)
        }
    }
})
    


function drawRightAnswersChart(questions, i) {
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

function drawOptionsChart(questions, i, options, countOfSelected) {
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