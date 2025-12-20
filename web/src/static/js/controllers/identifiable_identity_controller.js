function get_all_identifiable_entities() {
    fetch(GET_ALL_IDENTIFIABLE_ENTITIES, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
    })
    .then(async response => {
        if (!response.ok) {
            const err = new Error(`HTTP error! Status: ${response.status}`);
            err.status = response.status;
            throw err;
        }
        return response.json();
    })
    .then(data => {
        return data;
    });
}