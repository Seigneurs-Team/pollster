import { sendRequest } from './api.js';

const COLORS = [
    '#F678A7',
    '#4dc9f6',
    '#A155B9',

    '#62AEC5',
    '#ADD2E4',
    '#E64072',
    '#165BA9',
    '#FFA4B6',

    '#f67019',
    '#f53794',
    '#537bc4',
    '#acc236',
    '#166a8f',
    '#00a950',
    '#58595b',
    '#8549ba'
];

let statistics = {}
let questions = []
const chartsTypes = []

async function sendStatisticslRequest(id) {
    console.log('getting statistics...');

    return sendRequest(`/get_statistics/${id}`, 'GET')
        .then((statistics) => statistics)
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
            chartsTypes[i] = 'rw-answers'
        }
        // а у вопросов с вариантами ответа по умолчанию будет график - количество выбора каждого варианта
        if (questions[i].type_of_question == "radio" || questions[i].type_of_question == "checkbox") {

            const [options, countOfSelected] = getOptions(i)
            questions[i].options = options
            questions[i].countOfSelected = countOfSelected

            drawBarChart(i, options, countOfSelected)
            chartsTypes[i] = 'options'
        }
    }
})


// количество выбранных правильных вариантов ответа: в labels всегда "right/wrong", в data 1й элемент - количество правльных, 2й - неправильных ответов. в вопросах с коротким ответом то же самое (но это для графика. а так все ответы будут списком выводиться)
function drawRightAnswersChart(i, type = 'doughnut') {

    const myChart = new Chart($(`#${questions[i].id} .chart`), {
        type: type,
        data: {
            labels: [
                'right',
                'wrong'
            ],
            datasets: [{
                label: 'Ответило',
                data: [questions[i].num_of_right_answers, questions[i].num_of_wrong_answers],
                backgroundColor: COLORS,
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
                label: 'Выбрало',
                data: countOfSelected,
                backgroundColor: COLORS,
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
    const chartType = $(this).attr('class')


    for (let i = 0; i < questions.length; i++) {
        if (questions[i].id == id) {
            const questionType = questions[i]['type_of_question']

            if (questionType == 'short text') {
                drawRightAnswersChart(i, chartType)
            } else {
                drawOptionsChart(i, questions[i].options, questions[i].countOfSelected, chartType)
                break;
            }
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

$('.change-chart-data').on('click', function () {
    const chart = $(this).closest('.question').data('chart');
    const id = $(this).closest(`.question`).attr('id');
    const dataType = $(this).hasClass('chart-data-options') ? 'options' : 'rw-answers'


    changeChartData(this, chart, id, dataType)
})

// изменяет данные, по которым строится диаграмма: варианты ответа - правильные/неправильные ответы
function changeChartData(btn, chart, id, dataType) {
    console.log('Changing...')

    chart.destroy()

    // кнопки переключения 
    const chartDataRWAnswers = $(btn).closest('.question').children().find('.chart-data-rw-answers')
    const chartDataOptions = $(btn).closest('.question').children().find('.chart-data-options')

    for (let i = 0; i < questions.length; i++) {
        if (questions[i].id == id) {
            if (dataType == 'options') {
                drawBarChart(i, questions[i].options, questions[i].countOfSelected)

                // активная кнопка
                chartDataRWAnswers.removeClass('active')
                chartDataOptions.addClass('active')

            } else if (dataType == 'rw-answers') {
                drawRightAnswersChart(i)

                // активная кнопка
                chartDataOptions.removeClass('active')
                chartDataRWAnswers.addClass('active')
            }
            break;
        }
    }
}

function drawBarChart (i, options, countOfSelected) {
    // можно использовать типы bar, polarArea, pie, doughnut

    const datasets = []
    options.forEach((option, idx) => {
        datasets.push({
            label: option,
            data: [countOfSelected[idx]],
            backgroundColor: COLORS[idx],
            hoverOffset: 4
        })
    })

    const myChart = new Chart($(`#${questions[i].id} .chart`), {
        type: 'bar',
        data: {
            labels: ['Количество голосов'],
            datasets: datasets
        },
    });
    $(`#${questions[i].id}`).data('chart', myChart);


}