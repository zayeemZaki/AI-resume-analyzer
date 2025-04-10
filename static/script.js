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

        resultsDiv.classList.add("hidden");
        loadingDiv.classList.remove("hidden");

        const formData = new FormData();
        formData.append("resume", fileInput.files[0]);
        formData.append("job_description", jobDescription.value);

        fetch("/analyze_resume", {
            method: "POST",
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            loadingDiv.classList.add("hidden");
            resultsDiv.classList.remove("hidden");

            if (data.error) {
                resultsContent.innerHTML = `<p class="error"><strong>Error:</strong> ${data.error}</p>`;
                return;
            }

            // Grammar / bullet analysis
            const styleIssues = data.style_issues || [];
            const lineAnalysis = data.line_analysis || [];
            let bulletAnalysisHtml = "<strong>Bullet-by-Bullet Analysis:</strong>";

            // style issues
            if (styleIssues.length > 0) {
                bulletAnalysisHtml += `
                    <h4>Style Issues:</h4>
                    <ul>
                        ${styleIssues.map(issue => `<li>⚠️ ${issue}</li>`).join("")}
                    </ul>
                `;
            }
            // grammar line analysis
            if (lineAnalysis.length > 0) {
                bulletAnalysisHtml += `
                    <div class="suggestions-container">
                        ${lineAnalysis.map(entry => {
                            const grammarHtml =
                              entry.grammar_errors && entry.grammar_errors.length > 0
                                ? `
                                  <ul class="grammar-issues-list">
                                      ${entry.grammar_errors.map(err => `<li>⚠️ ${err.message || err}</li>`).join("")}
                                  </ul>
                                  `
                                : `<p class="no-issues">✅ No grammar issues found.</p>`;

                            const improvedHtml = entry.paraphrased
                                ? `<strong>Improved:</strong> ${entry.paraphrased}`
                                : `<strong>Improved:</strong> <i>No suggestion available</i>`;

                            const diffHtml = entry.diff_html
                                ? `<div class="diff-highlight"><strong>Changes:</strong><br/>${entry.diff_html}</div>`
                                : "";

                            return `
                                <div class="suggestion-box">
                                    <div class="original-text"><em>Original:</em> ${entry.text}</div>
                                    ${grammarHtml}
                                    <div class="suggestion-text">${improvedHtml}</div>
                                    ${diffHtml}
                                </div>
                            `;
                        }).join("")}
                    </div>
                `;
            } else {
                bulletAnalysisHtml += `<p>✅ No bullet analysis available.</p>`;
            }

            // recommended sections
            const recommendedSectionsHtml = `
                <div class="result-section">
                    <strong>Resume Sections Recommendation:</strong>
                    <p>We recommend including the following sections:
                    <ul>
                        <li>EXPERIENCE</li>
                        <li>EDUCATION</li>
                        <li>SKILLS</li>
                        <li>PROJECTS</li>
                    </ul>
                    For more details, see
                    <a href="https://ocs.yale.edu/resources/stemconnect-technical-resume-sample/" target="_blank">
                      STEMConnect Technical Resume Sample
                    </a>.
                    </p>
                </div>
            `;

            // Build final results
            const formattingFeedback = data.formatting_feedback || [];
            // REMOVED grouping_issues usage
            const missingKeywords = data.missing_keywords || [];
            const atsScore = data.score;
            const feedback = data.feedback || "No feedback available";

            resultsContent.innerHTML = `
                <h3>Analysis Results</h3>
                <div class="result-section">
                    <p><strong>ATS Compatibility Score:</strong> ${atsScore}/100</p>
                    <p><strong>Overall Feedback:</strong> ${feedback}</p>
                </div>

                <div class="result-section">
                    <strong>Missing Keywords:</strong>
                    ${
                      missingKeywords.length > 0
                      ? `
                        <ul>
                            ${missingKeywords.map(kw => `<li>${kw}</li>`).join("")}
                        </ul>
                        `
                      : `<p>✅ All important keywords matched!</p>`
                    }
                </div>

                <div class="result-section">
                    ${bulletAnalysisHtml}
                </div>

                ${recommendedSectionsHtml}

                <div class="result-section">
                    <strong>Formatting Issues:</strong>
                    ${
                      formattingFeedback.length > 0
                      ? `
                        <ul>
                            ${formattingFeedback.map(fb => `<li>${fb}</li>`).join("")}
                        </ul>
                        `
                      : `<p>✅ Perfect formatting!</p>`
                    }
                </div>
            `;
        })
        .catch(err => {
            loadingDiv.classList.add("hidden");
            resultsDiv.classList.remove("hidden");
            resultsContent.innerHTML = `<p class="error"><strong>Error:</strong> Something went wrong. Please try again.</p>`;
            console.error(err);
        });
    });
});
