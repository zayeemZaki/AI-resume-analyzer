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
        .then((response) => response.json())
        .then((data) => {
            loadingDiv.classList.add("hidden");
            resultsDiv.classList.remove("hidden");

            console.log("[DEBUG] Full backend response:", data);

            if (data.error) {
                resultsContent.innerHTML = `<p class="error"><strong>Error:</strong> ${data.error}</p>`;
                return;
            }

            // 1) Grab data from response
            const styleIssues = data.style_issues || [];
            const lineAnalysis = data.line_analysis || [];
            const metrics = data.metrics || {};
            console.log("[DEBUG] Style issues:", styleIssues);
            console.log("[DEBUG] Line analysis:", lineAnalysis);
            console.log("[DEBUG] Metrics:", metrics);

            // 2) Build bullet analysis HTML
            let bulletAnalysisHtml = "";
            if (styleIssues.length > 0 || lineAnalysis.length > 0) {
                bulletAnalysisHtml += "<strong>Bullet-by-Bullet Analysis:</strong>";

                // Show style issues
                if (styleIssues.length > 0) {
                    bulletAnalysisHtml += `
                        <h4>Style Issues:</h4>
                        <ul>
                            ${styleIssues.map(issue => `<li>⚠️ ${issue}</li>`).join("")}
                        </ul>
                    `;
                }

                // Show line-by-line analysis
                if (lineAnalysis.length > 0) {
                    bulletAnalysisHtml += `
                        <div class="suggestions-container">
                            ${lineAnalysis.map(entry => {

                                // Grammar error display
                                const grammarHtml = (entry.grammar_errors && entry.grammar_errors.length > 0)
                                    ? `
                                        <ul class="grammar-issues-list">
                                            ${entry.grammar_errors.map(err => `
                                                <li>⚠️ ${err.message || err}</li>
                                            `).join("")}
                                        </ul>
                                      `
                                    : `<p class="no-issues">✅ No grammar issues found.</p>`;

                                // Paraphrased suggestion
                                const improvedHtml = entry.paraphrased
                                    ? `<strong>Improved:</strong> ${entry.paraphrased}`
                                    : `<strong>Improved:</strong> <i>No suggestion available</i>`;

                                // Diff highlighting (if any)
                                // We'll store the HTML in entry.diff_html if your backend provides it
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
                }
            } else {
                bulletAnalysisHtml = `<p>✅ No bullet analysis available.</p>`;
            }

            // 3) Build the rest of your results (unchanged from your existing code)
            resultsContent.innerHTML = `
                <h3>Analysis Results</h3>
                <div class="result-section">
                    <p><strong>ATS Compatibility Score:</strong> ${data.score}/100</p>
                    <p><strong>Overall Feedback:</strong> ${data.feedback || "No feedback available"}</p>
                </div>

                <div class="result-section">
                    <strong>Detected Resume Sections:</strong>
                    ${
                        data.sections && Object.keys(data.sections).length > 0
                        ? `
                            <ul class="section-list">
                                ${Object.keys(data.sections).map(section => `
                                    <li><span class="section-name">${section}</span> (${data.sections[section].length} items)</li>
                                `).join("")}
                            </ul>
                          `
                        : `<p>❌ No sections detected</p>`
                    }
                </div>

                <div class="result-section">
                    <strong>Missing Keywords:</strong>
                    ${
                        data.missing_keywords && data.missing_keywords.length > 0
                        ? `
                            <ul>
                                ${data.missing_keywords.map(kw => `<li>${kw}</li>`).join("")}
                            </ul>
                          `
                        : `<p>✅ All important keywords matched!</p>`
                    }
                </div>

                <div class="result-section">
                    ${bulletAnalysisHtml}
                </div>

                <div class="result-section">
                    <strong>Formatting Issues:</strong>
                    ${
                        data.formatting_feedback && data.formatting_feedback.length > 0
                        ? `
                            <ul>
                                ${data.formatting_feedback.map(fb => `<li>${fb}</li>`).join("")}
                            </ul>
                          `
                        : `<p>✅ Perfect formatting!</p>`
                    }
                </div>

                <div class="result-section">
                    <strong>Content Organization:</strong>
                    ${
                        data.grouping_issues && data.grouping_issues.length > 0
                        ? `
                            <ul>
                                ${data.grouping_issues.map(issue => `<li>${issue}</li>`).join("")}
                            </ul>
                          `
                        : `<p>✅ Content well-organized!</p>`
                    }
                </div>
            `;
        })
        .catch((err) => {
            loadingDiv.classList.add("hidden");
            resultsDiv.classList.remove("hidden");
            resultsContent.innerHTML = `<p class="error"><strong>Error:</strong> Something went wrong. Please try again.</p>`;
            console.error(err);
        });
    });
});
