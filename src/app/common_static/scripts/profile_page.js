$("#your-polls-btn").on('click', function (event) { openTab(event,'your-polls');});
$("#completed-polls-btn").on('click', function (event) { openTab(event,'completed-polls');});
$(".log-out").on('click',  async function () {
    console.log('sending log out request...');
    const response = await fetch('/log_out', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        credentials: 'include', // Отправляем куки
    });
    const responseData = await response.json();
    console.log('Ответ сервера:', responseData); // Выводим ответ сервера в консоль

    if (!response.ok) {
        console.error('Ошибка при выходе из аккаунта:', responseData);
        throw new Error('Ошибка при выходе из аккаунта');
    }
});

$(".delete-account").on('click',  async function () {
    console.log('sending delete account request...');
    const response = await fetch('/delete_account', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        credentials: 'include', // Отправляем куки
    });
    const responseData = await response.json();
    console.log('Ответ сервера:', responseData); // Выводим ответ сервера в консоль

    if (!response.ok) {
        console.error('Ошибка при удалении аккаунта:', responseData);
        throw new Error('Ошибка при удалении аккаунта');
    }
});


function openTab(event, tabName) {
    // Hide all elements with class "tabcontent"
    $(".tabcontent").hide();

    // Remove "active" class from all elements with class "tablinks"
    $(".tablinks").removeClass("active");

    // Show the current tab, and add an "active" class to the button that opened the tab
    $(`#${tabName}`).show();
    $(event.currentTarget).addClass("active");
}

$(document).ready(function() {
    // по умолчанию вкладка "ваши опросы"
    $("#your-polls-btn").addClass("active");
    $("#your-polls").show()
})

$(".delete-poll").on('click', async function () {
    // Останавливаем всплытие события, чтобы предотвратить переход по ссылке
    event.stopPropagation();
    event.preventDefault();
    console.log('deleting poll...');
    const id = $(this).attr('data-poll');
console.log(id)

    const response = await fetch(`/delete_poll/${id}`, {
        method: 'GET',
        credentials: 'include', // Отправляем куки
    });
    const responseData = await response.json();
    console.log('Ответ сервера:', responseData); // Выводим ответ сервера в консоль

    if (!response.ok) {
        console.error('Ошибка при удалении опроса:', responseData);
        throw new Error('Ошибка при удалении опроса');
    }

    return responseData;
})

$('.tag').click(function() {
    // Проверяем, где находится текущий элемент
    if ($(this).parent().hasClass('not-selected-tags')) {
        // Если элемент в .not-selected-tags, перемещаем его в .selected-tags
        $(this).appendTo('.selected-tags');
    } else if ($(this).parent().hasClass('selected-tags')) {
        // Если элемент в .selected-tags, перемещаем его в .not-selected-tags
        $(this).appendTo('.not-selected-tags');
    }
});

// Фон шапки
$(document).ready(function() {
    $('header').css('background-image', 'url(' + $('header').data('background') + ')');
});