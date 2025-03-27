document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("resumeForm");
    const fileInput = document.getElementById("resumeUpload");
    const jobDescription = document.getElementById("jobDescription");
    const loadingDiv = document.getElementById("loading");
    const resultsDiv = document.getElementById("results");
    const resultsContent = document.getElementById("resultsContent");

    form.addEventListener("submit", function (e) {
        e.preventDefault();

        if (fileInput.files.length === 0) {
            alert("Please upload a resume file.");
            return;
        }

        if (jobDescription.value.trim() === "") {
            alert("Please enter a job description.");
            return;
        }

        // Show loading and reset previous results
        resultsDiv.classList.add("hidden");
        loadingDiv.classList.remove("hidden");

        const formData = new FormData();
        formData.append("resume", fileInput.files[0]);
        formData.append("job_description", jobDescription.value);

        fetch("/analyze_resume", {
            method: "POST",
            body: formData,
        })
            .then((response) => response.json())
            .then((data) => {
                loadingDiv.classList.add("hidden");
                resultsDiv.classList.remove("hidden");

                if (data.error) {
                    resultsContent.innerHTML = `<p class="error"><strong>Error:</strong> ${data.error}</p>`;
                } else {
                    resultsContent.innerHTML = `
                        <h3>Analysis Results</h3>
                        <div class="result-section">
                            <p><strong>Score:</strong> ${data.score}</p>
                            <p><strong>Feedback:</strong> ${data.feedback}</p>
                        </div>
                        <div class="result-section">
                            <strong>Missing Keywords:</strong>
                            ${data.missing_keywords.length > 0 ? `
                                <ul>
                                    ${data.missing_keywords.map((kw) => `<li>${kw}</li>`).join("")}
                                </ul>
                            ` : `<p>✅ No missing keywords!</p>`}
                        </div>
                        <div class="result-section">
                            <strong>Formatting Feedback:</strong>
                            <ul>
                                ${data.formatting_feedback.map((fb) => `<li>${fb}</li>`).join("")}
                            </ul>
                        </div>
                    `;
                }
            })
            .catch((err) => {
                loadingDiv.classList.add("hidden");
                resultsDiv.classList.remove("hidden");
                resultsContent.innerHTML = `<p class="error"><strong>Error:</strong> Something went wrong. Please try again.</p>`;
                console.error(err);
            });
    });
});
