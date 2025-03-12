document.addEventListener("DOMContentLoaded", function () {
    const fileInput = document.getElementById("resumeUpload");
    const analyzeButton = document.getElementById("analyzeResume");
    const jobDescription = document.getElementById("jobDescription");
    const loadingDiv = document.getElementById("loading");
    const resultsDiv = document.getElementById("results");
    const resultsContent = document.getElementById("resultsContent");

    // Ensure loading is hidden at the start
    loadingDiv.style.display = "none";
    resultsDiv.style.display = "none";

    // **Enable the button when a file is selected**
    fileInput.addEventListener("change", function () {
        if (fileInput.files.length > 0) {
            analyzeButton.removeAttribute("disabled");
        } else {
            analyzeButton.setAttribute("disabled", "true");
        }
    });

    analyzeButton.addEventListener("click", function () {
        if (fileInput.files.length === 0) {
            alert("Please upload a resume file.");
            return;
        }
        if (jobDescription.value.trim() === "") {
            alert("Please enter a job description.");
            return;
        }

        // Show loading after clicking
        loadingDiv.style.display = "block";
        resultsDiv.style.display = "none";

        const formData = new FormData();
        formData.append("resume", fileInput.files[0]);
        formData.append("job_description", jobDescription.value);

        fetch("/analyze_resume", {
            method: "POST",
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                loadingDiv.style.display = "none";
                resultsDiv.style.display = "block";

                if (data.error) {
                    resultsContent.innerHTML = `<p style="color: red;"><strong>Error:</strong> ${data.error}</p>`;
                } else {
                    resultsContent.innerHTML = `
                        <div class="result-section">
                            <strong>Score:</strong> ${data.score}
                        </div>
                        <div class="result-section">
                            <strong>Feedback:</strong> ${data.feedback}
                        </div>
                        <div class="result-section">
                            <strong>Missing Keywords:</strong>
                            <ul>${data.missing_keywords.map(keyword => `<li>${keyword}</li>`).join('')}</ul>
                        </div>
                        <div class="result-section">
                            <strong>Formatting Feedback:</strong>
                            <ul>${data.formatting_feedback.map(feedback => `<li>${feedback}</li>`).join('')}</ul>
                        </div>
                    `;
                }
            })
            .catch(error => {
                loadingDiv.style.display = "none";
                resultsDiv.style.display = "block";
                resultsContent.innerHTML = `<p style="color: red;"><strong>Error:</strong> Something went wrong.</p>`;
                console.error("Error:", error);
            });
    });
});
