$(document).ready(function() {
    $('#search-button').on('click', function() {
        let query = $('#search-input').val().trim();
        if (query.length > 0) {
            $.ajax({
                url: '/search',
                method: 'GET',
                data: { query: query },
                success: function(data) {
                    let resultsContainer = $('#search-results');
                    resultsContainer.empty();
                    if (data.length > 0) {
                        data.forEach(item => {
                            resultsContainer.append(`
                                <li class="list-group-item">
                                    <h5>${item.title}</h5>
                                    <p>${item.description}</p>
                                    <p><strong>Author:</strong> ${item.author}</p>
                                    <p><strong>Keywords:</strong> ${item.keywords}</p>
                                    <p><strong>Price:</strong> $${item.price}</p>
                                </li>
                            `);
                        });
                    } else {
                        resultsContainer.append('<li class="list-group-item">No results found</li>');
                    }
                },
                error: function() {
                    alert('Error fetching search results');
                }
            });
        } else {
            $('#search-results').empty().append('<li class="list-group-item">Please enter a search term</li>');
        }
    });
});
