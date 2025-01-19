let currentQuestionBtn = null
let currentQuestionContent = null // переменная хранит вопрос, для которого сейчас выбирается тип вопроса в модальном окне. модалка открывается по нажатию на кнопку, а в эту переменную записывается родитель этой кнопки
let currentQuestionOptions = null
let questionType = null

const modalType = $("#choose-question-type-modal");
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

closeModalBtn.on('click', function () { modalType.hide();})

$(".answerType").on('click', function () {
    // обработка нажатия на кнопку выбора того или иного типа вопроса: рендеринг соответствующего контента, скрытие кнопки "выбрать тип ответа", затем назначение обработчиков событий, если были отрисованы чекбоксы или радиокнопки (событие нажатия на кнопку добавления варианта ответа)
    
    let questionType = $(this).attr('name')
    let questionId = $(currentQuestionBtn).parent('.question').attr('id')
    console.log('questionId: ', questionId)

    // после выбора типа ответа кнопка "тип ответа" скрывается, добавляется соответствующие интерфейс
    let content = questionContents(questionType, questionId)

    currentQuestionContent.append($(content));
    
    /* назначаем обработчики событий (на button которая добавляет option в checkbox и radiobutton) */
    $('.addOptionRadio').on('click', function () { addOption(this, 'radio')    })
    $('.addOptionCheckbox').on('click', function () { addOption(this, 'checkbox')    })

    // скрываем кнопку выбора типа вопроса. TODO в дальнейшем можно сделать так, чтобы ее текст менялся на "изменить тип вопроса", где при необходимости radio заменялись бы на checkbox и наоборот. но тогда нужно будет не только добавлять QuestionContent, но и перед этим извлекать его содержимое, затем удалять, и только потом добавлять новое
    $(currentQuestionBtn).hide()
    modalType.hide();

    // после генерации содержимого вопроса обнуляем currentQuestionBtn, currentQuestionContent
    currentQuestionBtn = null
    currentQuestionContent = null 
})


function questionContents(questionType, questionId) {
    //  - вопрос с развернутым ответом - добавляется надпись "вопрос с развернутым ответом"
    //  - вопрос с кратким текстовым ответом - input для ввода правильного ответа (если пользователь ничего не напишет, то правильного ответа нет. placeholder="введите правильный ответ (необязательно)")
    //  - checkbox: ul (минимум 2 li), после него кнопка "+" для добавления варианта ответа. выбранный(е) вариант(ы) считаются правильными
    //  - radiobutton:  тож самое. если картинки, то в ul добавляем поля для загрузки изображений. если не во все поля загружены изображения, будет выходить предупреждение

    if (questionType == "short text") {
        console.log('hi there')
        return '<input class="right-answer" type="text" maxlength="60" placeholder="введите правильный ответ (необязательно)">';
    } else if (questionType == "long text") {
        return '<p>Это вопрос с развернутым ответом</p>';

    } else if (questionType == "radiobutton") {
        // name равно индексу question, id должно быть уникально как в кажодой радиокнопке, так и в каждом вопросе, поэтому оно будет составляться из номера вопроса и номера кнопки {question_id}-{radiobutton_id}. в checkbox то же самое
        // TODO добавить кнопку "удалить" для option (и в checkbox тоже)
        return `
    <div class="options">
        <div class="option"><input type="radio" name="1" id="1_1"> <input type="text"
                for="1_1"></input>
        </div>
        <div class="option"><input type="radio" name="1" id="1_2"> <input type="text"
                for="1_2"></input></div>
    </div>
    <br><button class="addOptionRadio">+</button>
    `
    } else if (questionType == "checkbox") {
        return `
    <div class="options">
        <div class="option"><input type="checkbox" name="1" id="1_1"> <input type="text"
                for="1_1"></input>
        </div>
        <div class="option"><input type="checkbox" name="1" id="1_2"> <input type="text"
                for="1_2"></input></div>
    </div>
    <br><button class="addOptionCheckbox">+</button>
    `
    // TODO загрузка изображений
    } else if (questionType == "radiobutton img") {
        return 0

    } else if (questionType == "checkbox img") {
        return 0

    }

}



function addOption(target, type) {
    let options = $(target).closest('.question').find('.options'); // closest находит ближайший элемент .question. отличие от метода parent в том, что parent ищет только родительский элемент, а closest - также выше по иерархии.

    let optionsCount = options.find('.option').length;

    // Создаем новый вариант ответа
    optionsCount++; // Увеличиваем счетчик для нового варианта
    options.append($(`<div class="option">
        <input type="${type}" name="1" id="1_${optionsCount}">
        <input type="text" for="1_${optionsCount}">
    </div>`));
}
