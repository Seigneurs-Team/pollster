/* const del_btns = $(".delete-poll");


del_btns.on("click", function () {
    console.log('deleting poll...')
    let poll_id = $(event.currentTarget).attr('data-poll')
    console.log(poll_id);

    // тут на сервер отправляется запрос на удаление опроса по id
}); 
*/

// нажатие на кнопку filter
$(".opn-filter").on('click', function () {
    $(".popup").toggle();
});
$("#applyFilters").on('click', function () {
    $(".popup").toggle();
});