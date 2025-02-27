// Шаг 1: Получить challenge от бэкенда
export async function getChallenge() {
    console.log('getting challenge...');

    const response = await fetch('/get_challenge', {
        method: 'GET',
        credentials: 'include', // Отправляем куки
    });

    if (!response.ok) {
        throw new Error('Ошибка при получении challenge');
    }

    const data = await response.json();
    console.log('Challenge received:', data);
    return data;
}

// Шаг 2: Найти nonce
export async function findProof(challenge) {
    let count = 0;
    const difficulty = challenge.count_of_bits;

    while (true) {
        const stringForHash = `${challenge.version}:${challenge.count_of_bits}:${challenge.timestamp}:${challenge.resource}:${challenge.extension}:${challenge.random_string}:${count}`;
        const hashValue = sha256(stringForHash); // Используй библиотеку для SHA-256

        if (hashValue.startsWith('0'.repeat(difficulty))) {
            console.log('Nonce found:', count);
            return count;
        } else {
            count++;
        }
    }
}
