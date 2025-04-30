

// нажатие на кнопку filter
$(".opn-popup").on('click', function () {
    $(".popup").toggleClass('popup__active');
});
$("#applyFilters").on('click', function () {
    $(".popup").toggleClass('popup__active');
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


// Закрытие при клике вне
$(document).on('click', function(e) {
    if (!$(e.target).closest('.popup').length && 
        !$(e.target).hasClass('opn-popup') && 
        $('.popup').attr('class').includes('popup__active')) {
            console.log(!$(e.target).closest('.popup').length)
            console.log(!$(e.target).hasClass('opn-popup'))
        $(".popup").toggleClass('popup__active');
    }
});

// Запрещаем закрытие при клике внутри попапа
$(".popup").click(function(e) {
    e.stopPropagation();
});