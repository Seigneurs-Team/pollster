// api.js
export async function sendRequest(url, method, data) {
    const response = await fetch(url, {
        method,
        headers: {'Content-Type': 'application/json'},
        credentials: 'include',
        body: JSON.stringify(data),
    });

console.log('response', response)
    if (response.status!== 200) {
        throw new Error(`HTTP error! Status: ${response.status}`);
    }

    return response;
}