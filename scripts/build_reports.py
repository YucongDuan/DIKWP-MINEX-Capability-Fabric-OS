from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release"
OUT.mkdir(exist_ok=True)

FONT_CN = "Noto Sans CJK SC"
FONT_EN = "Liberation Sans"
FONT_MONO = "DejaVu Sans Mono"
NAVY = "17324D"
BLUE = "234E70"
PALE = "D9EAF2"
TEAL = "168B7D"
GOLD = "D9A441"
GRAY = "5B6570"
LIGHT = "F4F7F9"


def shade(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_text(cell, text: str, *, bold=False, color=None, size=9, font=FONT_CN) -> None:
    cell.text = ""
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(text)
    r.bold = bold
    r.font.name = font
    r._element.rPr.rFonts.set(qn("w:eastAsia"), font)
    r.font.size = Pt(size)
    if color:
        r.font.color.rgb = RGBColor.from_string(color)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def set_repeat_table_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def add_page_field(paragraph) -> None:
    run = paragraph.add_run()
    fld_char1 = OxmlElement("w:fldChar")
    fld_char1.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = "PAGE"
    fld_char2 = OxmlElement("w:fldChar")
    fld_char2.set(qn("w:fldCharType"), "end")
    run._r.append(fld_char1)
    run._r.append(instr)
    run._r.append(fld_char2)


def add_hyperlink(paragraph, text: str, url: str, font: str) -> None:
    part = paragraph.part
    rid = part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True)
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), rid)
    new_run = OxmlElement("w:r")
    rpr = OxmlElement("w:rPr")
    color = OxmlElement("w:color"); color.set(qn("w:val"), "0563C1")
    underline = OxmlElement("w:u"); underline.set(qn("w:val"), "single")
    rfonts = OxmlElement("w:rFonts"); rfonts.set(qn("w:ascii"), font); rfonts.set(qn("w:eastAsia"), font)
    rpr.append(rfonts); rpr.append(color); rpr.append(underline)
    new_run.append(rpr)
    t = OxmlElement("w:t"); t.text = text
    new_run.append(t); hyperlink.append(new_run); paragraph._p.append(hyperlink)


def style_document(doc: Document, language: str) -> str:
    font = FONT_CN if language == "cn" else FONT_EN
    sec = doc.sections[0]
    sec.top_margin = Cm(1.7)
    sec.bottom_margin = Cm(1.55)
    sec.left_margin = Cm(1.8)
    sec.right_margin = Cm(1.8)
    sec.header_distance = Cm(0.7)
    sec.footer_distance = Cm(0.7)

    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = font
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), font)
    normal.font.size = Pt(9.7 if language == "cn" else 9.5)
    normal.paragraph_format.space_after = Pt(5)
    normal.paragraph_format.line_spacing = 1.14

    for name, size, color in [("Title", 28, NAVY), ("Subtitle", 14, GRAY), ("Heading 1", 17, NAVY), ("Heading 2", 13, BLUE), ("Heading 3", 11, TEAL)]:
        st = styles[name]
        st.font.name = font
        st._element.rPr.rFonts.set(qn("w:eastAsia"), font)
        st.font.size = Pt(size)
        st.font.color.rgb = RGBColor.from_string(color)
        st.font.bold = name != "Subtitle"
        st.paragraph_format.space_before = Pt(10 if name != "Title" else 0)
        st.paragraph_format.space_after = Pt(5)
        st.paragraph_format.keep_with_next = True

    # List styles
    for name in ("List Bullet", "List Number"):
        st = styles[name]
        st.font.name = font
        st._element.rPr.rFonts.set(qn("w:eastAsia"), font)
        st.font.size = Pt(9.5)

    return font


def add_header_footer(doc: Document, title: str, font: str) -> None:
    for section in doc.sections:
        header = section.header
        p = header.paragraphs[0]
        p.text = title
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r = p.runs[0]
        r.font.name = font; r._element.rPr.rFonts.set(qn("w:eastAsia"), font)
        r.font.size = Pt(8); r.font.color.rgb = RGBColor.from_string(GRAY)
        footer = section.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        rr = fp.add_run("MINEX-1000:2026-DRAFT  |  ")
        rr.font.name = font; rr._element.rPr.rFonts.set(qn("w:eastAsia"), font); rr.font.size = Pt(8); rr.font.color.rgb = RGBColor.from_string(GRAY)
        add_page_field(fp)


def add_cover(doc: Document, language: str, font: str) -> None:
    cn = language == "cn"
    title = "DIKWP MINEX 能力织网操作系统" if cn else "DIKWP MINEX Capability Fabric OS"
    subtitle = "模型优先时代的意图、能力、耗费与证据基础设施" if cn else "Intent, Capability, Expenditure, and Evidence Infrastructure for Model-First Computing"
    slogan = "目的优先，App可选；能力可流动，执行先有证据。" if cn else "Intent first. Apps optional. Capabilities liquid. Proof before execution."
    status = "研究型参考实现 / 中英文正式报告" if cn else "Research Reference Implementation / English System Report"

    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    c=t.cell(0,0); shade(c,NAVY)
    c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
    p=c.paragraphs[0]; p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before=Pt(30); p.paragraph_format.space_after=Pt(30)
    r=p.add_run(title); r.bold=True; r.font.size=Pt(26); r.font.color.rgb=RGBColor(255,255,255); r.font.name=font; r._element.rPr.rFonts.set(qn("w:eastAsia"),font)

    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before=Pt(22)
    r=p.add_run(subtitle); r.font.size=Pt(15); r.font.color.rgb=RGBColor.from_string(BLUE); r.font.name=font; r._element.rPr.rFonts.set(qn("w:eastAsia"),font)
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    r=p.add_run(slogan); r.italic=True; r.font.size=Pt(12); r.font.color.rgb=RGBColor.from_string(TEAL); r.font.name=font; r._element.rPr.rFonts.set(qn("w:eastAsia"),font)

    doc.add_picture(str(ROOT/'assets/architecture_bilingual.png'), width=Inches(6.8))
    doc.paragraphs[-1].alignment=WD_ALIGN_PARAGRAPH.CENTER

    table=doc.add_table(rows=5,cols=2); table.alignment=WD_TABLE_ALIGNMENT.CENTER
    rows = [
        ("Version / 版本", "1.0.0"),
        ("Date / 日期", "2026-09-07"),
        ("Pre-standard / 预标准", "MINEX-1000:2026-DRAFT"),
        ("Operating mode / 运行模式", "MESH95_INTENT_CAPABILITY_PARETO_MINIMUM_EXPENDITURE_LEASE_RECEIPT_CLOSURE"),
        ("Authority / 权限", "automatic_external_action_authority = 0"),
    ]
    for i,(a,b) in enumerate(rows):
        set_cell_text(table.cell(i,0),a,bold=True,size=8.5,font=font); shade(table.cell(i,0),PALE)
        set_cell_text(table.cell(i,1),b,size=8.5,font=font)
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before=Pt(14)
    r=p.add_run(status); r.font.size=Pt(10); r.font.color.rgb=RGBColor.from_string(GRAY); r.font.name=font; r._element.rPr.rFonts.set(qn("w:eastAsia"),font)
    doc.add_page_break()


def add_contents(doc: Document, headings: list[str], language: str, font: str) -> None:
    doc.add_heading("目录" if language=='cn' else "Contents", level=1)
    intro = "本报告的章节顺序与开源仓库中的系统报告一致。" if language=='cn' else "The chapter order matches the system report included in the open-source repository."
    doc.add_paragraph(intro)
    for idx,h in enumerate(headings,1):
        clean = re.sub(r"^\d+(?:\.\d+)*[.、]?\s*", "", h).strip()
        p=doc.add_paragraph()
        p.paragraph_format.left_indent=Cm(0.35)
        p.paragraph_format.first_line_indent=Cm(-0.35)
        p.paragraph_format.space_after=Pt(2)
        r=p.add_run(f"{idx}. {clean}")
        r.font.name=font; r._element.rPr.rFonts.set(qn("w:eastAsia"),font); r.font.size=Pt(9.5)
    doc.add_page_break()


def add_callout(doc: Document, text: str, font: str, fill="E8F3F1") -> None:
    table=doc.add_table(rows=1,cols=1)
    table.alignment=WD_TABLE_ALIGNMENT.CENTER
    cell=table.cell(0,0); shade(cell,fill)
    p=cell.paragraphs[0]; p.paragraph_format.space_before=Pt(5); p.paragraph_format.space_after=Pt(5)
    r=p.add_run(text); r.bold=True; r.font.name=font; r._element.rPr.rFonts.set(qn("w:eastAsia"),font); r.font.size=Pt(10); r.font.color.rgb=RGBColor.from_string(NAVY)


def parse_table(lines: list[str], start: int) -> tuple[list[list[str]], int]:
    rows=[]; i=start
    while i < len(lines) and lines[i].strip().startswith('|'):
        raw=[x.strip() for x in lines[i].strip().strip('|').split('|')]
        if not all(re.fullmatch(r':?-{3,}:?', x.replace(' ','')) for x in raw):
            rows.append(raw)
        i+=1
    return rows,i


def add_markdown_table(doc: Document, rows: list[list[str]], font: str) -> None:
    if not rows: return
    width=max(len(r) for r in rows)
    table=doc.add_table(rows=len(rows),cols=width)
    table.alignment=WD_TABLE_ALIGNMENT.CENTER
    table.style='Table Grid'
    for i,row in enumerate(rows):
        for j in range(width):
            txt=row[j] if j<len(row) else ''
            set_cell_text(table.cell(i,j),txt,bold=(i==0),color='FFFFFF' if i==0 else None,size=8.2,font=font)
            if i==0: shade(table.cell(i,j),BLUE)
            elif i%2==0: shade(table.cell(i,j),LIGHT)
    set_repeat_table_header(table.rows[0])
    doc.add_paragraph().paragraph_format.space_after=Pt(0)


def add_body_from_markdown(doc: Document, markdown_path: Path, language: str, font: str) -> None:
    lines=markdown_path.read_text(encoding='utf-8').splitlines()
    # Extract only second-level chapter headings for TOC, excluding front metadata.
    headings=[re.sub(r'^##\s+','',l).strip() for l in lines if l.startswith('## ') and not l.startswith('### ')]
    add_contents(doc,headings,language,font)

    i=0; in_code=False; code=[]; math=False; math_lines=[]; section_no=0
    inserted=set()
    while i<len(lines):
        line=lines[i].rstrip()
        stripped=line.strip()
        if i<8 and (stripped.startswith('# ') or stripped.startswith('**') or stripped=='---' or not stripped):
            i+=1; continue
        if stripped.startswith('```'):
            if not in_code:
                in_code=True; code=[]
            else:
                p=doc.add_paragraph()
                p.paragraph_format.left_indent=Cm(.45); p.paragraph_format.right_indent=Cm(.25)
                p.paragraph_format.space_before=Pt(3); p.paragraph_format.space_after=Pt(6)
                pPr=p._p.get_or_add_pPr(); shd=OxmlElement('w:shd'); shd.set(qn('w:fill'),'F1F3F5'); pPr.append(shd)
                r=p.add_run('\n'.join(code)); r.font.name=FONT_MONO; r._element.rPr.rFonts.set(qn('w:eastAsia'),FONT_MONO); r.font.size=Pt(8)
                in_code=False
            i+=1; continue
        if in_code:
            code.append(line); i+=1; continue
        if stripped=='\\[':
            math=True; math_lines=[]; i+=1; continue
        if math:
            if stripped=='\\]':
                p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_before=Pt(4); p.paragraph_format.space_after=Pt(6)
                r=p.add_run(' '.join(math_lines)); r.font.name=FONT_MONO; r._element.rPr.rFonts.set(qn('w:eastAsia'),FONT_MONO); r.font.size=Pt(9); r.font.color.rgb=RGBColor.from_string(BLUE)
                math=False
            else: math_lines.append(stripped)
            i+=1; continue
        if not stripped or stripped=='---':
            i+=1; continue
        if stripped.startswith('|'):
            rows,nxt=parse_table(lines,i); add_markdown_table(doc,rows,font); i=nxt; continue
        if stripped.startswith('## '):
            section_no+=1
            title=stripped[3:].strip()
            # Strategic page breaks, not one per section.
            if section_no in {5,10,13}:
                doc.add_page_break()
            doc.add_heading(title,level=1)
            # Insert figures at selected sections.
            if section_no==1 and 'architecture' not in inserted:
                add_callout(doc, 'Interface access never creates authority. / 能看见、能点击或能调用，不等于获得权限。', font)
                inserted.add('architecture')
            if section_no==5 and 'costs' not in inserted:
                doc.add_picture(str(ROOT/'assets/route_energy_quality.png'),width=Inches(6.25)); doc.paragraphs[-1].alignment=WD_ALIGN_PARAGRAPH.CENTER
                cap=doc.add_paragraph('Figure: Same outcome, different execution surfaces.' if language=='en' else '图：相同结果在不同执行表面上的能耗与质量差异。'); cap.alignment=WD_ALIGN_PARAGRAPH.CENTER
                doc.add_picture(str(ROOT/'assets/multidimensional_costs.png'),width=Inches(6.25)); doc.paragraphs[-1].alignment=WD_ALIGN_PARAGRAPH.CENTER
                inserted.add('costs')
            if section_no==6 and 'internalization' not in inserted:
                doc.add_picture(str(ROOT/'assets/internalization_ladder.png'),width=Inches(6.25)); doc.paragraphs[-1].alignment=WD_ALIGN_PARAGRAPH.CENTER
                inserted.add('internalization')
            if section_no==7 and 'mesh' not in inserted:
                doc.add_picture(str(ROOT/'assets/capability_mesh_topology.png'),width=Inches(6.25)); doc.paragraphs[-1].alignment=WD_ALIGN_PARAGRAPH.CENTER
                inserted.add('mesh')
            i+=1; continue
        if stripped.startswith('### '):
            doc.add_heading(stripped[4:].strip(),level=2); i+=1; continue
        if stripped.startswith('#### '):
            doc.add_heading(stripped[5:].strip(),level=3); i+=1; continue
        if re.match(r'^[-*]\s+',stripped):
            p=doc.add_paragraph(style='List Bullet'); p.add_run(re.sub(r'^[-*]\s+','',stripped)); i+=1; continue
        if re.match(r'^\d+\.\s+',stripped):
            p=doc.add_paragraph(style='List Number'); p.add_run(re.sub(r'^\d+\.\s+','',stripped)); i+=1; continue
        # Accumulate a normal paragraph until a structural boundary.
        parts=[stripped]; j=i+1
        while j<len(lines):
            nxt=lines[j].strip()
            if not nxt or nxt.startswith(('#','```','|','- ','* ','\\[')) or re.match(r'^\d+\.\s+',nxt): break
            parts.append(nxt); j+=1
        text=' '.join(parts)
        p=doc.add_paragraph()
        # Basic inline code/bold cleanup, avoiding raw markdown markers.
        tokens=re.split(r'(`[^`]+`|\*\*[^*]+\*\*)',text)
        for token in tokens:
            if token.startswith('`') and token.endswith('`'):
                r=p.add_run(token[1:-1]); r.font.name=FONT_MONO; r._element.rPr.rFonts.set(qn('w:eastAsia'),FONT_MONO); r.font.size=Pt(8.5); r.font.color.rgb=RGBColor.from_string(TEAL)
            elif token.startswith('**') and token.endswith('**'):
                r=p.add_run(token[2:-2]); r.bold=True
            else:
                # Make plain URLs clickable if paragraph is only a URL; otherwise preserve text.
                r=p.add_run(token)
            for r in p.runs:
                r.font.name=font; r._element.rPr.rFonts.set(qn('w:eastAsia'),font)
        i=j


def add_references(doc: Document, language: str, font: str) -> None:
    doc.add_page_break()
    doc.add_heading('参考来源与事实边界' if language=='cn' else 'References and source boundary',level=1)
    intro=('以下来源用于说明技术背景和接口标准，不构成对MINEX的认证。用户提供的文章是二级叙事，报告已将其中事实、作者推断和系统设计推断分开。'
           if language=='cn' else 'These sources establish technical context and interface standards; they do not certify MINEX. The supplied articles are secondary narratives, and this report separates source claims from system-design inference.')
    doc.add_paragraph(intro)
    refs=[
        ('OpenAI - GPT-6 Astra: A new generation of intelligence','https://openai.com/index/gpt-6-astra/'),
        ('OpenAI API - Computer use','https://developers.openai.com/api/docs/guides/tools-computer-use'),
        ('OpenAI API - Changelog','https://developers.openai.com/api/docs/changelog'),
        ('Model Context Protocol - Specification 2026-07-28','https://modelcontextprotocol.io/specification/2026-07-28'),
        ('Agent2Agent Protocol - Latest specification','https://a2a-protocol.org/latest/specification/'),
        ('Green Software Foundation - Software Carbon Intensity','https://sci.greensoftware.foundation/'),
        ('Green Software Foundation - Software Energy Intensity','https://greensoftware.foundation/standards/sei/'),
    ]
    for name,url in refs:
        p=doc.add_paragraph(style='List Number')
        add_hyperlink(p,name,url,font)
    add_callout(doc, 'Declared route costs are demonstration parameters unless the receipt identifies a physical or provider measurement source.' if language=='en' else '除非收据明确标注物理测量或供应商测量来源，否则路线耗费均为演示性声明参数。',font,fill='FFF2CC')


def build(language: str) -> Path:
    doc=Document()
    font=style_document(doc,language)
    title='DIKWP MINEX 能力织网操作系统' if language=='cn' else 'DIKWP MINEX Capability Fabric OS'
    add_header_footer(doc,title,font)
    add_cover(doc,language,font)
    md=ROOT/'docs'/('SYSTEM_REPORT_CN.md' if language=='cn' else 'SYSTEM_REPORT_EN.md')
    add_body_from_markdown(doc,md,language,font)
    add_references(doc,language,font)
    # Metadata
    props=doc.core_properties
    props.title=title
    props.subject='Minimum verified execution expenditure capability routing'
    props.author='Yucong Duan'
    props.keywords='DIKWP, capability routing, model-first software, MCP, A2A, computer use, energy efficiency'
    out=OUT/(f'DIKWP_MINEX_SYSTEM_REPORT_{"CN" if language=="cn" else "EN"}_v1.0.0.docx')
    doc.save(out)
    return out

if __name__=='__main__':
    for lang in ('cn','en'):
        print(build(lang))
