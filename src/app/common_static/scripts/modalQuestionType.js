let currentQuestionBtn = null
let currentQuestionContent = null // переменная хранит вопрос, для которого сейчас выбирается тип вопроса в модальном окне. модалка открывается по нажатию на кнопку, а в эту переменную записывается родитель этой кнопки
let questionType = null

const modalType = $("#choose-question-type-modal");
const openModalBtn = $('.chooseQuestionType')
const closeModalBtn = $('.modal-close')

$(window).on("click", function (event) {
    if (event.target == modalType[0]) {
        modalType.hide();
    }
});

export function showModal(target) {

    // кнопка "выберите тип вопроса", на которую только что нажали и контент соответствующего вопроса
    currentQuestionBtn = target
    currentQuestionContent = $(target).parent('.question').find('.questionContent');

    modalType.show();
}

openModalBtn.on('click', function () { showModal(this) })

closeModalBtn.on('click', function () {
    modalType.hide();
})

$(".answerType").on('click', function () {
    let questionType = $(this).attr('name')

    // после выбора типа ответа кнопка "тип ответа" скрывается, добавляется соответствующие интерфейс
    let content = questionContents(questionType)

    currentQuestionContent.append($(content));


    /* назначаем обработчики событий (как правило это нужно на button которая добавляет option в checkbox и radiobutton). тут надо поставить проверку на questionType */


    $('.addOptionRadio').on('click', function () {
        addOptionRadio()
    })

    $('.addOptionCheckbox').on('click', function () {
        addOptionCheckbox()
    })

    // if (questionType == "radiobutton") {

    // } else if (questionType == "checkbutton") {

    // }


    $(currentQuestionBtn).hide()
    modalType.hide();


    currentQuestionBtn = null
    currentQuestionContent = null // после генерации содержимого вопроса обнуляем currentQuestionContent
})


function questionContents(questionType) {
    //  - вопрос с развернутым ответом - добавляется надпись "вопрос с развернутым ответом"
    //  - вопрос с кратким текстовым ответом - input для ввода правильного ответа (если пользователь ничего не напишет, то правильного ответа нет. placeholder="введите правильный ответ (необязательно)")
    //  - checkbox: ul (минимум 2 li), после него кнопка "+" для добавления варианта ответа. выбранный(е) вариант(ы) считаются правильными
    //  - radiobutton:  тож самое. если картинки, то в ul добавляем поля для загрузки изображений. если не во все поля загружены изображения, будет выходить предупреждение

    if (questionType == "short text") {
        console.log('hi there')
        return '<input type="text" maxlength="60" placeholder="введите правильный ответ (необязательно)">';
    } else if (questionType == "long text") {
        return '<p>Это вопрос с развернутым ответом</p>';

    } else if (questionType == "radiobutton") {
        // TODO сделать не id="first", а name, и лучше id вообще удалить или присваивать униклаьный номер (хз как и зачем. лучше удалить)
        return '<div class="option"><input type="radio" name="1" id="first"><label for="first">first</label></div><div class="option"><input type="radio" name="1" id="second"><label for="second">second</label></div><br><button class="addOptionRadio">+</button>'

    } else if (questionType == "checkbutton") {
        return '<div class="option"><input type="checkbox" name="2" id="second"><label for="second">first</label></div><div class="option"><input type="checkbox" name="2" id="second"><label for="second">second</label></div><br><button class="addOptionCheckbox">+</button>'

    } else if (questionType == "radiobutton img") {
        return 0

    } else if (questionType == "checkbutton img") {
        return 0

    }

}



function addOptionRadio () {
    console.log('addOptionRadio clicked')

}

function addOptionCheckbox () {
    console.log('addOptionCheckbox clicked')

}
