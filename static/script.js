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

            // 1) Build bullet-by-bullet analysis
            let bulletAnalysisHtml = "<strong>Bullet-by-Bullet Analysis:</strong>";

            // If we have style issues
            if (styleIssues.length > 0) {
                bulletAnalysisHtml += `
                    <h4>Style Issues:</h4>
                    <ul>
                        ${styleIssues.map(issue => `<li>⚠️ ${issue}</li>`).join("")}
                    </ul>
                `;
            }

            // If we have line-by-line analyses
            if (lineAnalysis.length > 0) {
                bulletAnalysisHtml += `
                    <div class="suggestions-container">
                        ${
                          lineAnalysis.map(entry => {
                            // Grammar block
                            let grammarHtml;
                            if (entry.grammar_errors && entry.grammar_errors.length > 0) {
                                grammarHtml = `
                                  <div class="analysis-grammar">
                                    <span class="analysis-label">Grammar Issues</span>
                                    <ul>
                                      ${
                                        entry.grammar_errors.map(err =>
                                          `<li class="grammar-item">⚠️ ${err.message || err}</li>`
                                        ).join("")
                                      }
                                    </ul>
                                  </div>
                                `;
                            } else {
                                grammarHtml = `
                                  <p class="analysis-grammar-ok">✅ No grammar issues found.</p>
                                `;
                            }

                            // Improved text block
                            const improvedBlock = `
                              <div class="analysis-improved">
                                <span class="analysis-label">Improved</span>
                                <p>${
                                  entry.paraphrased
                                  ? entry.paraphrased
                                  : "<i>No suggestion available</i>"
                                }</p>
                              </div>
                            `;

                            // Diff changes block (optional)
                            let diffBlock = "";
                            if (entry.diff_html) {
                                diffBlock = `
                                  <div class="analysis-changes">
                                    <span class="analysis-label">Changes</span>
                                    <p>${entry.diff_html}</p>
                                  </div>
                                `;
                            }

                            // Combine into final "analysis-card"
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
                          }).join("")
                        }
                    </div>
                `;
            } else {
                bulletAnalysisHtml += `<p>✅ No bullet analysis available.</p>`;
            }

            // 2) Build recommended sections block
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

            // 3) Final results HTML
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
