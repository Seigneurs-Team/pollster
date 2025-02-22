/* const del_btns = $(".delete-poll");


del_btns.on("click", function () {
    console.log('deleting poll...')
    let poll_id = $(event.currentTarget).attr('data-poll')
    console.log(poll_id);

    // тут на сервер отправляется запрос на удаление опроса по id
}); 
*/

$(window).on("load", function () { getChallenge(); });

// Шаг 1: Получить challenge от бэкенда
function getChallenge() {
    // Установка куки
    document.cookie = "auth_sessionid=some_random_value; path=/;";
    console.log('page loaded')


    var Http = new XMLHttpRequest();
    var url = '/get_challenge'; // Эндпоинт для получения challenge

    Http.open('GET', url, true);

    Http.withCredentials = true;
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

// Шаг 2: Найти nonce
function findProof(challenge) {
    var count = 0;
    var difficulty = challenge.count_of_bits;

    function calculateHash() {
        var stringForHash = `${challenge.version}:${challenge.count_of_bits}:${challenge.timestamp}:${challenge.resource}:${challenge.extension}:${challenge.random_string}:${count}`;
        var hashValue = sha256(stringForHash); // Используй библиотеку для SHA-256

        if (hashValue.startsWith('0'.repeat(difficulty))) {
            console.log('Nonce found:', count);
        } else {
            count++;
            setTimeout(calculateHash, 0); // Асинхронно продолжаем поиск
        }
    }

    calculateHash();
}
