"""Render the three editable TriadLens Markdown documents as submission PDFs."""
from __future__ import annotations

import html
import re
from pathlib import Path

from reportlab.graphics.shapes import Drawing, Ellipse, Line, Polygon, Rect, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.utils import simpleSplit
from reportlab.platypus import (Flowable, Paragraph, SimpleDocTemplate, Spacer,
                                Table, TableStyle)

HERE = Path(__file__).parent
OUT = HERE / "pdf"
OUT.mkdir(exist_ok=True)
NAVY = colors.black
TEAL = colors.black
PALE = colors.white

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="DocTitleX", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=17, leading=22, textColor=NAVY, spaceAfter=16))
styles.add(ParagraphStyle(name="H1X", parent=styles["Heading1"], fontSize=12, leading=16, textColor=NAVY, spaceBefore=17, spaceAfter=6))
styles.add(ParagraphStyle(name="H2X", parent=styles["Heading2"], fontSize=10, leading=14, textColor=TEAL, spaceBefore=12, spaceAfter=5))
styles.add(ParagraphStyle(name="BodyX", parent=styles["BodyText"], fontSize=8.6, leading=12.5, spaceAfter=5))
styles.add(ParagraphStyle(name="CellX", parent=styles["BodyText"], fontSize=7.3, leading=10))
styles.add(ParagraphStyle(name="HeaderCellX", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=7.3, leading=10, textColor=colors.black))
styles.add(ParagraphStyle(name="DiagramTextX", parent=styles["BodyText"], alignment=TA_CENTER, fontSize=8))


def markup(text):
    value = html.escape(text.replace("·", " - ").replace("≤", "&lt;=").replace("≥", "&gt;=").replace("→", " to ").replace("–", "-").replace("—", "-"))
    value = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", value)
    value = re.sub(r"`([^`]+)`", r"<font name='Courier'>\1</font>", value)
    return value


def label(d, x, y, text, size=8, color=NAVY):
    d.add(String(x, y, text, fontName="Helvetica", fontSize=size, fillColor=color, textAnchor="middle"))


def arrow(d, x1, y1, x2, y2, color=TEAL):
    d.add(Line(x1, y1, x2, y2, strokeColor=color, strokeWidth=1.2))
    d.add(Polygon([x2, y2, x2-5, y2+3, x2-5, y2-3], fillColor=color, strokeColor=color))


def diagram(kind):
    d = Drawing(480, 190)
    if kind == "usecase":
        d.add(Rect(85, 12, 305, 168, strokeColor=NAVY, fillColor=colors.white, strokeWidth=1.2))
        label(d, 237, 165, "TriadLens", 10)
        for x, y, text in [(145,125,"Load example"),(310,125,"Enter features"),(145,80,"Compare models"),(310,80,"Inspect metrics"),(145,35,"Train models"),(310,35,"Deploy service")]:
            d.add(Ellipse(x, y, 66, 16, strokeColor=TEAL, fillColor=PALE))
            label(d, x, y-3, text, 7)
        label(d, 35, 100, "Student", 9)
        label(d, 445, 35, "Operator", 9)
        for x2,y2 in [(80,125),(245,125),(80,80),(245,80)]:
            d.add(Line(65,100,x2,y2,strokeColor=NAVY))
        for x2 in (80,245):
            d.add(Line(410,35,x2,35,strokeColor=NAVY))
    elif kind == "component":
        boxes=[(15,80,85,"Browser UI"),(125,80,85,"Flask API"),(245,125,100,"Input Validator"),(245,75,100,"Prediction Audit"),(245,25,100,"ML / DL / QML"),(380,80,90,"Artifacts")]
        for x,y,w,t in boxes:
            d.add(Rect(x,y,w,32,strokeColor=TEAL,fillColor=PALE,rx=5,ry=5))
            label(d,x+w/2,y+12,t,8)
        arrow(d,100,96,125,96)
        for y in (141,91,41):
            arrow(d,210,96,245,y)
            arrow(d,345,y,380,96)
        label(d,235,174,"Online inference components",10)
    elif kind == "deployment":
        boxes=[(10,80,75,"Browser"),(110,80,85,"K8s Service"),(225,120,100,"Pod 1: Flask"),(225,40,100,"Pod 2: Flask"),(365,120,105,"Docker Hub image"),(365,40,105,"Artifact Secrets")]
        for x,y,w,t in boxes:
            d.add(Rect(x,y,w,32,strokeColor=TEAL,fillColor=PALE,rx=5,ry=5))
            label(d,x+w/2,y+12,t,8)
        arrow(d,85,96,110,96)
        arrow(d,195,96,225,136)
        arrow(d,195,96,225,56)
        arrow(d,365,136,325,136)
        arrow(d,365,136,325,56)
        arrow(d,365,56,325,136)
        arrow(d,365,56,325,56)
        label(d,235,174,"Two replicas with private model mounts",10)
    else:
        training = kind == "train"
        names=["Operator" if training else "Student","train.py" if training else "Browser","Models" if training else "Flask API","Reports" if training else "Adapters"]
        xs=[50,165,300,425]
        for x,n in zip(xs,names):
            d.add(Rect(x-37,150,74,22,strokeColor=NAVY,fillColor=PALE))
            label(d,x,158,n,8)
            d.add(Line(x,20,x,150,strokeColor=colors.black,strokeWidth=.7,strokeDashArray=[3,3]))
        messages=([("Enter features",0,1),("POST /api/predict",1,2),("Validate input",2,2),("Run ML, DL, QML",2,3),("Results + audit",2,1)] if not training else
                  [("Run training",0,1),("Clean and split",1,1),("Fit three models",1,2),("Evaluate test set",2,1),("Save evidence",1,3)])
        for i,(t,a,b) in enumerate(messages):
            y=132-i*25
            arrow(d,xs[a],y,xs[b],y)
            label(d,(xs[a]+xs[b])/2,y+5,t,6.6)
    return d


def parse(path):
    lines=path.read_text(encoding="utf-8").splitlines()
    if len(lines) > 1 and lines[0].startswith("# ") and lines[1].startswith("# "):
        lines = lines[1:]
    placeholder_prefixes = (
        "Student: project team",
        "Tester: project team",
        "Class, section and instructor: complete on the private submission copy",
        "Instructor review: pending",
    )
    lines = [line for line in lines if not line.startswith(placeholder_prefixes)]
    story=[]
    private_meta=HERE.parent / ".private_submission.txt"
    i=0
    mermaid_number=0
    while i<len(lines):
        line=lines[i].strip()
        if not line:
            i+=1;continue
        if line.startswith("```mermaid"):
            i+=1
            while i<len(lines) and not lines[i].startswith("```"):
                i+=1
            i+=1
            if path.name == "SRS.md":
                kind="usecase"
            elif mermaid_number==0:
                kind="component"
            elif mermaid_number==1:
                kind="deployment"
            elif mermaid_number==2:
                kind="compare"
            else:
                kind="train"
            mermaid_number+=1
            story.extend([Spacer(1,6),diagram(kind),Spacer(1,7)])
            continue
        if line.startswith("|"):
            rows=[]
            while i<len(lines) and lines[i].strip().startswith("|"):
                cells=[x.strip() for x in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{2,}:?",x) for x in cells):
                    rows.append(cells)
                i+=1
            if rows:
                width=511/len(rows[0])
                table=Table([[Paragraph(markup(c),styles["HeaderCellX"] if n==0 else styles["CellX"]) for c in row] for n,row in enumerate(rows)],colWidths=[width]*len(rows[0]),repeatRows=1,hAlign="LEFT")
                table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),colors.white),("VALIGN",(0,0),(-1,-1),"TOP"),("GRID",(0,0),(-1,-1),.35,colors.black),("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
                story.extend([Spacer(1,5),table,Spacer(1,8)])
            continue
        if line.startswith("# "):
            story.append(Paragraph(markup(line[2:]),styles["DocTitleX"]))
            if private_meta.exists():
                identity = private_meta.read_text(encoding="utf-8").strip().replace("Private submission copy | ", "")
                story.append(Paragraph(markup(identity), styles["BodyX"]))
        elif line.startswith("## "):
            story.append(Paragraph(markup(line[3:]),styles["H1X"]))
        elif line.startswith("### "):
            story.append(Paragraph(markup(line[4:]),styles["H2X"]))
        else:
            parts=[line]
            while i+1<len(lines) and lines[i+1].strip() and not lines[i+1].lstrip().startswith(("#","|","```")):
                i+=1;parts.append(lines[i].strip())
            story.append(Paragraph(markup(" ".join(parts)),styles["BodyX"]))
        i+=1
    return story


for source in [HERE/"SRS.md", HERE/"System_Test_Plan.md", HERE/"Architecture_Design.md"]:
    target=OUT/source.with_suffix(".pdf").name
    doc=SimpleDocTemplate(str(target),pagesize=(595.28,841.89),leftMargin=42,rightMargin=42,topMargin=42,bottomMargin=42,title=source.stem,author="Aryan Vinju")
    doc.build(parse(source))
    print(target)
