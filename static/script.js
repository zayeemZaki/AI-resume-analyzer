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

            // Extract data
            const styleIssues = data.style_issues || [];
            const lineAnalysis = data.line_analysis || [];
            const formattingFeedback = data.formatting_feedback || [];
            const missingKeywords = data.missing_keywords || [];
            const atsScore = data.score || 0;
            const feedback = data.feedback || "No feedback available";

            // 1) Score & Overall Feedback card
            const scoreCard = `
              <div class="info-card info-score">
                <h4>ATS Compatibility Score</h4>
                <div class="info-body">
                  <p><strong>Score:</strong> ${atsScore}/100</p>
                  <p><strong>Overall Feedback:</strong> ${feedback}</p>
                </div>
              </div>
            `;

            // 2) Missing Keywords card
            const missingCard = `
              <div class="info-card info-missing">
                <h4>Missing Keywords</h4>
                <div class="info-body">
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
              </div>
            `;

            // 3) Bullet-by-Bullet Analysis
            let bulletAnalysisHtml = "<h4>Bullet-by-Bullet Analysis</h4>";
            if (styleIssues.length > 0) {
                bulletAnalysisHtml += `
                    <p><strong>Style Issues:</strong></p>
                    <ul>
                        ${styleIssues.map(issue => `<li>⚠️ ${issue}</li>`).join("")}
                    </ul>
                `;
            }
            if (lineAnalysis.length > 0) {
                bulletAnalysisHtml += `
                    <div class="suggestions-container">
                        ${lineAnalysis.map(entry => {
                            // Grammar block
                            let grammarHtml;
                            if (entry.grammar_errors && entry.grammar_errors.length > 0) {
                                grammarHtml = `
                                  <div class="analysis-grammar">
                                    <span class="analysis-label">Grammar Issues</span>
                                    <ul>
                                      ${entry.grammar_errors.map(err => `
                                        <li class="grammar-item">⚠️ ${err.message || err}</li>
                                      `).join("")}
                                    </ul>
                                  </div>
                                `;
                            } else {
                                grammarHtml = `<p class="analysis-grammar-ok">✅ No grammar issues found.</p>`;
                            }

                            // Improved text
                            const improvedBlock = `
                              <div class="analysis-improved">
                                <span class="analysis-label">Improved</span>
                                <p>${entry.paraphrased || "<i>No suggestion available</i>"}</p>
                              </div>
                            `;

                            // Changes/diff
                            let diffBlock = "";
                            if (entry.diff_html) {
                                diffBlock = `
                                  <div class="analysis-changes">
                                    <span class="analysis-label">Changes</span>
                                    <p>${entry.diff_html}</p>
                                  </div>
                                `;
                            }

                            return `
                              <div class="analysis-card">
                                <div class="analysis-header">
                                  <span class="analysis-label">Original</span>
                                  <p class="analysis-original">${entry.text}</p>
                                </div>
                                <div class="analysis-body">
                                  ${grammarHtml}
                                  ${improvedBlock}
                                  ${diffBlock}
                                </div>
                              </div>
                            `;
                        }).join("")}
                    </div>
                `;
            } else {
                bulletAnalysisHtml += `<p>✅ No bullet analysis available.</p>`;
            }

            const bulletCard = `
              <div class="info-card info-bullets">
                ${bulletAnalysisHtml}
              </div>
            `;

            // 4) Recommended Sections card
            const sectionsCard = `
              <div class="info-card info-sections">
                <h4>Resume Sections Recommendation</h4>
                <div class="info-body">
                  <p>We recommend including the following sections:</p>
                  <ul>
                    <li>EXPERIENCE</li>
                    <li>EDUCATION</li>
                    <li>SKILLS</li>
                    <li>PROJECTS</li>
                  </ul>
                  <p>
                    For more details, see
                    <a href="https://ocs.yale.edu/resources/stemconnect-technical-resume-sample/" target="_blank">
                      STEMConnect Technical Resume Sample
                    </a>.
                  </p>
                </div>
              </div>
            `;

            // 5) Formatting Issues card
            const formattingCard = `
              <div class="info-card info-formatting">
                <h4>Formatting Issues</h4>
                <div class="info-body">
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
              </div>
            `;

            // Final output
            resultsContent.innerHTML = `
              <h3>Analysis Results</h3>
              ${scoreCard}
              ${missingCard}
              ${bulletCard}
              ${sectionsCard}
              ${formattingCard}
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
