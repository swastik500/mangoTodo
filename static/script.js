document.addEventListener("DOMContentLoaded", function () {
    console.log("To-Do List App Loaded!");

    // Confirm before deleting a task
    document.querySelectorAll(".delete").forEach(button => {
        button.addEventListener("click", function (event) {
            if (!confirm("Are you sure you want to delete this task?")) {
                event.preventDefault();
            }
        });
    });
});
