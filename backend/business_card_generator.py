from __future__ import annotations

import argparse
import os
import random
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


WIDTH = 1050
HEIGHT = 600

LANG = {
    "en": {
        "app_title": "Business Card Generator",
        "divider": "=======================",
        "choose_language": "Choose language / Elige idioma [en/es]: ",
        "language_invalid": "Invalid language. Using English.",
        "enter_info": "Enter your information:",
        "name": "Name",
        "title": "Title",
        "email": "Email",
        "phone": "Phone",
        "contact_section": "Contact Details",
        "panel_subtitle": "Contact at a glance",
        "generating": "Generating business card...",
        "saved": "Business card saved to:",
        "output_default": "business_card",
        "badge": "PROFILE",
        "web_page_title": "Business Card Studio",
        "web_page_subtitle": "Design a polished card in minutes with a photo frame and instant preview.",
        "web_hero_title": "Professional business cards, built in Python.",
        "web_hero_copy": "Enter your details, upload a headshot, and generate a clean card image with a premium layout.",
        "web_form_title": "Create your card",
        "web_preview_title": "Live preview",
        "web_photo_hint": "Optional photo. A square portrait works best.",
        "web_generate": "Generate card",
        "web_language": "Language",
        "web_download": "Download PNG",
        "web_new_card": "Create another card",
        "web_success": "Business card generated successfully.",
        "web_name_label": "Name",
        "web_title_label": "Title",
        "web_email_label": "Email",
        "web_phone_label": "Phone",
        "web_photo_label": "Photo",
        "web_category_label": "Design category",
        "web_category_hint": "Choose a style before generating the 10 previews.",
        "web_category_all": "All styles",
        "web_category_classic": "Classic",
        "web_category_modern": "Modern",
        "web_category_dark": "Dark",
        "web_feature_1_title": "Pillow rendering",
        "web_feature_1_text": "Generates a high-resolution PNG card.",
        "web_feature_2_title": "Photo framing",
        "web_feature_2_text": "Uploads are cropped into a clean portrait circle.",
        "web_feature_3_title": "Bilingual UI",
        "web_feature_3_text": "Switch the interface between English and Spanish.",
        "web_preview_empty": "Your generated card will appear here.",
        "web_designs_title": "Choose a design",
        "web_designs_copy": "Ten random variations are generated from your data. Pick the one you want to finish.",
        "web_filter_label": "Filter by style",
        "web_filter_all": "All",
        "web_filter_classic": "Classic",
        "web_filter_modern": "Modern",
        "web_filter_dark": "Dark",
        "web_filter_empty": "No designs match this filter.",
        "web_generate_designs": "Generate 10 designs",
        "web_generate_filtered_designs": "Generate designs",
        "web_create_selected": "Create selected card",
        "web_start_over": "Start over",
        "web_selected_design": "Selected design",
    },
    "es": {
        "app_title": "Generador de Tarjetas de Presentacion",
        "divider": "=======================",
        "choose_language": "Choose language / Elige idioma [en/es]: ",
        "language_invalid": "Idioma invalido. Se usara ingles.",
        "enter_info": "Ingresa tu informacion:",
        "name": "Nombre",
        "title": "Cargo",
        "email": "Correo",
        "phone": "Telefono",
        "contact_section": "Datos de Contacto",
        "panel_subtitle": "Contacto rapido",
        "generating": "Generando tarjeta de presentacion...",
        "saved": "Tarjeta guardada en:",
        "output_default": "tarjeta_presentacion",
        "badge": "PERFIL",
        "web_page_title": "Estudio de Tarjetas de Presentacion",
        "web_page_subtitle": "Disena una tarjeta profesional en minutos con foto y vista previa inmediata.",
        "web_hero_title": "Tarjetas profesionales creadas con Python.",
        "web_hero_copy": "Ingresa tus datos, sube una foto y genera una tarjeta limpia con aspecto premium.",
        "web_form_title": "Crear tarjeta",
        "web_preview_title": "Vista previa",
        "web_photo_hint": "Foto opcional. Funciona mejor un retrato cuadrado.",
        "web_generate": "Generar tarjeta",
        "web_language": "Idioma",
        "web_download": "Descargar PNG",
        "web_new_card": "Crear otra tarjeta",
        "web_success": "Tarjeta generada correctamente.",
        "web_name_label": "Nombre",
        "web_title_label": "Cargo",
        "web_email_label": "Correo",
        "web_phone_label": "Telefono",
        "web_photo_label": "Foto",
        "web_category_label": "Categoria de diseno",
        "web_category_hint": "Elige un estilo antes de generar las 10 vistas previas.",
        "web_category_all": "Todos los estilos",
        "web_category_classic": "Clasico",
        "web_category_modern": "Moderno",
        "web_category_dark": "Oscuro",
        "web_feature_1_title": "Renderizado con Pillow",
        "web_feature_1_text": "Genera una tarjeta PNG en alta resolucion.",
        "web_feature_2_title": "Encuadre de foto",
        "web_feature_2_text": "Las imagenes se recortan en un circulo limpio de retrato.",
        "web_feature_3_title": "Interfaz bilingue",
        "web_feature_3_text": "Cambia la interfaz entre ingles y espanol.",
        "web_preview_empty": "La tarjeta generada aparecera aqui.",
        "web_designs_title": "Elige un diseno",
        "web_designs_copy": "Se generan diez variantes aleatorias con tus datos. Elige la que quieras finalizar.",
        "web_filter_label": "Filtra por estilo",
        "web_filter_all": "Todos",
        "web_filter_classic": "Clasico",
        "web_filter_modern": "Moderno",
        "web_filter_dark": "Oscuro",
        "web_filter_empty": "No hay disenos para este filtro.",
        "web_generate_designs": "Generar 10 disenos",
        "web_generate_filtered_designs": "Generar disenos",
        "web_create_selected": "Crear tarjeta seleccionada",
        "web_start_over": "Empezar de nuevo",
        "web_selected_design": "Diseno seleccionado",
    },
}


CATEGORY_LABELS = {
    "classic": {"en": "Classic", "es": "Clasico"},
    "modern": {"en": "Modern", "es": "Moderno"},
    "dark": {"en": "Dark", "es": "Oscuro"},
}

CATEGORY_THEME = {
    "all": {
        "primary": "#1b5f9b",
        "secondary": "#2e7db4",
        "tint": "rgba(87, 169, 255, 0.10)",
        "text": "#1b5f9b",
        "surface": "rgba(232, 239, 246, 0.88)",
        "border": "rgba(27, 95, 155, 0.10)",
        "button_text": "#ffffff",
    },
    "classic": {
        "primary": "#6c5ce7",
        "secondary": "#a29bfe",
        "tint": "rgba(108, 92, 231, 0.10)",
        "text": "#5b4fd1",
        "surface": "rgba(241, 239, 255, 0.92)",
        "border": "rgba(108, 92, 231, 0.12)",
        "button_text": "#ffffff",
    },
    "modern": {
        "primary": "#0f9d8a",
        "secondary": "#39c5b1",
        "tint": "rgba(15, 157, 138, 0.10)",
        "text": "#0f8b7a",
        "surface": "rgba(233, 248, 245, 0.92)",
        "border": "rgba(15, 157, 138, 0.12)",
        "button_text": "#ffffff",
    },
    "dark": {
        "primary": "#243447",
        "secondary": "#51657d",
        "tint": "rgba(36, 52, 71, 0.12)",
        "text": "#243447",
        "surface": "rgba(236, 241, 246, 0.92)",
        "border": "rgba(36, 52, 71, 0.12)",
        "button_text": "#ffffff",
    },
}

CATEGORY_ORDER = ("all", "classic", "modern", "dark")


DESIGN_PRESETS = [
    {
        "id": 0,
        "name_en": "Ocean Split",
        "name_es": "Division Oceano",
        "category": "modern",
        "panel_side": "left",
        "panel_width": 332,
        "bg_top": (239, 244, 250),
        "bg_bottom": (224, 234, 244),
        "panel_main": "#173b5f",
        "panel_alt": "#1f5d89",
        "panel_corner": "#0f2740",
        "accent": "#f4c542",
        "row_accent": "#2e7db4",
        "badge_bg": "#0f2740",
        "badge_align": "center",
        "avatar_fill": "#2e7db4",
        "avatar_secondary": "#1f5d89",
        "card_outline": "#d6e0ea",
        "row_fill": "#f8fbfd",
        "row_outline": "#dce5ef",
        "text_dark": "#18324a",
        "text_light": "#ffffff",
    },
    {
        "id": 1,
        "name_en": "Graphite Split",
        "name_es": "Division Grafito",
        "category": "dark",
        "panel_side": "left",
        "panel_width": 346,
        "bg_top": (245, 247, 250),
        "bg_bottom": (227, 232, 239),
        "panel_main": "#222b36",
        "panel_alt": "#3a4654",
        "panel_corner": "#11161d",
        "accent": "#7dd3fc",
        "row_accent": "#4f7cff",
        "badge_bg": "#11161d",
        "badge_align": "center",
        "avatar_fill": "#4f7cff",
        "avatar_secondary": "#2a3550",
        "card_outline": "#d8dee8",
        "row_fill": "#fbfcfe",
        "row_outline": "#e2e8f0",
        "text_dark": "#16212b",
        "text_light": "#f7fbff",
    },
    {
        "id": 2,
        "name_en": "Emerald Split",
        "name_es": "Division Esmeralda",
        "category": "modern",
        "panel_side": "left",
        "panel_width": 320,
        "bg_top": (239, 249, 246),
        "bg_bottom": (220, 235, 229),
        "panel_main": "#114c43",
        "panel_alt": "#1b7a67",
        "panel_corner": "#0b2d28",
        "accent": "#f97316",
        "row_accent": "#1f9d6a",
        "badge_bg": "#0b2d28",
        "badge_align": "center",
        "avatar_fill": "#1f9d6a",
        "avatar_secondary": "#114c43",
        "card_outline": "#d8e7e1",
        "row_fill": "#f7fbfa",
        "row_outline": "#d8e7e1",
        "text_dark": "#17352f",
        "text_light": "#ffffff",
    },
    {
        "id": 3,
        "name_en": "Midnight Mirror",
        "name_es": "Espejo Medianoche",
        "category": "dark",
        "panel_side": "right",
        "panel_width": 342,
        "bg_top": (236, 240, 248),
        "bg_bottom": (221, 228, 241),
        "panel_main": "#1d3557",
        "panel_alt": "#457b9d",
        "panel_corner": "#0f1f33",
        "accent": "#f4a261",
        "row_accent": "#2a9d8f",
        "badge_bg": "#0f1f33",
        "badge_align": "center",
        "avatar_fill": "#2a9d8f",
        "avatar_secondary": "#1d3557",
        "card_outline": "#d9e1ea",
        "row_fill": "#f9fbfd",
        "row_outline": "#dfe6ef",
        "text_dark": "#17324a",
        "text_light": "#ffffff",
    },
    {
        "id": 4,
        "name_en": "Amber Mirror",
        "name_es": "Espejo Ambar",
        "category": "classic",
        "panel_side": "right",
        "panel_width": 328,
        "bg_top": (249, 245, 237),
        "bg_bottom": (236, 228, 215),
        "panel_main": "#5c3d2e",
        "panel_alt": "#a97155",
        "panel_corner": "#342319",
        "accent": "#d97706",
        "row_accent": "#f59e0b",
        "badge_bg": "#342319",
        "badge_align": "center",
        "avatar_fill": "#f59e0b",
        "avatar_secondary": "#a97155",
        "card_outline": "#e8dccf",
        "row_fill": "#fffdf9",
        "row_outline": "#eadfce",
        "text_dark": "#4d3629",
        "text_light": "#fffaf2",
    },
    {
        "id": 5,
        "name_en": "Coral Mirror",
        "name_es": "Espejo Coral",
        "category": "modern",
        "panel_side": "right",
        "panel_width": 332,
        "bg_top": (250, 241, 241),
        "bg_bottom": (239, 224, 224),
        "panel_main": "#7f1d1d",
        "panel_alt": "#c2410c",
        "panel_corner": "#4c1010",
        "accent": "#fb7185",
        "row_accent": "#e11d48",
        "badge_bg": "#4c1010",
        "badge_align": "center",
        "avatar_fill": "#e11d48",
        "avatar_secondary": "#c2410c",
        "card_outline": "#ead5d5",
        "row_fill": "#fffafa",
        "row_outline": "#f0dede",
        "text_dark": "#572323",
        "text_light": "#fff8f8",
    },
    {
        "id": 6,
        "name_en": "Soft Frame",
        "name_es": "Marco Suave",
        "category": "classic",
        "panel_side": "left",
        "panel_width": 304,
        "bg_top": (247, 250, 253),
        "bg_bottom": (232, 238, 245),
        "panel_main": "#3b82f6",
        "panel_alt": "#60a5fa",
        "panel_corner": "#1d4ed8",
        "accent": "#0f172a",
        "row_accent": "#3b82f6",
        "badge_bg": "#1d4ed8",
        "badge_align": "center",
        "avatar_fill": "#3b82f6",
        "avatar_secondary": "#1d4ed8",
        "card_outline": "#d8e2ee",
        "row_fill": "#fcfdff",
        "row_outline": "#d8e2ee",
        "text_dark": "#1e293b",
        "text_light": "#ffffff",
    },
    {
        "id": 7,
        "name_en": "Jade Frame",
        "name_es": "Marco Jade",
        "category": "modern",
        "panel_side": "left",
        "panel_width": 338,
        "bg_top": (241, 250, 247),
        "bg_bottom": (224, 238, 232),
        "panel_main": "#0f766e",
        "panel_alt": "#14b8a6",
        "panel_corner": "#115e59",
        "accent": "#f59e0b",
        "row_accent": "#0f766e",
        "badge_bg": "#115e59",
        "badge_align": "center",
        "avatar_fill": "#14b8a6",
        "avatar_secondary": "#0f766e",
        "card_outline": "#d7e8e3",
        "row_fill": "#fbfdfc",
        "row_outline": "#d7e8e3",
        "text_dark": "#18403b",
        "text_light": "#f6fffd",
    },
    {
        "id": 8,
        "name_en": "Classic Frame",
        "name_es": "Marco Clasico",
        "category": "classic",
        "panel_side": "right",
        "panel_width": 314,
        "bg_top": (250, 250, 247),
        "bg_bottom": (235, 234, 228),
        "panel_main": "#334155",
        "panel_alt": "#64748b",
        "panel_corner": "#1e293b",
        "accent": "#c8a96a",
        "row_accent": "#334155",
        "badge_bg": "#1e293b",
        "badge_align": "center",
        "avatar_fill": "#334155",
        "avatar_secondary": "#64748b",
        "card_outline": "#e1ded8",
        "row_fill": "#fffdf8",
        "row_outline": "#e6e2da",
        "text_dark": "#2b3645",
        "text_light": "#fffdf7",
    },
    {
        "id": 9,
        "name_en": "Violet Frame",
        "name_es": "Marco Violeta",
        "category": "dark",
        "panel_side": "right",
        "panel_width": 338,
        "bg_top": (247, 243, 252),
        "bg_bottom": (232, 225, 244),
        "panel_main": "#5b21b6",
        "panel_alt": "#8b5cf6",
        "panel_corner": "#37106f",
        "accent": "#f59e0b",
        "row_accent": "#7c3aed",
        "badge_bg": "#37106f",
        "badge_align": "center",
        "avatar_fill": "#7c3aed",
        "avatar_secondary": "#5b21b6",
        "card_outline": "#dfd7f0",
        "row_fill": "#fcfbff",
        "row_outline": "#e7def7",
        "text_dark": "#31224f",
        "text_light": "#fbf8ff",
    },
]


def get_design_preset(design_id: int) -> dict:
    return DESIGN_PRESETS[design_id % len(DESIGN_PRESETS)]


def get_design_catalog(lang: str) -> list[dict]:
    catalog = []
    for preset in DESIGN_PRESETS:
        catalog.append(
            {
                "id": preset["id"],
                "name": preset["name_es"] if lang == "es" else preset["name_en"],
                "category": preset["category"],
                "category_label": CATEGORY_LABELS[preset["category"]][lang],
            }
        )
    return catalog


def get_category_catalog(lang: str) -> list[dict]:
    return [
        {"id": "all", "name": LANG[lang]["web_category_all"]},
        {"id": "classic", "name": LANG[lang]["web_category_classic"]},
        {"id": "modern", "name": LANG[lang]["web_category_modern"]},
        {"id": "dark", "name": LANG[lang]["web_category_dark"]},
    ]


def normalize_design_category(value: str | None) -> str:
    if value in CATEGORY_ORDER:
        return value
    return "all"


def get_category_theme(value: str | None) -> dict:
    category = normalize_design_category(value)
    return CATEGORY_THEME[category]


def random_design_ids(preferred_category: str = "all") -> list[int]:
    ids = [preset["id"] for preset in DESIGN_PRESETS]
    random.shuffle(ids)
    category = normalize_design_category(preferred_category)
    if category == "all":
        return ids

    preferred_ids = [preset["id"] for preset in DESIGN_PRESETS if preset["category"] == category]
    random.shuffle(preferred_ids)
    return preferred_ids


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a business card image.")
    parser.add_argument(
        "--lang",
        "-l",
        choices=("en", "es"),
        help="Interface language.",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output PNG file path. Defaults to a name based on the provided person.",
    )
    parser.add_argument(
        "--photo",
        "-p",
        help="Optional photo path to frame inside the card.",
    )
    parser.add_argument(
        "--design",
        "-d",
        type=int,
        default=0,
        help="Design preset id (0-9).",
    )
    return parser.parse_args()


def select_language(value: str | None) -> str:
    if value in LANG:
        return value

    choice = input(LANG["en"]["choose_language"]).strip().lower()
    if choice in LANG:
        return choice

    print(LANG["en"]["language_invalid"])
    return "en"


def prompt_text(prompt: str) -> str:
    value = input(f"{prompt}: ").strip()
    while not value:
        value = input(f"{prompt}: ").strip()
    return value


def sanitize_filename(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower()).strip("_")
    return slug or "business_card"


def split_full_name(full_name: str) -> tuple[str, str]:
    parts = [part for part in re.split(r"\s+", full_name.strip()) if part]
    if len(parts) <= 1:
        return full_name.strip(), ""
    if len(parts) == 2:
        return parts[0], parts[1]
    if len(parts) == 3:
        return " ".join(parts[:2]), parts[2]
    return " ".join(parts[:-2]), " ".join(parts[-2:])


def initials_from_name(full_name: str) -> str:
    parts = [part for part in re.split(r"\s+", full_name.strip()) if part]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return f"{parts[0][0]}{parts[-1][0]}".upper()


def find_font(candidates: list[str], size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            try:
                return ImageFont.truetype(str(path), size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def get_fonts() -> dict[str, ImageFont.FreeTypeFont | ImageFont.ImageFont]:
    windows_fonts = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
    candidates_regular = [
        str(windows_fonts / "arial.ttf"),
        str(windows_fonts / "segoeui.ttf"),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    candidates_bold = [
        str(windows_fonts / "arialbd.ttf"),
        str(windows_fonts / "segoeuib.ttf"),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/Library/Fonts/Arial Bold.ttf",
    ]
    candidates_italic = [
        str(windows_fonts / "ariali.ttf"),
        str(windows_fonts / "segoeuii.ttf"),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
        "/Library/Fonts/Arial Italic.ttf",
    ]
    return {
        "regular": find_font(candidates_regular, 26),
        "small": find_font(candidates_regular, 22),
        "title": find_font(candidates_bold, 58),
        "subtitle": find_font(candidates_regular, 28),
        "contact": find_font(candidates_regular, 25),
        "label": find_font(candidates_italic, 20),
    }


def text_size(draw: ImageDraw.ImageDraw, text: str, font) -> tuple[int, int]:
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    return right - left, bottom - top


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    words = text.split()
    if not words:
        return [""]

    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if text_size(draw, candidate, font)[0] <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def draw_centered_multiline(
    draw: ImageDraw.ImageDraw,
    center_x: int,
    top_y: int,
    text: str,
    font,
    fill: str,
    max_width: int,
    line_spacing: int = 8,
) -> int:
    lines = wrap_text(draw, text, font, max_width)
    line_heights = [text_size(draw, line, font)[1] for line in lines]
    total_height = sum(line_heights) + line_spacing * (len(lines) - 1 if len(lines) > 1 else 0)
    current_y = top_y
    for line, line_height in zip(lines, line_heights):
        line_width = text_size(draw, line, font)[0]
        draw.text((center_x - line_width // 2, current_y), line, fill=fill, font=font)
        current_y += line_height + line_spacing
    return total_height


def lerp_channel(a: int, b: int, t: float) -> int:
    return int(a + (b - a) * t)


def vertical_gradient(width: int, height: int, top_color: tuple[int, int, int], bottom_color: tuple[int, int, int]) -> Image.Image:
    image = Image.new("RGB", (width, height), top_color)
    pixels = image.load()
    for y in range(height):
        t = y / max(height - 1, 1)
        color = tuple(lerp_channel(top_color[i], bottom_color[i], t) for i in range(3))
        for x in range(width):
            pixels[x, y] = color
    return image


def draw_circle_badge(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill: str, outline: str | None = None) -> None:
    draw.ellipse(box, fill=fill, outline=outline, width=2 if outline else 0)


def draw_briefcase_icon(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], color: str) -> None:
    x1, y1, x2, y2 = box
    w = x2 - x1
    h = y2 - y1
    handle_w = int(w * 0.34)
    handle_h = int(h * 0.18)
    handle_x1 = x1 + (w - handle_w) // 2
    handle_x2 = handle_x1 + handle_w
    handle_y2 = y1 + int(h * 0.26)
    handle_y1 = handle_y2 - handle_h
    body_top = y1 + int(h * 0.32)
    body = (x1 + int(w * 0.08), body_top, x2 - int(w * 0.08), y2 - int(h * 0.08))
    draw.rounded_rectangle((handle_x1, handle_y1, handle_x2, handle_y2), radius=4, outline=color, width=3)
    draw.rounded_rectangle(body, radius=6, outline=color, width=3)
    draw.line((x1 + int(w * 0.08), body_top + int(h * 0.22), x2 - int(w * 0.08), body_top + int(h * 0.22)), fill=color, width=3)
    draw.line((x1 + int(w * 0.48), body_top, x1 + int(w * 0.48), y2 - int(h * 0.08)), fill=color, width=3)


def draw_envelope_icon(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], color: str) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle((x1, y1, x2, y2), radius=5, outline=color, width=3)
    draw.line((x1, y1, (x1 + x2) // 2, (y1 + y2) // 2), fill=color, width=3)
    draw.line((x2, y1, (x1 + x2) // 2, (y1 + y2) // 2), fill=color, width=3)
    draw.line((x1, y2, (x1 + x2) // 2, (y1 + y2) // 2), fill=color, width=3)
    draw.line((x2, y2, (x1 + x2) // 2, (y1 + y2) // 2), fill=color, width=3)


def draw_phone_icon(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], color: str) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle((x1 + 8, y1 + 3, x2 - 8, y2 - 3), radius=8, outline=color, width=3)
    draw.rounded_rectangle((x1 + 14, y1 + 7, x2 - 14, y2 - 9), radius=4, outline=color, width=2)
    draw.ellipse((x1 + (x2 - x1) // 2 - 3, y2 - 10, x1 + (x2 - x1) // 2 + 3, y2 - 4), fill=color)


def draw_contact_row(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    icon_name: str,
    title: str,
    value: str,
    fonts: dict[str, ImageFont.FreeTypeFont | ImageFont.ImageFont],
    accent: str,
    text_color: str,
    bg_color: str,
) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=22, fill=bg_color, outline="#dce5ef", width=2)
    badge = (x1 + 20, y1 + 18, x1 + 88, y1 + 86)
    draw_circle_badge(draw, badge, fill=accent)

    icon_box = (badge[0] + 18, badge[1] + 18, badge[2] - 18, badge[3] - 18)
    if icon_name == "briefcase":
        draw_briefcase_icon(draw, icon_box, "#ffffff")
    elif icon_name == "email":
        draw_envelope_icon(draw, icon_box, "#ffffff")
    else:
        draw_phone_icon(draw, icon_box, "#ffffff")

    draw.text((x1 + 112, y1 + 18), title, fill="#6c7a89", font=fonts["label"])
    draw.text((x1 + 112, y1 + 42), value, fill=text_color, font=fonts["contact"])


def create_shadow(base: Image.Image, box: tuple[int, int, int, int], radius: int = 34) -> Image.Image:
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_box = (box[0] + 16, box[1] + 18, box[2] + 16, box[3] + 18)
    shadow_draw.rounded_rectangle(shadow_box, radius=radius, fill=(18, 28, 45, 120))
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    return Image.alpha_composite(base, shadow)


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def build_avatar(
    initials: str,
    photo_path: Path | None,
    size: int,
    fonts: dict[str, ImageFont.FreeTypeFont | ImageFont.ImageFont],
    fill_color: str = "#2e7db4",
    secondary_color: str = "#1f5d89",
) -> Image.Image:
    avatar = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    avatar_draw = ImageDraw.Draw(avatar)

    if photo_path and photo_path.exists():
        try:
            with Image.open(photo_path) as source:
                source = source.convert("RGBA")
                fitted = ImageOps.fit(
                    source,
                    (size - 10, size - 10),
                    method=Image.Resampling.LANCZOS,
                    centering=(0.5, 0.35),
                )
                mask = Image.new("L", fitted.size, 0)
                mask_draw = ImageDraw.Draw(mask)
                mask_draw.ellipse((0, 0, fitted.size[0] - 1, fitted.size[1] - 1), fill=255)
                avatar.paste(fitted, (5, 5), mask)
                avatar_draw.ellipse((2, 2, size - 3, size - 3), outline=(255, 255, 255, 220), width=3)
                avatar_draw.ellipse((6, 6, size - 7, size - 7), outline=(255, 255, 255, 70), width=1)
                return avatar
        except OSError:
            pass

    avatar_draw.ellipse((0, 0, size - 1, size - 1), fill=fill_color)
    avatar_draw.polygon([(0, 0), (size, 0), (size, int(size * 0.72)), (0, int(size * 0.35))], fill=secondary_color)
    avatar_draw.ellipse((1, 1, size - 2, size - 2), outline=(255, 255, 255, 75), width=2)
    mono_font = fonts["title"]
    mono_w, mono_h = text_size(avatar_draw, initials, mono_font)
    avatar_draw.text(
        ((size - mono_w) // 2, (size - mono_h) // 2 - 3),
        initials,
        fill="#ffffff",
        font=mono_font,
    )
    return avatar


def generate_business_card(
    name: str,
    title: str,
    email: str,
    phone: str,
    output_path: Path,
    strings: dict[str, str],
    photo_path: Path | None = None,
    design_id: int = 0,
    badge_text: str = "CARD",
) -> Path:
    fonts = get_fonts()
    design = get_design_preset(design_id)

    bg = vertical_gradient(WIDTH, HEIGHT, design["bg_top"], design["bg_bottom"]).convert("RGBA")
    bg_draw = ImageDraw.Draw(bg)
    bg_draw.ellipse((-180, -100, 440, 480), fill=(*hex_to_rgb(design["avatar_fill"]), 28))
    bg_draw.ellipse((760, -120, 1240, 360), fill=(*hex_to_rgb(design["panel_alt"]), 24))
    bg_draw.polygon([(790, 600), (1050, 360), (1050, 600)], fill=(*hex_to_rgb(design["accent"]), 18))

    card_margin = 36
    card_box = (card_margin, card_margin, WIDTH - card_margin, HEIGHT - card_margin)
    image = create_shadow(bg, card_box, radius=38)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(card_box, radius=38, fill="#ffffff", outline=design["card_outline"], width=2)

    panel_side = design["panel_side"]
    panel_width = design["panel_width"]
    if panel_side == "left":
        panel_x1 = card_margin
        panel_x2 = panel_x1 + panel_width
        content_x1 = panel_x2 + 42
        content_x2 = WIDTH - 58
    else:
        panel_x2 = WIDTH - card_margin
        panel_x1 = panel_x2 - panel_width
        content_x1 = card_margin + 22
        content_x2 = panel_x1 - 42

    panel_y1 = card_margin
    panel_y2 = HEIGHT - card_margin
    panel_center_x = panel_x1 + panel_width // 2

    panel_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    panel_draw = ImageDraw.Draw(panel_layer)
    panel_draw.rounded_rectangle((panel_x1, panel_y1, panel_x2, panel_y2), radius=38, fill=design["panel_main"])
    panel_draw.rectangle((panel_x1, panel_y1 + 24, panel_x2, panel_y1 + 160), fill=design["panel_alt"])
    if panel_side == "left":
        panel_draw.polygon([(panel_x2 - 70, panel_y1), (panel_x2, panel_y1), (panel_x2, panel_y1 + 130)], fill=design["panel_corner"])
        panel_draw.polygon([(panel_x1, panel_y2 - 130), (panel_x1 + 190, panel_y2), (panel_x1, panel_y2)], fill=design["panel_alt"])
        panel_draw.line((panel_x1 + 34, panel_y1 + 274, panel_x2 - 34, panel_y1 + 274), fill=(255, 255, 255, 60), width=2)
        accent_box = (panel_x2 - 8, panel_y1, panel_x2 + 6, panel_y2)
    else:
        panel_draw.polygon([(panel_x1, panel_y1), (panel_x1 + 70, panel_y1), (panel_x1, panel_y1 + 130)], fill=design["panel_corner"])
        panel_draw.polygon([(panel_x2, panel_y2 - 130), (panel_x2 - 190, panel_y2), (panel_x2, panel_y2)], fill=design["panel_alt"])
        panel_draw.line((panel_x1 + 34, panel_y1 + 274, panel_x2 - 34, panel_y1 + 274), fill=(255, 255, 255, 60), width=2)
        accent_box = (panel_x1 - 6, panel_y1, panel_x1 + 8, panel_y2)
    image = Image.alpha_composite(image, panel_layer)
    draw = ImageDraw.Draw(image)
    draw.rectangle(accent_box, fill=design["accent"])

    initials = initials_from_name(name)
    avatar_y_center = 150
    avatar = build_avatar(
        initials,
        photo_path,
        132,
        fonts,
        fill_color=design["avatar_fill"],
        secondary_color=design["avatar_secondary"],
    )
    image.paste(avatar, (panel_center_x - avatar.size[0] // 2, avatar_y_center - avatar.size[1] // 2), avatar)

    given_names, surnames = split_full_name(name)
    names_top_y = 244
    content_width = panel_width - 68
    draw_centered_multiline(
        draw,
        center_x=panel_center_x,
        top_y=names_top_y,
        text=given_names.upper(),
        font=fonts["subtitle"],
        fill=design["text_light"],
        max_width=content_width,
        line_spacing=2,
    )
    surname_font = fonts["title"] if surnames else fonts["subtitle"]
    draw_centered_multiline(
        draw,
        center_x=panel_center_x,
        top_y=names_top_y + 70,
        text=surnames.upper() if surnames else "",
        font=surname_font,
        fill="#e8f2fb",
        max_width=content_width,
        line_spacing=2,
    )

    badge_w, badge_h = text_size(draw, badge_text, fonts["label"])
    if design["badge_align"] == "left":
        badge_x = panel_x1 + 28
    elif design["badge_align"] == "right":
        badge_x = panel_x2 - badge_w - 56
    else:
        badge_x = panel_center_x - badge_w // 2
    badge_y = HEIGHT - 122
    draw.rounded_rectangle(
        (badge_x - 18, badge_y - 12, badge_x + badge_w + 18, badge_y + badge_h + 12),
        radius=18,
        fill=design["badge_bg"],
    )
    draw.text((badge_x, badge_y), badge_text, fill="#ffffff", font=fonts["label"])

    contact_heading = strings["contact_section"].upper()
    draw.text((content_x1, 78), contact_heading, fill=design["text_dark"], font=fonts["label"])
    draw.rectangle((content_x1, 104, content_x1 + 120, 108), fill=design["accent"])
    draw.text((content_x1, 124), strings["panel_subtitle"], fill="#6d7e90", font=fonts["small"])

    title_box = (content_x1, 186, content_x2, 272)
    email_box = (content_x1, 304, content_x2, 390)
    phone_box = (content_x1, 422, content_x2, 508)

    for box, icon_name, value, accent in [
        (title_box, "briefcase", title, design["row_accent"]),
        (email_box, "email", email, design["row_accent"]),
        (phone_box, "phone", phone, design["row_accent"]),
    ]:
        draw_contact_row(
            draw,
            box,
            icon_name,
            strings["title"].upper() if icon_name == "briefcase" else strings["email"].upper() if icon_name == "email" else strings["phone"].upper(),
            value,
            fonts,
            accent=accent,
            text_color=design["text_dark"],
            bg_color=design["row_fill"],
        )

    draw.line((content_x1, 546, content_x2, 546), fill=design["card_outline"], width=2)
    draw.ellipse((content_x2 - 88, 50, content_x2 - 12, 126), outline=design["card_outline"], width=2)
    draw.ellipse((content_x2 - 62, 74, content_x2 - 36, 100), fill=design["row_accent"])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(output_path, format="PNG")
    return output_path


def main() -> None:
    args = parse_args()
    language = select_language(args.lang)
    strings = LANG[language]

    print(strings["app_title"])
    print(strings["divider"])
    print()
    print(strings["enter_info"])

    name = prompt_text(strings["name"])
    title = prompt_text(strings["title"])
    email = prompt_text(strings["email"])
    phone = prompt_text(strings["phone"])

    print()
    print(strings["generating"])

    default_name = sanitize_filename(name) or strings["output_default"]
    output_file = Path(args.output) if args.output else Path.cwd() / f"{default_name}.png"
    photo_path = Path(args.photo) if args.photo else None

    saved_path = generate_business_card(
        name=name,
        title=title,
        email=email,
        phone=phone,
        output_path=output_file,
        strings=strings,
        photo_path=photo_path,
        design_id=args.design,
        badge_text=strings["badge"],
    )

    print(f"{strings['saved']} {saved_path.resolve()}")


if __name__ == "__main__":
    main()
