/* const del_btns = $(".delete-poll");


del_btns.on("click", function () {
    console.log('deleting poll...')
    let poll_id = $(event.currentTarget).attr('data-poll')
    console.log(poll_id);

    // тут на сервер отправляется запрос на удаление опроса по id
}); 
*/

$(window).on("load", function () { getChallenge(); });
function getChallenge() {
    console.log('page loaded')
    var Http = new XMLHttpRequest();
    var url = '/get_challenge'; // Эндпоинт для получения challenge

    Http.open('GET', url, true);
    Http.send();

    Http.onload = function () {
        if (Http.status === 200) {
            var response = JSON.parse(Http.response);
            console.log('Challenge received:', response);

            // Вызываем функцию для поиска nonce
            findProof(response);
        } else {
            console.error('Error getting challenge:', Http.statusText);
        }
    };
}