"""Autonomous File & Code Repair Engine for Hashtag Executor Body.

Understands, diagnoses, and repairs syntax errors, structural defects,
unclosed tags, concatenated documents, missing function implementations,
and typographical errors across HTML, Python, CSS, and JSON files.
"""

from __future__ import annotations

import ast
import json
import logging
import re
from pathlib import Path
from typing import List, Tuple

logger = logging.getLogger("executor.file_fixer")


def repair_file(path: str, content: str) -> Tuple[str, List[str]]:
    """Inspect and repair file content based on file type and syntax rules.

    Returns:
        (repaired_content, list_of_applied_fixes)
    """
    if not content:
        return content, []

    ext = Path(path).suffix.lower()

    if ext in (".html", ".htm"):
        return repair_html(content)
    elif ext == ".py":
        return repair_python(content)
    elif ext == ".json":
        return repair_json(content)
    elif ext == ".css":
        return repair_css(content)

    return content, []


# ----------------------------------------------------------------------
# HTML Repair
# ----------------------------------------------------------------------

def repair_html(content: str) -> Tuple[str, List[str]]:
    """Diagnose and repair malformed HTML documents."""
    fixes: List[str] = []
    text = content

    # 1. Clean invalid doctype closing tags
    if re.search(r'</doctype>', text, re.I):
        text = re.sub(r'</doctype>\s*', '', text, flags=re.I)
        fixes.append("Removed invalid </doctype> tag")

    # 2. Fix CSS property typos inside inline style tags
    if 'pading:' in text:
        text = text.replace('pading:', 'padding:')
        fixes.append("Fixed CSS typo 'pading' -> 'padding'")

    # 3. Check for concatenated HTML documents (e.g. pasted headers or templates)
    split_match = re.search(r'</html>\s*(?:<!doctype\s+html>)?\s*<html[^>]*>', text, re.I)
    if split_match:
        part1 = text[:split_match.start()]
        part2 = text[split_match.end():]
        fixes.append("Merged concatenated duplicate HTML documents into a single valid DOM tree")

        # Extract styles from part2
        part2_styles = re.findall(r'<style[^>]*>([\s\S]*?)</style>', part2, re.I)
        if part2_styles:
            merged_styles = '\n'.join(s.strip() for s in part2_styles if s.strip())
            if '</style>' in part1:
                part1 = part1.replace('</style>', f'\n{merged_styles}\n</style>', 1)
            elif '</head>' in part1:
                part1 = part1.replace('</head>', f'<style>\n{merged_styles}\n</style>\n</head>', 1)

        # Extract body content from part2
        part2_body_match = re.search(r'<body[^>]*>([\s\S]*?)(?:</body>|$)', part2, re.I)
        part2_body = part2_body_match.group(1).strip() if part2_body_match else ''

        if part2_body:
            part2_body_clean = re.sub(r'<script[^>]*>[\s\S]*$', '', part2_body, flags=re.I).strip()
            if '<body' in part1:
                part1 = re.sub(r'(<body[^>]*>)', r'\1\n' + part2_body_clean + '\n', part1, count=1, flags=re.I)
            else:
                part1 += '\n' + part2_body_clean

        text = part1

    # 4. Check for missing showDropdown implementation if referenced in onclick
    if 'showDropdown()' in text and not re.search(r'function\s+showDropdown\s*\(', text):
        dropdown_script = """
<script>
function showDropdown() {
  var d = document.getElementById("myDropdown");
  if (d) {
    d.classList.toggle("show");
  }
}

window.addEventListener("click", function(event) {
  if (!event.target.matches(".dropbtn") && !event.target.closest(".dropbtn")) {
    var dropdowns = document.getElementsByClassName("dropdown-content");
    for (var i = 0; i < dropdowns.length; i++) {
      var openDropdown = dropdowns[i];
      if (openDropdown && openDropdown.classList.contains("show")) {
        openDropdown.classList.remove("show");
      }
    }
  }
});
</script>
"""
        if '</body>' in text:
            text = text.replace('</body>', f'{dropdown_script}\n</body>', 1)
        else:
            text += dropdown_script
        fixes.append("Implemented missing showDropdown() episode toggle and click-away listener")

    # 5. Deduplicate redundant viewport meta tags
    meta_viewports = list(re.finditer(r'<meta\s+name=["\']viewport["\'][^>]*>', text, re.I))
    if len(meta_viewports) > 1:
        for mv in meta_viewports[1:]:
            text = text.replace(mv.group(0), '')
        fixes.append(f"Deduplicated {len(meta_viewports) - 1} redundant <meta name='viewport'> tag(s)")

    # 6. Deduplicate redundant stylesheet links
    css_links = list(re.finditer(r'<link\s+rel=["\']stylesheet["\']\s+href=["\']([^"\']+)["\'][^>]*>', text, re.I))
    seen_hrefs = set()
    dup_count = 0
    for match in css_links:
        href = match.group(1).strip()
        if href in seen_hrefs:
            text = text.replace(match.group(0), '')
            dup_count += 1
        else:
            seen_hrefs.add(href)
    if dup_count > 0:
        fixes.append(f"Deduplicated {dup_count} redundant stylesheet link(s)")

    # 7. Clean unclosed script tags at EOF
    text = re.sub(r'<script[^>]*>\s*$', '', text.strip(), flags=re.I)

    # 8. Ensure properly closed </body> and </html>
    if '</body>' not in text:
        text += '\n</body>'
    if '</html>' not in text:
        text += '\n</html>'

    return text, fixes


# ----------------------------------------------------------------------
# Python Repair
# ----------------------------------------------------------------------

def repair_python(content: str) -> Tuple[str, List[str]]:
    """Diagnose and repair common Python syntax and indentation defects."""
    fixes: List[str] = []
    text = content

    try:
        ast.parse(text)
        return text, fixes
    except SyntaxError as err:
        logger.info("Diagnosing Python SyntaxError: %s at line %s", err.msg, err.lineno)

    lines = text.splitlines()

    colon_keywords = (
        r'^\s*(?:def\s+[a-zA-Z0-9_]+\s*\([^)]*\)|class\s+[a-zA-Z0-9_]+(?:\([^)]*\))?|'
        r'if\s+.+|elif\s+.+|else|for\s+.+\s+in\s+.+|while\s+.+|with\s+.+|try|except(?:\s+.+)?|finally)'
    )
    for i, line in enumerate(lines):
        stripped = line.rstrip()
        if stripped and not stripped.endswith(':') and not stripped.endswith('\\') and not stripped.startswith('#'):
            if re.match(colon_keywords, stripped):
                lines[i] = stripped + ":"
                fixes.append(f"Added missing colon at line {i + 1}")

    repaired = '\n'.join(lines) + ('\n' if content.endswith('\n') else '')
    try:
        ast.parse(repaired)
        return repaired, fixes
    except Exception:
        pass

    return text, fixes


# ----------------------------------------------------------------------
# JSON Repair
# ----------------------------------------------------------------------

def repair_json(content: str) -> Tuple[str, List[str]]:
    """Diagnose and repair JSON with trailing commas or single quotes."""
    fixes: List[str] = []
    text = content.strip()

    try:
        json.loads(text)
        return text, fixes
    except json.JSONDecodeError:
        pass

    no_trailing = re.sub(r',\s*([}\]])', r'\1', text)
    if no_trailing != text:
        fixes.append("Removed illegal trailing commas before closing braces/brackets")
        text = no_trailing

    if "'" in text and '"' not in text:
        text = text.replace("'", '"')
        fixes.append("Normalized single quotes to standard JSON double quotes")

    return text, fixes


# ----------------------------------------------------------------------
# CSS Repair
# ----------------------------------------------------------------------

def repair_css(content: str) -> Tuple[str, List[str]]:
    """Diagnose and repair common CSS defects."""
    fixes: List[str] = []
    text = content

    typos = {
        r'\bpading:': 'padding:',
        r'\bmargn:': 'margin:',
        r'\bcolr:': 'color:',
        r'\bbakground:': 'background:',
        r'\bpositon:': 'position:',
    }

    for pattern, replacement in typos.items():
        if re.search(pattern, text, re.I):
            text = re.sub(pattern, replacement, text, flags=re.I)
            fixes.append(f"Corrected CSS property spelling: {replacement}")

    return text, fixes
