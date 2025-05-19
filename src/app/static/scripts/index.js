import { sendRequest } from "./api.js";

// открытие и закрытие фильтров
$(".opn-popup").on('click', function () {
    $("#popup").toggleClass('popup__active');
});
$("#applyFilters").on('click', function () {
    $("#popup").toggleClass('popup__active');
});
const pollsDiv = $("#polls");



// Обработка выбора тегов
$('.tag').click(function () {
    if ($(this).parent().hasClass('not-selected-tags') && $('.selected-tags').children().length < 4) {
        $(this).appendTo('.selected-tags');
    } else if ($(this).parent().hasClass('selected-tags')) {
        $(this).appendTo('.not-selected-tags');
    }
})

// для неактивных фильтров
// $('.popup input').attr("disabled", "disabled")
// $('.popup button').attr("disabled", "disabled")


// Закрытие при клике вне
$(document).on('click', function (e) {
    if (!$(e.target).closest('.popup').length &&
        !$(e.target).hasClass('opn-popup') &&
        $('.popup').attr('class').includes('popup__active')) {
        console.log(!$(e.target).closest('.popup').length)
        console.log(!$(e.target).hasClass('opn-popup'))
        $(".popup").toggleClass('popup__active');
    }
});

// Запрещаем закрытие при клике внутри попапа
$(".popup").click(function (e) {
    e.stopPropagation();
});

$("#search-btn").click(searchPolls)

// Обработчик нажатия Enter в поле ввода
$("#search-input").keydown(function(event) {
    if (event.key === "Enter") {
        searchPolls(); // Вызываем функцию поиска
    }
});


function searchPolls() {
    const tags = []
    $('#selected-tags').children().each((index, tag) => {
        tags.push($($(tag).children()[0]).text())
    })
    console.log('tags', tags)

    let watchedPolls = []

    const data = {
        "name_of_poll_for_search": $('#search-input').val(),
        "tags": tags,
        "watched_polls": watchedPolls,
        "count_of_polls": 10
    }
    console.log('data', data)

    sendRequest('/search_polls', 'POST', data).then(responseJson => {
        const listOfPolls = responseJson.list_of_polls
        console.log('listOfPolls', listOfPolls)

        // очищаем список опросов и заполняем результатами поиска
        pollsDiv.empty()
        renderPolls(listOfPolls)
    })

    // обновляем watched polls для того чтобы когда юзер нажмет "еще" сразу достать готовый запрос из sessionstorage
    $('.poll-item').each((index, poll) => {
        watchedPolls.push(poll.getAttribute('id'))
    })
    console.log('new watchedPolls', watchedPolls)
    data["watched_polls"] = watchedPolls

    sessionStorage.currentRequest = JSON.stringify(data)
}


function renderPolls(listOfPolls) {
    // функция для добавления опросов на страницу

    listOfPolls.forEach(poll => {
        const pollTags = poll.tags.reduce((pollTags, tag) => {
            return pollTags += `<div class="tag">${tag}</div>
            `
        }, '')

        const pollEl = $(`
<li class="poll-item" id="${poll.id_of_poll}">
    <a href="passing_poll/${poll.id_of_poll}/">
        <div class="poll-img"><img src="data:image/png;base64,${poll.cover}" alt="poll image"></div>
        <h2 class="poll-name">${poll.name_of_poll}</h2>
        <p class="poll-description">${poll.description}</p>
    </a>
    <div class="poll-bottom">
        <div class="poll-bottom-left">
            <span class="poll-author">Автор: ${poll.nickname_of_author}</span>
            <div class="poll-tags">
                ${pollTags}
            </div>
        </div>
        <a href="/statistics/${poll.id_of_poll}" class="statistics-btn">
            <img class="warning-img"
                src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iMzMiIHZpZXdCb3g9IjAgMCAzMiAzMyIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4NCjxwYXRoIGQ9Ik0yNCAyNy4xNjY2VjEzLjgzMzNNMTYgMjcuMTY2NlY1LjgzMzI1TTggMjcuMTY2NlYxOS4xNjY2IiBzdHJva2U9IiMxRTFFMUUiIHN0cm9rZS13aWR0aD0iMyIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+DQo8L3N2Zz4NCg==">
        </a>
    </div>
</li>
`)

        pollsDiv.append(pollEl);

    });
}


$('#more').click(() => {
    const requestData = sessionStorage.currentRequest
    if (requestData) {
        sendRequest('/search_polls', 'POST', requestData).then(responseJson => {
        const listOfPolls = responseJson.list_of_polls
        console.log('new listOfPolls', listOfPolls)

        // добавляем результаты поиска
        renderPolls(listOfPolls)
    })
    }
})