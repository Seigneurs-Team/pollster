import { sendRequest } from './api.js';

async function sendStatisticslRequest(id) {
    const response = await sendRequest(`/statistics/${id}`, 'GET');
    console.log('response:', response)
    // Обработка ответа от сервера
    if (response.status === 200) {
        alert('Статистика успешно получена')
    }
    return await response.json();

}


$('#get-statistics').on('click', async function () {
    console.log('getting statistics...')
    const pollID = $('#get-statistics').data('poll-id') 
    
    const response = await sendStatisticslRequest(pollID)
        console.log('Ответ сервера:', response);
})
