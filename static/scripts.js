document.addEventListener('DOMContentLoaded', function () {
    // Пример динамического обновления данных на странице
    const searchForm = document.querySelector('#search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function (event) {
            event.preventDefault();
            const query = document.querySelector('#search-query').value;

            fetch(`/search?query=${encodeURIComponent(query)}`)
                .then(response => response.text())
                .then(html => {
                    document.querySelector('#search-results').innerHTML = html;
                })
                .catch(error => console.error('Ошибка:', error));
        });
    }
});
