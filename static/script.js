// Form validation for search bar - checks if search input is empty on submit

// Sets up event listener for content loaded event which fires when HTML doc has been loaded
document.addEventListener("DOMContentLoaded", function () {
    const searchForm = document.querySelector("form[action='/search']"); // Selects form element with the attribute set to /search and assigns it the variable searchForm

    // Sets up event listener for the submit event on the searchForm
    searchForm.addEventListener("submit", function (event) {
        const query = searchForm.querySelector("input[name='query']").value.trim(); // Retrieves value of the input field 'query', trims whitespace, and assign to the query variable
        // Checks if query is empty string
        if (query === "") {
            alert("Search query cannot be empty"); // Displays alert message if empty string
            event.preventDefault(); // Prevents form from being submitted
        }
    });
});