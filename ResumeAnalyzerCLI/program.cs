using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;
using iText.Kernel.Pdf;
using iText.Kernel.Pdf.Canvas.Parser;
using iText.Kernel.Pdf.Canvas.Parser.Data;
using iText.Kernel.Pdf.Canvas.Parser.Listener;
using DocumentFormat.OpenXml.Packaging;
using DocumentFormat.OpenXml.Wordprocessing;

namespace ResumeAnalyzer.CLI
{
    public class AnalysisResult
    {
        public Dictionary<string, List<string>> Sections { get; set; } = new();
        public List<string> FormattingErrors { get; set; } = new();
        public List<string> GrammarIssues { get; set; } = new();
        public string? Error { get; set; }
    }

    class Program
    {
        static void Main(string[] args)
        {
            try
            {
                if (args.Length < 2)
                {
                    throw new ArgumentException("Usage: <command> <filepath>\nCommands: parse, validate, grammar");
                }

                var command = args[0].ToLower();
                var filePath = args[1];
                var result = new AnalysisResult();

                ValidateFilePath(filePath);

                switch (command)
                {
                    case "parse":
                        result.Sections = ParseResumeSections(filePath);
                        break;
                    
                    case "validate":
                        result.FormattingErrors = ValidateFormatting(filePath);
                        break;
                    
                    case "grammar":
                        var text = ExtractText(filePath);
                        result.GrammarIssues = CheckGrammar(text);
                        break;
                        
                    default:
                        throw new ArgumentException($"Invalid command: {command}");
                }

                Console.WriteLine(JsonSerializer.Serialize(result));
            }
            catch (Exception ex)
            {
                var errorResult = new AnalysisResult
                {
                    Error = $"{ex.GetType().Name}: {ex.Message}"
                };
                Console.WriteLine(JsonSerializer.Serialize(errorResult));
                Environment.Exit(1);
            }
        }

        static void ValidateFilePath(string filePath)
        {
            if (!File.Exists(filePath))
                throw new FileNotFoundException("File not found", filePath);

            var extension = Path.GetExtension(filePath).ToLower();
            if (extension != ".pdf" && extension != ".docx")
                throw new NotSupportedException("Only PDF and DOCX files are supported");
        }

        static Dictionary<string, List<string>> ParseResumeSections(string filePath)
        {
            try 
            {
                var text = ExtractText(filePath);
                return new Dictionary<string, List<string>>
                {
                    ["experience"] = ExtractSection(text, "experience"),
                    ["education"] = ExtractSection(text, "education"),
                    ["skills"] = ExtractSection(text, "skills"),
                    ["summary"] = ExtractSection(text, "summary|objective")
                };
            }
            catch (Exception ex)
            {
                return new Dictionary<string, List<string>> 
                {
                    ["Error"] = new List<string> { ex.Message }
                };
            }
        }

        static string ExtractText(string filePath)
        {
            try
            {
                var path = Path.GetFullPath(filePath); // Normalize path
                return Path.GetExtension(path).ToLower() switch
                {
                    ".pdf" => ParsePdf(path),
                    ".docx" => ParseDocx(path),
                    _ => throw new NotSupportedException($"Unsupported file type: {Path.GetExtension(path)}")
                };
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Failed to extract text: {ex.Message}");
            }
        }

        static string ParsePdf(string filePath)
        {
            using var reader = new PdfReader(filePath);
            using var doc = new PdfDocument(reader);
            var text = new System.Text.StringBuilder();

            for (int i = 1; i <= doc.GetNumberOfPages(); i++)
            {
                text.AppendLine(PdfTextExtractor.GetTextFromPage(doc.GetPage(i)));
            }

            return text.ToString();
        }

        static string ParseDocx(string filePath)
        {
            try
            {
                using var doc = WordprocessingDocument.Open(filePath, false);
                var body = doc.MainDocumentPart?.Document.Body;
                return body?.InnerText ?? string.Empty;
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Failed to parse DOCX: {ex.Message}");
            }
        }

        static List<string> ExtractSection(string text, string sectionPattern)
        {
            var sectionHeader = new System.Text.RegularExpressions.Regex(
                $@"(?i)\b({sectionPattern})\b[^\n]*\n+(.*?)(?=\n\b\w+:|$)",
                System.Text.RegularExpressions.RegexOptions.Singleline
            );
            
            var match = sectionHeader.Match(text);
            return match.Success ? 
                ParseSectionItems(match.Groups[2].Value.Trim()) : 
                new List<string>();
        }

        static List<string> ParseSectionItems(string sectionText)
        {
            var items = new List<string>();
            var bulletRegex = new System.Text.RegularExpressions.Regex(
                @"(?m)^\s*[\u2022\u25CF•\-*]\s*(.+)$"
            );

            foreach (System.Text.RegularExpressions.Match m in bulletRegex.Matches(sectionText))
            {
                items.Add(m.Groups[1].Value.Trim());
            }

            return items.Count > 0 ? items : new List<string> { sectionText.Trim() };
        }

        static List<string> ValidateFormatting(string filePath)
        {
            var errors = new List<string>();
            var extension = Path.GetExtension(filePath).ToLower();

            if (extension == ".pdf")
            {
                using var reader = new PdfReader(filePath);
                using var doc = new PdfDocument(reader);
                
                var fonts = new HashSet<string>();
                var fontSizes = new HashSet<float>();

                for (int i = 1; i <= doc.GetNumberOfPages(); i++)
                {
                    var page = doc.GetPage(i);
                    var eventListener = new FilteredEventListener();
                    var fontProcessor = new FontAnalysisProcessor();
                    eventListener.AttachEventListener(fontProcessor);
                    
                    var parser = new PdfCanvasProcessor(eventListener);
                    parser.ProcessPageContent(page);
                    
                    fonts.UnionWith(fontProcessor.Fonts);
                    fontSizes.UnionWith(fontProcessor.FontSizes);
                }

                if (fonts.Count > 3)
                    errors.Add($"Too many fonts ({fonts.Count}) - Use maximum 2-3 fonts");
                
                if (fontSizes.Count > 4)
                    errors.Add($"Too many font sizes ({fontSizes.Count}) - Use 2-3 sizes max");
            }
            else if (extension == ".docx")
            {
                using var doc = WordprocessingDocument.Open(filePath, false);
                var stylesPart = doc.MainDocumentPart?.StyleDefinitionsPart;
                var styles = new HashSet<string>();

                if (stylesPart?.Styles != null)
                {
                    foreach (var style in stylesPart.Styles.Elements<Style>())
                    {
                        if (!string.IsNullOrEmpty(style.StyleId))
                            styles.Add(style.StyleId!);
                    }
                }

                if (styles.Count > 5)
                    errors.Add($"Too many paragraph styles ({styles.Count}) - Simplify formatting");
            }

            return errors.Count == 0 ? 
                new List<string> { "Good formatting consistency" } : 
                errors;
        }

        static List<string> CheckGrammar(string text)
        {
            var issues = new List<string>();
            
            if (text.Split(new[] { ' ', '\n' }, StringSplitOptions.RemoveEmptyEntries).Length < 100)
                issues.Add("Document seems too short - typical resumes have 200-500 words");
            
            if (System.Text.RegularExpressions.Regex.IsMatch(text, @"\b(I|my|me)\b", 
                System.Text.RegularExpressions.RegexOptions.IgnoreCase))
                issues.Add("Avoid first-person pronouns - use professional third-person");

            return issues;
        }
    }

    public class FontAnalysisProcessor : IEventListener, IContentOperator
    {
        public HashSet<string> Fonts { get; } = new();
        public HashSet<float> FontSizes { get; } = new();

        public void Invoke(
            PdfCanvasProcessor processor,
            PdfLiteral oper,
            IList<PdfObject> operands)
        {
            if (oper.ToString() == "Tf" && operands.Count >= 2)
            {
                var fontName = operands[0]?.ToString();
                if (!string.IsNullOrEmpty(fontName))
                    Fonts.Add(fontName);

                if (float.TryParse(operands[1]?.ToString(), out float size))
                    FontSizes.Add(size);
            }
        }

        public void EventOccurred(IEventData data, EventType type)
        {
            // Not used but required by interface
        }

        public ICollection<EventType> GetSupportedEvents()
        {
            return Array.Empty<EventType>();
        }
    }
}