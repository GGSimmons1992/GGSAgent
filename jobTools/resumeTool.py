from smolagents.tools import Tool
import re


class ResumeTool(Tool):
    """Tool for parsing resume text and extracting a concise summary"""

    name = "resume_parser"
    description = "Parse resume text and return a concise summary: name, contact, top skills, and experience highlights."
    inputs = {"resume_text": {"type": "string", "description": "Full resume text"}}
    output_type = "string"

    def forward(self, resume_text: str) -> str:
        try:
            text = resume_text or ""
            # Find email
            email_match = re.search(r"[\w\.-]+@[\w\.-]+", text)
            email = email_match.group(0) if email_match else "(not found)"

            # Find phone
            phone_match = re.search(r"(\+?\d[\d\-() ]{7,}\d)", text)
            phone = phone_match.group(0) if phone_match else "(not found)"

            # Very simple name guess: first line or 'Name:'
            name = "(not found)"
            lines = [l.strip() for l in text.splitlines() if l.strip()]
            if lines:
                # look for a line starting with Name:
                for ln in lines[:8]:
                    if ln.lower().startswith("name:"):
                        name = ln.split(":", 1)[1].strip()
                        break
                else:
                    # fallback to first line if it contains letters
                    if re.search(r"[A-Za-z]{2,}", lines[0]):
                        name = lines[0]

            # Extract skills section if present
            skills = []
            skills_section = re.search(
                r"skills[:\s\n]*(.+?)(?:\n\s*\n|experience:|education:|$)",
                text,
                re.I | re.S,
            )
            if skills_section:
                skills_text = skills_section.group(1)
                # split by commas or newlines
                parts = re.split(r"[,\n]", skills_text)
                skills = [p.strip() for p in parts if p.strip()][:20]
            else:
                # heuristic: find common skill keywords
                keywords = [
                    "python",
                    "java",
                    "javascript",
                    "react",
                    "aws",
                    "docker",
                    "kubernetes",
                    "sql",
                    "tensorflow",
                    "pytorch",
                ]
                for kw in keywords:
                    if re.search(rf"\b{kw}\b", text, re.I):
                        skills.append(kw)

            # Experience highlight: first 2-3 lines under Experience
            exp_highlights = ""
            exp_section = re.search(
                r"experience[:\s\n]*(.+?)(?:\n\s*\n|education:|$)", text, re.I | re.S
            )
            if exp_section:
                exp_text = exp_section.group(1).strip()
                lines = [l.strip() for l in exp_text.splitlines() if l.strip()]
                exp_highlights = " ".join(lines[:3])

            summary_lines = [f"Name: {name}", f"Email: {email}", f"Phone: {phone}"]
            if skills:
                summary_lines.append("Top skills: " + ", ".join(skills))
            if exp_highlights:
                summary_lines.append("Experience highlights: " + exp_highlights[:800])

            return "\n".join(summary_lines)
        except Exception as e:
            return f"Error parsing resume: {str(e)}"
