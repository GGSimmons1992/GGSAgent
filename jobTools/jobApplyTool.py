from smolagents.tools import Tool
import requests
from bs4 import BeautifulSoup


class JobApplyTool(Tool):
    """Prepare a tailored cover letter and give apply instructions for a job posting"""

    name = "job_apply_helper"
    description = "Fetch a job posting and return a prepared cover letter (based on provided resume text) and application instructions."
    inputs = {
        "job_url": {"type": "string", "description": "URL of the job posting"},
        "resume_text": {
            "type": "string",
            "description": "Applicant resume text (optional)",
            "nullable": True,
        },
        "applicant_name": {
            "type": "string",
            "description": "Applicant name (optional)",
            "nullable": True,
        },
    }
    output_type = "string"

    def forward(
        self, job_url: str, resume_text: str = "", applicant_name: str = ""
    ) -> str:
        try:
            resp = requests.get(
                job_url, timeout=10, headers={"User-Agent": "GGSAgent/1.0"}
            )
            if resp.status_code != 200:
                return f"Failed to fetch job posting: status {resp.status_code}"
            soup = BeautifulSoup(resp.text, "html.parser")
            title = (
                soup.title.string.strip()
                if soup.title and soup.title.string
                else "(no title)"
            )
            # Try to extract main job description
            paragraphs = [
                p.get_text(separator=" ", strip=True)
                for p in soup.find_all(["p", "li"])
            ][:100]
            job_desc = "\n".join(paragraphs)[:3000]

            # Create a simple cover letter template (the model agent can improve it further)
            name_line = f"{applicant_name}" if applicant_name else "[Your Name]"
            letter = (
                f"Dear Hiring Manager,\n\n"
                f"I am writing to express my interest in the position titled '{title}'.\n\n"
                f"Based on the job description:\n{job_desc[:800]}\n\n"
                f"My background:\n{(resume_text[:800] + '...') if resume_text else '(resume not provided)'}\n\n"
                f"I believe I would be a strong fit for this role and would welcome the opportunity to discuss how my experience aligns with your needs.\n\n"
                f"Sincerely,\n{name_line}"
            )

            instructions = (
                "Application prepared. To apply:\n"
                f"1) Review the cover letter above and edit any personal details.\n"
                f"2) Submit via the application link: {job_url}\n"
                "3) If the job application requires a form, paste the cover letter into the message or cover letter field.\n"
                "If you want, I can try to open the application page with Selenium and attempt an automated submission, but that requires login and extra automation steps."
            )

            return f"Cover Letter:\n\n{letter}\n\nApply Instructions:\n{instructions}"
        except Exception as e:
            return f"Error preparing application materials: {str(e)}"
