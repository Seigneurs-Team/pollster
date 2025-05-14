// api.js
export async function sendRequest(url, method, data = undefined, timeout = 0) {
    const controller = new AbortController();
    let timeoutId;

    if (timeout > 0) {
        timeoutId = setTimeout(() => controller.abort(), timeout);
    }

    const sendData = {
        method,
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        signal: controller.signal
    }
    if (data) {
        sendData.body = JSON.stringify(data)
    }

    try {
        const promise = await fetch(url, sendData);

        clearTimeout(timeoutId);
        console.log('promise:', promise)

        const responseJSON = await promise.json();
        console.log('json:', responseJSON)

        if (promise.status !== 200) {
            let errorMessage = responseJSON.message || responseJSON.response
            console.log('ошибка: ', errorMessage)
            throw new Error(errorMessage)
        }

        return responseJSON;
    } catch (error) {
        clearTimeout(timeoutId);
        throw error;
    }
}