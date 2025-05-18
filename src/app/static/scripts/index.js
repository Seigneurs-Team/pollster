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



function searchPolls() {
    const tags = []
    $('#selected-tags').children().each((index, tag) => {
        tags.push($($(tag).children()[0]).text())
    })
    console.log('tags', tags)

    const watchedPolls = []
    $('.poll-item').each((index, poll) => {
        watchedPolls.push(poll.getAttribute('id'))
    })
    console.log('watchedPolls', watchedPolls)

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

    /*
{
  "list_of_polls": [
    {
      "name_of_poll": "string",
      "description": "string",
      "tags": [
        "string"
      ],
      "id_of_poll": 0,
      "id_of_author": 0,
      "nickname_of_author": "string",
      "cover": "string"
    }
  ]
}
    */
}


function renderPolls(listOfPolls) {
    // функция для отрисовки списка опросов при поиске/сбросе поиска. в обоих случаях опросы получаются соответствующим запросом к серверу


    listOfPolls.forEach(poll => {
        const pollTags = poll.tags.reduce((pollTags, tag) => {
            return pollTags += `<div class="tag">${tag}</div>
            `
        }, '')

        const pollEl = $(`
<li class="poll-item" id="${poll.id_of_poll}">
    <a href="passing_poll/${poll.id_of_poll}/">
        <!-- <div class="poll-img" data-image="data:image/png;base64,${poll.cover}"></div> -->
        <div class="poll-img"><img src="data:image/png;base64,${poll.cover}" alt="poll image"></div>
        <h2 class="poll-name">${poll.name_of_poll}</h2>
        <p class="poll-description">${poll.description}</p>
        <span class="poll-author">Автор: ${poll.nickname_of_author}</span>
        <div class="poll-tags">
            ${pollTags}
        </div>
    </a>
</li>
`)

        pollsDiv.append(pollEl);

    });
}