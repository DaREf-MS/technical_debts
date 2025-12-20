function get_commits_by_branch_name(branch_name) {
    fetch(GET_COMMITS_BY_BRANCH_NAME, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            branch_name: branch_name,
        })
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

function get_commits_by_branch_id(branch_id) {
    console.log('Fetching commits for branch_id:', branch_id);
    return fetch(GET_COMMITS_BY_BRANCH_ID, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            branch_id: branch_id,
        })
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
        console.log('Received commit data from API:', data);
        return data;
    });
}