"""Certificate Service"""

import os
import subprocess
from uuid import uuid4
from docxtpl import DocxTemplate
from jinja2 import StrictUndefined, Environment

from fastapi_keycloak import KeycloakUser

from ..models import CourseProgress, Certificate

from core import logger
from .file_service import save_certficate_in_minio


jinja_env = Environment()
jinja_env.undefined = StrictUndefined
jinja_env.trim_blocks = True
jinja_env.lstrip_blocks = True
jinja_env.filters["none_to_empty"] = lambda value: value or ""


async def generate_certificate(progress: CourseProgress, user: KeycloakUser):
    """Generate student certificate at the end of course"""

    output_dir = "tmp"

    try:
        template_path = "templates/leapfrog.docx"

        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template file not found: {template_path}")

        template = DocxTemplate(template_path)
        student_name = f"{user.firstName} {user.lastName}"
        context = {
            "student_name": student_name,
            "course": progress.course.name,
            "date": progress.end_date.created_at.strftime("%d/%m/%Y"),
        }

        template.render(context, jinja_env=jinja_env)

        student_ref = student_name.replace(" ", "_").upper()
        ref = str(uuid4()).split("-", maxsplit=1)[0].upper()
        output_filename_base = f"CERTFICATE_{student_ref}_{ref}"
        docx_filename = f"{output_filename_base}.docx"
        pdf_filename = f"{output_filename_base}.pdf"

        template.save(os.path.join(output_dir, docx_filename))

        subprocess.run(
            [
                "libreoffice",
                "--headless",
                "--convert-to",
                "pdf",
                os.path.join(output_dir, docx_filename),
                "--outdir",
                output_dir,
            ],
            check=True,
        )

        # Cleanup the temporary docx file
        os.remove(os.path.join(output_dir, docx_filename))

        logger.info("Generated file: %s", pdf_filename)

        certficate_url = await save_certficate_in_minio(output_dir + "/" + pdf_filename)

        if certficate_url:
            await Certificate(
                student_id=progress.student_id,
                course_id=progress.course_id,
                file_url=certficate_url,
            ).insert()
            logger.info("Generated Certifcated: %s", pdf_filename)
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        logger.error("Error generating item file: %s", e)
