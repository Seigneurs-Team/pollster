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
