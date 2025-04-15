import { sendRequest } from './api.js';

let statistics = {}
let questions = []

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
    const pollID = $('main').data('poll-id')
    statistics = await sendStatisticslRequest(pollID)
    console.log('statistics', statistics)
    questions = statistics.questions
    console.log('questions: ', questions)

    // отрисовываем графики
    for (let i = 0; i < questions.length; i++) {
        // у short text график с правлиьными/неправильными ответами
        if (questions[i].type_of_question == "short text") {

            drawRightAnswersChart(i)

        }
        // а у вопросов с вариантами ответа по умолчанию будет график - количество выбора каждого варианта
        if (questions[i].type_of_question == "radio" || questions[i].type_of_question == "checkbox") {

            const [options, countOfSelected] = getOptions(i)
            questions[i].options = options
            questions[i].countOfSelected = countOfSelected

            drawOptionsChart(i, options, countOfSelected)
        }
    }
})



function drawRightAnswersChart(i) {
    // количество выбранных правильных вариантов ответа: в labels всегда "right/wrong", в data 1й элемент - количество правльных, 2й - неправильных ответов. в вопросах с коротким ответом то же самое (но это для графика. а так все ответы будут списком выводиться)

    const myChart = new Chart($(`#${questions[i].id} .chart`), {
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
    $(`#${questions[i].id}`).data('chart', myChart);

}

function drawOptionsChart(i, options, countOfSelected, type = 'bar') {
    // количество выбранных вариантов ответа: нужно получить список вариантов ответа и список количества выбора каждого из них
    /// можно использовать типы bar, polarArea, pie, doughnut
    const myChart = new Chart($(`#${questions[i].id} .chart`), {
        type: type,
        data: {
            labels: options,
            datasets: [{
                label: 'options',
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
    $(`#${questions[i].id}`).data('chart', myChart);


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

$('.chart-settings button').on('click', function () {
    const chart = $(this).closest(`.question`).data('chart');
    chart.destroy()
    const id = $(this).closest(`.question`).attr('id');


    const type = $(this).attr('class')
    for (let i = 0; i < questions.length; i++) {
        if (questions[i].id == id) {
            drawOptionsChart(i, questions[i].options, questions[i].countOfSelected, type)
            break;
        }
    }

    // закрытие окна настроек диаграммы
    closeModal(this)
})


// Открытие модального окна для выбора типа вопроса
$(".opn-chart-settings").on('click', function () {
    $(this).closest('.question').children().find('.modal').show()
});

// Закрытие модального окна
$('.modal-close').on('click', function () {
    closeModal(this)
});

function closeModal(modal) {
    $(modal).closest('.modal').hide();
}