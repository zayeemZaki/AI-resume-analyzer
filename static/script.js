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

            const grammar = data.grammar_issues || {};
            const styleIssues = grammar.style_issues || [];
            const grammarErrors = grammar.lines_with_grammar_errors || [];

            const hasStyleIssues = styleIssues.length > 0;
            const hasGrammarErrors = grammarErrors.length > 0;

            console.log("[DEBUG] Style issues:", styleIssues);
            console.log("[DEBUG] Grammar errors:", grammarErrors);

            // ✅ Safely build grammar HTML
            let grammarHtml = "";

            if (hasStyleIssues || hasGrammarErrors) {
                grammarHtml += "<strong>Grammar Issues:</strong>";

                if (hasStyleIssues) {
                    grammarHtml += `
                        <h4>Style Issues:</h4>
                        <ul>
                            ${styleIssues.map(si => `<li>⚠️ ${si}</li>`).join("")}
                        </ul>
                    `;
                }

                if (hasGrammarErrors) {
                    grammarHtml += `
                        <h4>Grammar Errors by Paragraph:</h4>
                        <ul>
                            ${grammarErrors.map(para => `
                                <li>
                                    <strong>Paragraph ${para.line_number}:</strong><br/>
                                    <pre>${para.text}</pre>
                                    ${para.errors.map(err => `
                                        <div style="margin-left: 10px;">
                                            <em>${err.message}</em><br/>
                                            <strong>Suggestion:</strong> ${err.suggestions.join(", ") || "None"}
                                        </div>
                                    `).join("")}
                                </li>
                            `).join("")}
                        </ul>
                    `;
                }
            } else {
                grammarHtml = `<p>✅ No grammar issues found!</p>`;
            }

            // 🧠 Final HTML
            resultsContent.innerHTML = `
                <h3>Analysis Results</h3>
                <div class="result-section">
                    <p><strong>ATS Compatibility Score:</strong> ${data.score}/100</p>
                    <p><strong>Overall Feedback:</strong> ${data.feedback || "No feedback available"}</p>
                </div>

                <div class="result-section">
                    <strong>Detected Resume Sections:</strong>
                    ${Object.keys(data.sections).length > 0 ? `
                        <ul class="section-list">
                            ${Object.keys(data.sections).map(section => `
                                <li><span class="section-name">${section}</span> (${data.sections[section].length} items)</li>
                            `).join("")}
                        </ul>
                    ` : `<p>❌ No sections detected</p>`}
                </div>

                <div class="result-section">
                    <strong>Missing Keywords:</strong>
                    ${data.missing_keywords.length > 0 ? `
                        <ul>
                            ${data.missing_keywords.map((kw) => `<li>${kw}</li>`).join("")}
                        </ul>
                    ` : `<p>✅ All important keywords matched!</p>`}
                </div>

                <div class="result-section">
                    ${grammarHtml}
                </div>

                <div class="result-section">
                    <strong>Formatting Issues:</strong>
                    ${data.formatting_feedback && data.formatting_feedback.length > 0 ? `
                        <ul>
                            ${data.formatting_feedback.map((fb) => `<li>${fb}</li>`).join("")}
                        </ul>
                    ` : `<p>✅ Perfect formatting!</p>`}
                </div>

                <div class="result-section">
                    <strong>Content Organization:</strong>
                    ${data.grouping_issues && data.grouping_issues.length > 0 ? `
                        <ul>
                            ${data.grouping_issues.map((issue) => `<li>${issue}</li>`).join("")}
                        </ul>
                    ` : `<p>✅ Content well-organized!</p>`}
                </div>

                <div class="result-section">
                    <strong>Writing Enhancements:</strong>
                    ${data.paraphrased_suggestions && data.paraphrased_suggestions.length > 0 ? `
                        <div class="suggestions-container">
                            ${data.paraphrased_suggestions.map(suggestion => `
                                <div class="suggestion-box">
                                    <div class="original-text">
                                        <em>Original:</em> ${suggestion.original}
                                    </div>
                                    <div class="suggestion-text">
                                        <em>Improved:</em> ${suggestion.suggestion}
                                    </div>
                                </div>
                            `).join("")}
                        </div>
                    ` : `<p>✅ No writing improvements needed!</p>`}
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
