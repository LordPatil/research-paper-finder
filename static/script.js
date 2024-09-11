document.getElementById("topicForm").addEventListener("submit", function (event) {
    event.preventDefault();
    const topic = document.getElementById("topic").value;

    fetch("/get_papers", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ topic })
    })
    .then(response => response.json())
    .then(data => {
        let resultDiv = document.getElementById("results");
        resultDiv.innerHTML = "";
        if (data.error) {
            resultDiv.textContent = data.error;
        } else {
            data.forEach((paper, index) => {
                let paperElement = document.createElement("div");
                paperElement.textContent = `${index + 1}. ${paper.title} - ${paper.authors.map(a => a.name).join(", ")}`;
                resultDiv.appendChild(paperElement);
            });
        }
    })
    .catch(error => console.error("Error fetching papers:", error));
});

