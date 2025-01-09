document.addEventListener('DOMContentLoaded', function() {
    const starButtons = document.querySelectorAll('.star-button');
    starButtons.forEach(button => {
        button.addEventListener('click', function() {
            const recipeId = this.getAttribute('data-recipe-id');
            fetch(`/favorite/${recipeId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': '{{ csrf_token() }}'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'added') {
                    this.innerHTML = '★';
                } else if (data.status === 'removed') {
                    this.innerHTML = '☆';
                }
            });
        });
    });
});