// отправка опроса на сервер
const host = 'http://127.0.0.1:8000';
import { hasHTMLTags } from './create_poll_page.js';
import { sendRequest } from './api.js';

async function sendCreatePollRequest(data) {
    const response = await sendRequest('/create_poll', 'POST', data);
    console.log('response:', response)
    console.log('response.status === 200', response.status === 200)
    // Обработка ответа от сервера
    if (response.status === 200) {
        // Успешное создание опроса
        alert('Опрос успешно создан')
        window.location.href = '/'; // Перенаправление на домашнюю страницу
    }
}


export function createPoll() {
    let questions = $('.question').map(function() {
        let $question = $(this);
        let type = $question.attr('data-type');
        let options = [];
        let hasImage = false;

        $question.find('.option, .option-img').each(function() { // TODO убрать этот общий блок, разбить на два блока :
            // $question.find('.option и $question.find('.option-img'
            // в первом добавляться (options.push) будет текст, во втором - картинка
            let optionData = {
                text: '', // Инициализируем пустой текст
                image: null
            };

            // Обработка разных типов вариантов
            if ($(this).hasClass('option-img')) {
                // Для вариантов с изображениями
                const fileInput = $(this).find('input[type="file"]');
                optionData.image = fileInput[0]?.files[0] || null;
                optionData.text = optionData.image ? optionData.image.name : '';
            } else {
                // Для обычных текстовых вариантов
                const textInput = $(this).find('.value');
                optionData.text = textInput.val() ? textInput.val().trim() : '';
            }

            options.push(optionData);
        });

        return {
            id: $question.attr('id'),
            type: type,
            text: $question.find('.questionText').val().trim(),
            options: options,
            hasImage: hasImage
        };
    }).get();
    let tags = [];

    // Перебираем все элементы, у которых id начинается с "tag-"
    $('.selected-tags [id^="tag-"]').each(function () {
        tags.push($(this).text().trim()); // получаем текст тэга
    });
    // Формируем FormData
    const pollData = new FormData();
    
    // Основные данные
    // TODO поменять структуру: делать не data и json в ней, а отдельные 'name', 'questions'
    pollData.append('data', JSON.stringify({
        name_of_poll: $('#pollTitle').val(),
        description: $('#pollDescription').val(),
        tags: tags,
        questions: questions.map(q => ({
            ...q,
            options: q.options.map(opt => ({
                text: opt.text,
                // Указываем только факт наличия изображения
                hasImage: !!opt.image 
            }))
        }))
    }));

    // Добавляем файлы в понятной структуре
    questions.forEach((q, qIndex) => {
        q.options.forEach((opt, optIndex) => {
            if (opt.image) {
                pollData.append(`questions[${qIndex}][options][${optIndex}][image]`, opt.image);
            }
        });
    });

    console.log('pollData',pollData)
    console.log('pollData.keys',pollData.keys)
    console.log('pollData.keys()',pollData.keys())

    pollData.forEach((item) => {
        console.log(item)
        console.log(pollData.get(item))
    })

    // Полный вывод содержимого FormData
console.log("Full FormData content:");
for (let [key, value] of pollData.entries()) {
    if (value instanceof File) {
        console.log(`${key} -> File: ${value.name} (${value.size} bytes, ${value.type})`);
    } else {
        console.log(`${key} -> ${value}`);
    }
}
    // Отправка
    sendCreatePollRequest(pollData);
}
function checkCorrectData(pollData, questions) {
    let isInvalid = false;
    let msg = '';

    // Проверка названия опроса
    if (!pollData.get('name_of_poll')?.trim()) {
        msg = 'Некорректно заполнена форма: Название опроса не может быть пустым!';
        isInvalid = true;
    }
    // Проверка наличия вопросов
    else if (!questions.length) {
        msg = 'Некорректно заполнена форма: Вы не добавили ни одного вопроса!';
        isInvalid = true;
    }
    // Проверка текстовых полей
    else {
        $(`.questions input[type="text"], .questions textarea`).each(function () {
            const value = $(this).val();
            if (!value.trim() && !$(this).hasClass('right-answer')) {
                isInvalid = true;
                msg = 'Некорректно заполнена форма: Пустые поля!';
                return false;  // Прерываем each
            }
        });

        // Проверка на HTML-теги
        $(`input[type="text"], textarea`).each(function () {
            if (hasHTMLTags($(this).val())) {
                isInvalid = true;
                msg = 'Некорректно заполнена форма: Недопустимые символы (например, < или >)!';
                return false;
            }
        });
    }

    if (isInvalid) {
        $('.error-message.submit').text(msg).show();
        console.error(msg);
        return false;
    } else {
        $('.error-message.submit').hide();
        return true;
    }
}