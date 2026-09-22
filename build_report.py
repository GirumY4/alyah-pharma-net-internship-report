#!/usr/bin/env python3
r"""
Alyah Pharma Net — Internship Report Builder
=============================================
Pipeline:  parts/*.md  --merge-->  build/merged_report.md  --pdf-->  dist/*.pdf

Commands
    python build_report.py check    scan parts for [[TODO:...]] placeholders,
                                    missing images and convention violations
    python build_report.py merge    concatenate parts into build/merged_report.md
    python build_report.py pdf      render the merged MD to a typeset PDF
    python build_report.py all      check + merge + pdf   (default)

Supported Markdown subset
    ## / ### / #### headings      (H1 is reserved for auto part titles)
    paragraphs, **bold**, *italic*, `code`, [link](url)
    - bullet lists / 1. numbered lists (one nesting level with two spaces)
    > blockquotes
    ``` fenced code blocks
    | pipe tables |  with caption via  <!-- table: Caption text -->
    ![caption](assets/images/x.png)  -> auto-numbered "Figure p.n"
    directives:  \newpage   \toc   \lotf
    part marker (inserted by merge):  <!-- part: N -->
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.platypus import (BaseDocTemplate, Frame, HRFlowable, Image,
                                NextPageTemplate, PageBreak, PageTemplate,
                                Paragraph, Preformatted, Spacer, Table,
                                TableStyle)
from reportlab.platypus.tableofcontents import TableOfContents
try:
    from PIL import Image as PILImage  # optional accelerator
except ImportError:
    PILImage = None

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from config.report_config import (PAGE_BUDGETS, PART_FILES, PART_TITLES,
                                  REPORT, OUTPUT_NAME)

PARTS_DIR = ROOT / "parts"
BUILD_DIR = ROOT / "build"
DIST_DIR = ROOT / "dist"
MERGED = BUILD_DIR / "merged_report.md"

GREEN = colors.HexColor("#0F5E4D")
GOLD = colors.HexColor("#DDAA4A")
INK = colors.HexColor("#17231F")
MUTED = colors.HexColor("#587067")
PAGE_W, PAGE_H = A4
MARGIN = 25 * mm
AVAIL = PAGE_W - 2 * MARGIN

TODO_RE = re.compile(r"\[\[TODO:[^\]]*\]\]")


# --------------------------------------------------------------------------
# Styles
# --------------------------------------------------------------------------
def make_styles():
    S = {}
    S["PartTitle"] = ParagraphStyle("PartTitle", fontName="Helvetica-Bold",
                                    fontSize=19, leading=24, textColor=GREEN,
                                    spaceAfter=4)
    S["H2"] = ParagraphStyle("H2", fontName="Helvetica-Bold", fontSize=13.5,
                             leading=18, textColor=INK, spaceBefore=14,
                             spaceAfter=6, keepWithNext=1)
    S["H3"] = ParagraphStyle("H3", fontName="Helvetica-Bold", fontSize=11.5,
                             leading=15, textColor=colors.HexColor("#33463F"),
                             spaceBefore=10, spaceAfter=4, keepWithNext=1)
    S["H4"] = ParagraphStyle("H4", fontName="Helvetica-BoldOblique",
                             fontSize=10.5, leading=14, textColor=INK,
                             spaceBefore=8, spaceAfter=3, keepWithNext=1)
    S["Body"] = ParagraphStyle("Body", fontName="Times-Roman", fontSize=11,
                               leading=15.5, alignment=TA_JUSTIFY, spaceAfter=7)
    S["Bullet1"] = ParagraphStyle("Bullet1", parent=S["Body"], leftIndent=16,
                                  bulletIndent=6, spaceAfter=3,
                                  alignment=TA_LEFT)
    S["Bullet2"] = ParagraphStyle("Bullet2", parent=S["Bullet1"],
                                  leftIndent=32, bulletIndent=20)
    S["Quote"] = ParagraphStyle("Quote", parent=S["Body"], leftIndent=20,
                                rightIndent=20, fontName="Times-Italic")
    S["Code"] = ParagraphStyle("Code", fontName="Courier", fontSize=8.2,
                               leading=10.5,
                               textColor=colors.HexColor("#22302A"))
    S["FigCap"] = ParagraphStyle("FigCap", fontName="Times-Italic",
                                 fontSize=9.5, leading=12, alignment=TA_CENTER,
                                 spaceBefore=4, spaceAfter=10, textColor=MUTED)
    S["TableCap"] = ParagraphStyle("TableCap", parent=S["FigCap"],
                                   alignment=TA_LEFT, spaceBefore=8,
                                   spaceAfter=4)
    S["TOCHeading"] = ParagraphStyle("TOCHeading", parent=S["H2"],
                                     spaceBefore=0)
    S["Cell"] = ParagraphStyle("Cell", fontName="Times-Roman", fontSize=9,
                               leading=12)
    S["CellH"] = ParagraphStyle("CellH", parent=S["Cell"],
                                fontName="Helvetica-Bold")
    S["Warn"] = ParagraphStyle("Warn", parent=S["Body"], textColor=
                               colors.HexColor("#B3261E"), fontName=
                               "Helvetica-Bold", fontSize=9.5)
    # Cover styles
        # ---- Cover styles (mirror the university outline template) ----
    S["CovUni"] = ParagraphStyle("CovUni", fontName="Times-Bold", fontSize=17,
                                 leading=22, alignment=TA_CENTER, textColor=INK)
    S["CovInst"] = ParagraphStyle("CovInst", fontName="Times-Bold", fontSize=15,
                                  leading=20, alignment=TA_CENTER, textColor=INK)
    S["CovFac"] = ParagraphStyle("CovFac", fontName="Times-Bold", fontSize=13.5,
                                 leading=18, alignment=TA_CENTER, textColor=INK)
    S["CovTitle"] = ParagraphStyle("CovTitle", fontName="Times-Bold",
                                   fontSize=16, leading=21,
                                   alignment=TA_CENTER, textColor=INK,
                                   spaceBefore=6, spaceAfter=6)
    S["CovLeft"] = ParagraphStyle("CovLeft", fontName="Times-Bold",
                                  fontSize=13, leading=18,
                                  alignment=TA_LEFT, textColor=INK,
                                  spaceAfter=4)
    S["CovLine"] = ParagraphStyle("CovLine", fontName="Times-Roman",
                                  fontSize=12.5, leading=17,
                                  alignment=TA_LEFT, textColor=INK,
                                  spaceAfter=6)
    S["CovLineInd"] = ParagraphStyle("CovLineInd", parent=S["CovLine"],
                                     leftIndent=14)
    return S


def toc_level_styles():
    return [
        ParagraphStyle("TOC0", fontName="Helvetica-Bold", fontSize=10.5,
                       leading=16, textColor=INK, spaceBefore=6),
        ParagraphStyle("TOC1", fontName="Times-Roman", fontSize=10.5,
                       leading=14, leftIndent=14),
        ParagraphStyle("TOC2", fontName="Times-Roman", fontSize=9.5,
                       leading=13, leftIndent=28, textColor=MUTED),
    ]


# --------------------------------------------------------------------------
# Inline markdown -> ReportLab markup
# --------------------------------------------------------------------------
INLINE_RE = re.compile(
    r"\*\*(?P<bold>.+?)\*\*"
    r"|(?<!\*)\*(?P<ital>[^*]+?)\*(?!\*)"
    r"|`(?P<code>[^`]+?)`"
    r"|\[(?P<linktext>[^\]]+)\]\((?P<linkurl>https?://[^)\s]+)\)"
)


def _inline_repl(m):
    if m.group("bold") is not None:
        return "<b>%s</b>" % m.group("bold")
    if m.group("ital") is not None:
        return "<i>%s</i>" % m.group("ital")
    if m.group("code") is not None:
        return '<font face="Courier" size="9">%s</font>' % m.group("code")
    return '<link href="%s" color="#0F5E4D">%s</link>' % (
        m.group("linkurl"), m.group("linktext"))


def inline(text: str) -> str:
    """Markdown inline markup -> ReportLab markup, single left-to-right pass."""
    t = text.replace("\\_", "_")      # un-escape escaped underscores
    t = html.escape(t, quote=False)   # escape & < > only; inserted tags stay intact
    return INLINE_RE.sub(_inline_repl, t)


def para(text: str, style, **kw):
    """Paragraph with markup conversion and a crash-proof fallback."""
    try:
        return Paragraph(inline(text), style, **kw)
    except Exception as exc:          # never kill the whole build on one line
        print(f"  ! markup fallback ({exc}): {text[:60]}...")
        return Paragraph(html.escape(text), style, **kw)


# --------------------------------------------------------------------------
# Markdown parser -> block list
# --------------------------------------------------------------------------
def parse_md(text: str):
    blocks = []
    lines = text.splitlines()
    i, n = 0, len(lines)
    pending_table_caption = None
    while i < n:
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        # directives & comments
        if stripped == "\\newpage":
            blocks.append(("pagebreak",)); i += 1; continue
        if stripped == "\\toc":
            blocks.append(("toc",)); i += 1; continue
        if stripped == "\\lotf":
            blocks.append(("lotf",)); i += 1; continue
        m = re.match(r"<!--\s*part:\s*(\d+)\s*-->", stripped)
        if m:
            blocks.append(("part", int(m.group(1)))); i += 1; continue
        m = re.match(r"<!--\s*table:\s*(.+?)\s*-->", stripped)
        if m:
            pending_table_caption = m.group(1); i += 1; continue
        if stripped.startswith("<!--"):
            i += 1; continue

        # fenced code
        if stripped.startswith("```"):
            lang = stripped[3:].strip()
            buf = []
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i]); i += 1
            i += 1
            blocks.append(("code", lang, "\n".join(buf)))
            continue

        # headings (H1 forbidden inside parts; tolerated as H2)
        m = re.match(r"(#{1,4})\s+(.*)", stripped)
        if m:
            level = min(len(m.group(1)), 4)
            blocks.append(("h", level, m.group(2).strip()))
            i += 1
            continue

        # image
        m = re.match(r"!\[(.*)\]\((.+)\)", stripped)
        if m:
            blocks.append(("img", m.group(1).strip(), m.group(2).strip()))
            i += 1
            continue

        # blockquote
        if stripped.startswith("> "):
            buf = []
            while i < n and lines[i].strip().startswith("> "):
                buf.append(lines[i].strip()[2:]); i += 1
            blocks.append(("quote", " ".join(buf)))
            continue

        # table
        if stripped.startswith("|") and i + 1 < n and \
                re.match(r"^\|[\s:\-|]+\|$", lines[i + 1].strip()):
            header = [c.strip() for c in stripped.strip("|").split("|")]
            i += 2
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append([c.strip()
                             for c in lines[i].strip().strip("|").split("|")])
                i += 1
            blocks.append(("table", pending_table_caption, header, rows))
            pending_table_caption = None
            continue

        # lists
        m = re.match(r"(-|\*)\s+(.*)", stripped)
        m2 = re.match(r"(\d+)[.)]\s+(.*)", stripped)
        if m or m2:
            ordered = bool(m2)
            items = []
            while i < n:
                s = lines[i].strip()
                mm_ = re.match(r"(-|\*)\s+(.*)", s)
                mm2 = re.match(r"(\d+)[.)]\s+(.*)", s)
                if mm_ or mm2:
                    lvl = 1
                    content = (mm_ or mm2).group(2)
                    if lines[i].startswith("  "):
                        lvl = 2
                    items.append((lvl, content))
                    i += 1
                elif s and items and not s.startswith(("#", "|", ">", "`")):
                    lvl, content = items[-1]
                    items[-1] = (lvl, content + " " + s)
                    i += 1
                else:
                    break
            blocks.append(("list", ordered, items))
            continue

        # paragraph
        buf = [stripped]
        i += 1
        while i < n:
            s = lines[i].strip()
            if (not s or s.startswith(("#", "|", ">", "```", "!["))
                    or s in ("\\newpage", "\\toc", "\\lotf")
                    or s.startswith("<!--")
                    or re.match(r"(-|\*)\s+", s) or re.match(r"\d+[.)]\s+", s)):
                break
            buf.append(s); i += 1
        blocks.append(("p", " ".join(buf)))
    return blocks


# --------------------------------------------------------------------------
# TOC flowables
# --------------------------------------------------------------------------
class ListOfFiguresTables(TableOfContents):
    def notify(self, kind, content):
        if kind == "LOTFEntry":
            self.addEntry(*content)


class ReportDocTemplate(BaseDocTemplate):
    def __init__(self, filename, **kw):
        super().__init__(filename, **kw)
        self.part_starts = []
        self._bk = 0
        frame = Frame(MARGIN, MARGIN, AVAIL, PAGE_H - 2 * MARGIN, id="main")
        self.addPageTemplates([
            PageTemplate(id="Cover", frames=[frame]),
            PageTemplate(id="Main", frames=[frame],
                         onPageEnd=_draw_header),
        ])

    def beforeDocument(self):
        self.part_starts = []
        self._bk = 0

    def _bookmark(self, text, level):
        self._bk += 1
        key = f"bk-{self._bk}"
        self.canv.bookmarkPage(key)
        self.canv.addOutlineEntry(text, key, level=level, closed=False)

    def afterFlowable(self, flowable):
        if not isinstance(flowable, Paragraph):
            return
        name = flowable.style.name
        text = flowable.getPlainText()
        if name == "PartTitle":
            self.part_starts.append((self.page, text))
            self._bookmark(text, 0)
            self.notify("TOCEntry", (0, text, self.page))
        elif name == "H2":
            self._bookmark(text, 1)
            self.notify("TOCEntry", (1, text, self.page))
        elif name == "H3":
            self.notify("TOCEntry", (2, text, self.page))
        elif name in ("FigCap", "TableCap"):
            self.notify("LOTFEntry", (0, text, self.page))


def _draw_header(canvas, doc):
    canvas.saveState()
    y = PAGE_H - 15 * mm
    canvas.setStrokeColor(GREEN)
    canvas.setLineWidth(0.8)
    canvas.line(MARGIN, y, PAGE_W - MARGIN, y)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(MARGIN, y + 2.5 * mm, REPORT["project_short"])
    title = ""
    for pg, t in doc.part_starts:
        if pg <= doc.page:
            title = t
    canvas.drawRightString(PAGE_W - MARGIN, y + 2.5 * mm, title)
    canvas.restoreState()


class NumberedCanvas(pdfcanvas.Canvas):
    """Defers footer drawing so 'Page X of Y' knows the total."""
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._saved = []

    def showPage(self):
        self._saved.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._saved)
        for state in self._saved:
            self.__dict__.update(state)
            self.saveState()
            self.setFont("Helvetica", 8.5)
            self.setFillColor(MUTED)
            self.drawCentredString(PAGE_W / 2.0, 12 * mm,
                                   f"Page {self._pageNumber} of {total}")
            self.restoreState()
            pdfcanvas.Canvas.showPage(self)
        pdfcanvas.Canvas.save(self)
def _image_size(path: Path):
    """Return (width, height) in pixels for PNG/JPEG, with or without Pillow."""
    if PILImage is not None:
        with PILImage.open(path) as im:
            return im.size
    data = path.read_bytes()
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")
    if data[:2] == b"\xff\xd8":
        i = 2
        while i < len(data) - 9:
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
                return (int.from_bytes(data[i + 7:i + 9], "big"),
                        int.from_bytes(data[i + 5:i + 7], "big"))
            if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
                i += 2
                continue
            i += 2 + int.from_bytes(data[i + 2:i + 4], "big")
    raise ValueError(f"Unsupported image format (install Pillow for full support): {path}")

# --------------------------------------------------------------------------
# Story builder
# --------------------------------------------------------------------------
def build_story(blocks, S):
    toc = TableOfContents()
    toc.levelStyles = toc_level_styles()
    try:
        toc.dotsMinLevel = 0
    except Exception:
        pass
    lotf = ListOfFiguresTables()
    lotf.levelStyles = [ParagraphStyle("LOTF", fontName="Times-Roman",
                                       fontSize=10, leading=14)]
    try:
        lotf.dotsMinLevel = 0
    except Exception:
        pass

    story = []
    # ---- Cover page (layout mirrors the university outline template) ----
    img_dir = ROOT / "assets" / "images"
    logo = next((p for p in img_dir.glob("logo.*")
                 if p.suffix.lower() in (".png", ".jpg", ".jpeg")), None)
    story += [Spacer(1, 8 * mm)]
    if logo:
        w, h = _image_size(logo)
        sc = min(95.0 / w, 95.0 / h, 1.0)
        story += [Image(str(logo), width=w * sc, height=h * sc,
                        hAlign="CENTER"), Spacer(1, 6 * mm)]
    story += [
        Paragraph(REPORT["university"], S["CovUni"]),
        Paragraph(REPORT["institute"], S["CovInst"]),
        Paragraph(REPORT["faculty"], S["CovFac"]),
        Paragraph(REPORT["department"], S["CovFac"]),
        Spacer(1, 14 * mm),
        Paragraph("Internship Report", S["CovTitle"]),
        Spacer(1, 16 * mm),
        Paragraph(REPORT["hosting_company"], S["CovLeft"]),
        Paragraph(REPORT["project_title"], S["CovLeft"]),
        Spacer(1, 24 * mm),
    ]
    # By / ID / Mentor / Company Supervisor / Date: a left-aligned block
    # offset toward the right half of the page, exactly as in the template
    sig_rows = [
        [Paragraph("<b>By:</b> " + REPORT["author"], S["CovLine"])],
        [Paragraph(REPORT["id_no"], S["CovLineInd"])],
        [Paragraph("<b>Mentor:</b> " + REPORT["mentor"], S["CovLine"])],
        [Paragraph("<b>Company Supervisor:</b> "
                   + REPORT["company_supervisor"], S["CovLine"])],
        [Paragraph("<b>Date:</b> " + REPORT["submission_date"], S["CovLine"])],
    ]
    sig_table = Table(sig_rows, colWidths=[0.62 * AVAIL])
    sig_table.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    sig_table.hAlign = "RIGHT"
    story += [sig_table, NextPageTemplate("Main"), PageBreak()]
    # ---- Parts ----
    fig_n = {}
    tab_n = {}
    current_part = 1
    first_part = True

    def part_header(idx):
        nonlocal first_part
        out = []
        if not first_part:
            out.append(PageBreak())
        first_part = False
        out.append(Paragraph(PART_TITLES[idx - 1], S["PartTitle"]))
        out.append(HRFlowable(width="100%", thickness=1.2, color=GOLD,
                              spaceAfter=12))
        return out

    if not blocks or blocks[0][0] != "part":
        blocks.insert(0, ("part", 1))

    for blk in blocks:
        kind = blk[0]
        if kind == "part":
            current_part = blk[1]
            story += part_header(current_part)
        elif kind == "pagebreak":
            story.append(PageBreak())
        elif kind == "toc":
            story += [Paragraph("Table of Contents", S["TOCHeading"]), toc]
        elif kind == "lotf":
            story += [Paragraph("List of Figures and Tables",
                                S["TOCHeading"]), lotf]
        elif kind == "h":
            level, text = blk[1], blk[2]
            style = {2: "H2", 3: "H3", 4: "H4"}.get(level, "H2")
            story.append(para(text, S[style]))
        elif kind == "p":
            story.append(para(blk[1], S["Body"]))
        elif kind == "quote":
            story.append(para(blk[1], S["Quote"]))
        elif kind == "list":
            ordered, items = blk[1], blk[2]
            counter = 0
            for lvl, content in items:
                if lvl == 1:
                    counter += 1
                bullet = f"{counter}." if ordered and lvl == 1 else \
                    ("\u2022" if lvl == 1 else "\u2013")
                style = S["Bullet1"] if lvl == 1 else S["Bullet2"]
                story.append(para(content, style, bulletText=bullet))
        elif kind == "code":
            pre = Preformatted(blk[2], S["Code"])
            tbl = Table([[pre]], colWidths=[AVAIL])
            tbl.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F5F5F0")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#D8D8D0")),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            story += [tbl, Spacer(1, 8)]
        elif kind == "img":
            alt, path = blk[1], blk[2]
            full = ROOT / path
            if full.exists():
                w, h = _image_size(full)
                sc = min(AVAIL / w, 480.0 / h, 1.0)
                story.append(Image(str(full), width=w * sc, height=h * sc,
                                   hAlign="CENTER"))
            else:
                story.append(Paragraph(f"[missing image: {path}]", S["Warn"]))
            fig_n[current_part] = fig_n.get(current_part, 0) + 1
            cap = f"Figure {current_part}.{fig_n[current_part]}: {alt}"
            story.append(Paragraph(cap, S["FigCap"]))
        elif kind == "table":
            _, caption, header, rows = blk
            if caption:
                tab_n[current_part] = tab_n.get(current_part, 0) + 1
                cap = f"Table {current_part}.{tab_n[current_part]}: {caption}"
                story.append(Paragraph(cap, S["TableCap"]))
            data = [[Paragraph(inline(c), S["CellH"]) for c in header]]
            for r in rows:
                data.append([Paragraph(inline(c), S["Cell"]) for c in r])
            tbl = Table(data, repeatRows=1, hAlign="LEFT")
            tbl.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E5F0EC")),
                ("LINEBELOW", (0, 0), (-1, 0), 0.8, GREEN),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#C9D6D0")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ]))
            story += [tbl, Spacer(1, 10)]
    return story


# --------------------------------------------------------------------------
# Commands
# --------------------------------------------------------------------------
def read_parts():
    out = []
    for idx, fname in enumerate(PART_FILES, start=1):
        path = PARTS_DIR / fname
        if not path.exists():
            print(f"  ! missing part file: {fname}")
            continue
        out.append((idx, path.read_text(encoding="utf-8")))
    return out


def cmd_check():
    print("== check ==")
    problems = 0
    for idx, fname in enumerate(PART_FILES, start=1):
        path = PARTS_DIR / fname
        if not path.exists():
            print(f"  MISSING  {fname}")
            problems += 1
            continue
        text = path.read_text(encoding="utf-8")
        todos = TODO_RE.findall(text)
        for line in text.splitlines():
            if line.startswith("# "):
                print(f"  CONVENTION  {fname}: H1 not allowed in parts "
                      f"(use ## and below)")
                problems += 1
        for m in re.finditer(r"!\[[^\]]*\]\(([^)]+)\)", text):
            if not (ROOT / m.group(1)).exists():
                print(f"  IMAGE     {fname}: missing {m.group(1)}")
                problems += 1
        print(f"  {fname}: {len(todos)} open TODO(s)")
    cfg = (ROOT / "config" / "report_config.py").read_text(encoding="utf-8")
    cfg_todos = TODO_RE.findall(cfg)
    print(f"  report_config.py: {len(cfg_todos)} open TODO(s)")
    print(f"== check finished: {problems} problem(s) ==")


def cmd_merge():
    BUILD_DIR.mkdir(exist_ok=True)
    chunks = []
    for idx, text in read_parts():
        chunks.append(f"<!-- part: {idx} -->\n\n{text.strip()}\n")
    MERGED.write_text("\n\n".join(chunks), encoding="utf-8")
    print(f"== merge == wrote {MERGED.relative_to(ROOT)}")


def cmd_pdf():
    BUILD_DIR.mkdir(exist_ok=True)
    DIST_DIR.mkdir(exist_ok=True)
    if MERGED.exists():
        blocks = parse_md(MERGED.read_text(encoding="utf-8"))
    else:
        print("  (merged file absent — parsing parts directly)")
        blocks = []
        for idx, text in read_parts():
            blocks.append(("part", idx))
            blocks += parse_md(text)
    S = make_styles()
    story = build_story(blocks, S)
    out = DIST_DIR / OUTPUT_NAME
    doc = ReportDocTemplate(str(out), pagesize=A4,
                            title=REPORT["project_short"],
                            author=REPORT["author"])
    doc.multiBuild(story, canvasmaker=NumberedCanvas)

    total = doc.page
    print("== pdf == page budget report")
    starts = doc.part_starts
    for i, (pg, title) in enumerate(starts):
        end = starts[i + 1][0] - 1 if i + 1 < len(starts) else total
        pages = end - pg + 1
        budget = PAGE_BUDGETS.get(i + 1, 99)
        flag = "OK" if pages <= budget else f"OVER by {pages - budget}"
        print(f"  {title:<48} pages {pg:>3}-{end:<3} "
              f"({pages:>2}/{budget})  {flag}")
    print(f"  total pages: {total}")
    print(f"  output: {out}")


def main():
    ap = argparse.ArgumentParser(description="Internship report builder")
    ap.add_argument("command", nargs="?", default="all",
                    choices=["check", "merge", "pdf", "all"])
    args = ap.parse_args()
    if args.command in ("check", "all"):
        cmd_check()
    if args.command in ("merge", "all"):
        cmd_merge()
    if args.command in ("pdf", "all"):
        cmd_pdf()


if __name__ == "__main__":
    main()