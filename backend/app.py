from __future__ import annotations

import uuid
from pathlib import Path

from flask import Flask, render_template, request, send_from_directory, url_for
from werkzeug.utils import secure_filename

from backend.business_card_generator import (
    LANG,
    generate_business_card,
    get_design_catalog,
    get_category_catalog,
    get_category_theme,
    normalize_design_category,
    random_design_ids,
    sanitize_filename,
)


BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "generated_cards"
PREVIEW_DIR = OUTPUT_DIR / "previews"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PREVIEW_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}

app = Flask(
    __name__,
    template_folder=str(FRONTEND_DIR / "templates"),
    static_folder=str(FRONTEND_DIR / "static"),
    static_url_path="/static",
)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024


def select_language(value: str | None) -> str:
    return value if value in LANG else "en"


def store_uploaded_photo(uploaded_file) -> Path | None:
    if not uploaded_file or not uploaded_file.filename:
        return None

    filename = secure_filename(uploaded_file.filename)
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_IMAGE_EXTENSIONS:
        suffix = ".png"

    destination = UPLOAD_DIR / f"{uuid.uuid4().hex}{suffix}"
    uploaded_file.save(destination)
    return destination


def cleanup_preview_batch(batch_id: str | None, design_ids: list[int]) -> None:
    if not batch_id:
        return

    for design_id in design_ids:
        preview_path = PREVIEW_DIR / f"{batch_id}_{design_id}.png"
        if preview_path.exists():
            preview_path.unlink(missing_ok=True)


@app.route("/", methods=["GET", "POST"])
def index():
    lang = select_language(request.values.get("lang", "es"))
    strings = LANG[lang]
    design_catalog = {item["id"]: item for item in get_design_catalog(lang)}
    category_options = get_category_catalog(lang)
    values = {
        "name": "",
        "title": "",
        "email": "",
        "phone": "",
    }
    preview_url = None
    download_url = None
    download_name = None
    success_message = None
    design_options: list[dict] = []
    selected_design = "0"
    form_stage = "preview"
    photo_ref = ""
    batch_id = ""
    design_ids_str = ""
    preferred_category = "all"
    preferred_category_label = next((item["name"] for item in category_options if item["id"] == "all"), "All styles")
    category_theme = get_category_theme(preferred_category)
    scroll_y = "0"

    if request.method == "POST":
        values = {
            "name": request.form.get("name", "").strip(),
            "title": request.form.get("title", "").strip(),
            "email": request.form.get("email", "").strip(),
            "phone": request.form.get("phone", "").strip(),
        }

        selected_design = request.form.get("design_id", "0").strip() or "0"
        form_stage = request.form.get("stage", "preview").strip() or "preview"
        photo_ref = request.form.get("photo_ref", "").strip()
        batch_id = request.form.get("batch_id", "").strip()
        design_ids_str = request.form.get("design_ids", "").strip()
        scroll_y = request.form.get("scroll_y", "0").strip() or "0"
        preferred_category = normalize_design_category(request.form.get("preferred_category", "all").strip())
        preferred_category_label = next((item["name"] for item in category_options if item["id"] == preferred_category), preferred_category_label)
        category_theme = get_category_theme(preferred_category)
        previous_design_ids = [int(value) for value in design_ids_str.split(",") if value.strip().isdigit()]

        if form_stage == "final":
            design_id = int(selected_design) if selected_design.isdigit() else 0
            photo_path = UPLOAD_DIR / photo_ref if photo_ref else None
            output_name = sanitize_filename(values["name"]) or strings["output_default"]
            output_file = OUTPUT_DIR / f"{output_name}_d{design_id}_{uuid.uuid4().hex[:8]}.png"

            generate_business_card(
                name=values["name"],
                title=values["title"],
                email=values["email"],
                phone=values["phone"],
                output_path=output_file,
                strings=strings,
                photo_path=photo_path,
                design_id=design_id,
                badge_text=strings["badge"],
            )
            preview_url = url_for("generated_file", filename=output_file.name)
            download_url = preview_url
            download_name = output_file.name
            success_message = strings["web_success"]
            cleanup_preview_batch(batch_id, previous_design_ids)
            if photo_path and photo_path.exists():
                photo_path.unlink(missing_ok=True)
            form_stage = "preview"
            photo_ref = ""
            batch_id = ""
            design_ids_str = ""
        else:
            uploaded_photo = request.files.get("photo")
            photo_path = store_uploaded_photo(uploaded_photo)
            photo_ref = photo_path.name if photo_path else ""
            batch_id = uuid.uuid4().hex
            design_ids = random_design_ids(preferred_category)
            design_ids_str = ",".join(str(value) for value in design_ids)
            cleanup_preview_batch(request.form.get("batch_id", "").strip(), previous_design_ids)

            for design_id in design_ids:
                preview_file = PREVIEW_DIR / f"{batch_id}_{design_id}.png"
                generate_business_card(
                    name=values["name"],
                    title=values["title"],
                    email=values["email"],
                    phone=values["phone"],
                    output_path=preview_file,
                    strings=strings,
                    photo_path=photo_path,
                    design_id=design_id,
                    badge_text=strings["badge"],
                )
                design_options.append(
                    {
                        "id": design_id,
                        "name": design_catalog[design_id]["name"],
                        "category": design_catalog[design_id]["category"],
                        "category_label": design_catalog[design_id]["category_label"],
                        "preview_url": url_for("generated_file", filename=f"previews/{preview_file.name}"),
                    }
                )
            selected_design = str(design_ids[0])
            form_stage = "final"

    return render_template(
        "index.html",
        strings=strings,
        lang=lang,
        values=values,
        preview_url=preview_url,
        download_url=download_url,
        download_name=download_name,
        success_message=success_message,
        design_options=design_options,
        selected_design=selected_design,
        form_stage=form_stage,
        photo_ref=photo_ref,
        batch_id=batch_id,
        design_ids_str=design_ids_str,
        category_options=category_options,
        preferred_category=preferred_category,
        preferred_category_label=preferred_category_label,
        category_theme=category_theme,
        scroll_y=scroll_y,
    )


@app.route("/generated/<path:filename>")
def generated_file(filename: str):
    return send_from_directory(OUTPUT_DIR, filename)


if __name__ == "__main__":
    app.run(debug=True)
