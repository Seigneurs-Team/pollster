// api.js
export async function sendRequest(url, method, data, timeout = 0) {
    const controller = new AbortController();
    let timeoutId;
    
    if (timeout > 0) {
        timeoutId = setTimeout(() => controller.abort(), timeout);
    }

    try {
        const response = await fetch(url, {
            method,
            headers: {'Content-Type': 'application/json'},
            credentials: 'include',
            body: JSON.stringify(data),
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        console.log(response)
        return response;
    } catch (error) {
        clearTimeout(timeoutId);
        throw error;
    }
}