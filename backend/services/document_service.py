import html
import re


def sanitize_text(text: str) -> str:
    """Normalize common typographic characters while preserving document text."""
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u00a0": " ",
        "\u2022": "-",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return re.sub(r"[ \t]+$", "", text).strip()


def format_html_preview(text: str) -> str:
    """Convert plain generated text to safe, readable HTML."""
    safe = html.escape(sanitize_text(text))
    blocks = []

    for block in re.split(r"\n\s*\n", safe):
        lines = block.splitlines()
        if not lines:
            continue
        first = lines[0].strip()
        if re.match(r"^\d+[\.\)]\s+", first):
            blocks.append(
                "<section class='legal-section'>"
                + "<h3>"
                + first
                + "</h3>"
                + "<p>"
                + "<br>".join(lines[1:])
                + "</p></section>"
            )
        elif len(first) < 100 and first.upper() == first and any(c.isalpha() for c in first):
            blocks.append(f"<h2>{first}</h2>")
            if len(lines) > 1:
                blocks.append("<p>" + "<br>".join(lines[1:]) + "</p>")
        else:
            blocks.append("<p>" + "<br>".join(lines) + "</p>")

    return "\n".join(blocks)
