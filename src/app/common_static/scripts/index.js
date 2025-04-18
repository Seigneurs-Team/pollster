

// нажатие на кнопку filter
$(".opn-filter").on('click', function () {
    $(".popup").toggle();
});
$("#applyFilters").on('click', function () {
    $(".popup").toggle();
});

// добавление тэгов
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

$('.popup input').attr("disabled", "disabled")
$('.popup button').attr("disabled", "disabled")