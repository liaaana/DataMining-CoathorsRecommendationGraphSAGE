document.addEventListener('DOMContentLoaded', function() {
    const button = document.getElementById('generateButton');
    const input = document.getElementById('nameInput');
    const output = document.getElementById('output');
    const buttonText = button.querySelector('.button-text');
    const loadingSpinner = button.querySelector('.loading-spinner');

    function setLoading(isLoading) {
        if (isLoading) {
            buttonText.style.display = 'none';
            loadingSpinner.style.display = 'block';
            button.disabled = true;
            input.disabled = true;
        } else {
            buttonText.style.display = 'block';
            loadingSpinner.style.display = 'none';
            button.disabled = false;
            input.disabled = false;
        }
    }

    async function handleSearch() {
        const name = input.value.trim();
        if (!name) {
            output.innerHTML = '<div class="error-message">Please enter your name</div>';
            return;
        }

        setLoading(true);
        try {
            const response = await fetch('/recommend', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ author: name })
            });

            if (!response.ok) {
                throw new Error('Failed to fetch collaborators');
            }

            const data = await response.json();
            if (!data.recommendations || data.recommendations.length === 0) {
                output.innerHTML = '<div class="no-results">No potential collaborators found</div>';
                return;
            }

            const html = `
                <ul class="collaborator-list">
                    ${data.recommendations.map(([name]) => `
                        <li class="collaborator-item">
                            <span class="collaborator-name">${name}</span>
                        </li>
                    `).join('')}
                </ul>
            `;
            output.innerHTML = html;
        } catch (error) {
            console.error('Error:', error);
            output.innerHTML = '<div class="error-message">Error finding collaborators. Please try again.</div>';
        } finally {
            setLoading(false);
        }
    }

    button.addEventListener('click', handleSearch);
    input.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleSearch();
        }
    });
});