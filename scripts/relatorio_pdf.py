#!/usr/bin/env python3
"""Renderizador local de relatório Markdown simples (ReportLab)."""
from pathlib import Path
import re,sys,html
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,KeepTogether,Image
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
font_pairs = [
 ('/System/Library/Fonts/Supplemental/Arial Unicode.ttf','/System/Library/Fonts/Supplemental/Arial Bold.ttf'),
 ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),
]
import reportlab
font_dir=Path(reportlab.__file__).parent/'fonts'
font_pairs.append((str(font_dir/'Vera.ttf'),str(font_dir/'VeraBd.ttf')))
font_regular,font_bold=next((a,b) for a,b in font_pairs if Path(a).is_file() and Path(b).is_file())
pdfmetrics.registerFont(TTFont('ReportArial',font_regular))
pdfmetrics.registerFont(TTFont('ReportArialBold',font_bold))
pdfmetrics.registerFontFamily('ReportArial',normal='ReportArial',bold='ReportArialBold',italic='ReportArial',boldItalic='ReportArialBold')
source=Path(sys.argv[1]);target=Path(sys.argv[2])
styles=getSampleStyleSheet()
styles['Normal'].fontName='ReportArial';styles['Normal'].fontSize=9.5;styles['Normal'].leading=14;styles['Normal'].spaceAfter=7
styles['Title'].fontName='ReportArialBold';styles['Title'].textColor=colors.HexColor('#114d3d');styles['Title'].fontSize=23;styles['Title'].leading=28
for name,size in [('Heading1',16),('Heading2',13),('Heading3',11)]:
 styles[name].fontName='ReportArialBold';styles[name].textColor=colors.HexColor('#114d3d');styles[name].fontSize=size;styles[name].leading=size+4;styles[name].spaceBefore=13;styles[name].spaceAfter=7
styles.add(ParagraphStyle('Cell',parent=styles['Normal'],fontSize=7.3,leading=10,spaceAfter=0))
styles.add(ParagraphStyle('CodeText',parent=styles['Normal'],fontName='Courier',fontSize=7.5,leading=10))

def inline(s):
 s=html.escape(s)
 s=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',s)
 s=re.sub(r'`([^`]+)`',r'<font name="Courier">\1</font>',s)
 s=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',r'\1',s)
 return s

def page(canvas,doc):
 canvas.setStrokeColor(colors.HexColor('#2d8865'));canvas.line(42,805,553,805)
 canvas.setFont('Helvetica',7);canvas.setFillColor(colors.HexColor('#52625e'))
 canvas.drawString(42,817,'ANÁLISE DE INVESTIMENTOS | RELATÓRIO')
 canvas.drawString(42,25,'Relatório independente • Premissas e limitações explicitadas no texto')
 canvas.drawRightString(553,25,str(doc.page))

lines=source.read_text().splitlines();story=[];i=0
while i<len(lines):
 line=lines[i].strip()
 if not line: i+=1;continue
 im=re.match(r'^!\[([^]]*)\]\(([^)]+)\)$',line)
 if im:
  path=source.parent/im.group(2)
  obj=Image(str(path));ratio=min(511/obj.imageWidth,430/obj.imageHeight)
  obj.drawWidth=obj.imageWidth*ratio;obj.drawHeight=obj.imageHeight*ratio
  story.extend([obj,Paragraph(inline(im.group(1)),styles['Cell']),Spacer(1,12)]);i+=1;continue
 if line.startswith('|'):
  rows=[]
  while i<len(lines) and lines[i].strip().startswith('|'):
   row=[s.strip() for s in lines[i].strip().strip('|').split('|')]
   if not all(re.fullmatch(r':?-+:?',s) for s in row): rows.append(row)
   i+=1
  cols=max(map(len,rows));width=511/cols
  cells=[[Paragraph(inline(s),styles['Cell']) for s in row]+['']*(cols-len(row)) for row in rows]
  table=Table(cells,colWidths=[width]*cols,repeatRows=1,hAlign='LEFT')
  table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e0eee7')),('LINEBELOW',(0,0),(-1,0),.7,colors.HexColor('#2d8865')),('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),6),('LINEBELOW',(0,1),(-1,-1),.25,colors.HexColor('#d4dfda'))]))
  story.extend([table,Spacer(1,9)]);continue
 if line.startswith('```'):
  i+=1;code=[]
  while i<len(lines) and not lines[i].strip().startswith('```'):code.append(lines[i]);i+=1
  story.append(Paragraph('<br/>'.join(html.escape(s) for s in code),styles['CodeText']));i+=1;continue
 m=re.match(r'^(#{1,4})\s+(.*)',line)
 if m:
  level=len(m.group(1));sty='Title' if level==1 and not story else 'Heading'+str(min(level,3))
  story.append(Paragraph(inline(m.group(2)),styles[sty]));i+=1;continue
 if re.fullmatch(r'[-*_]{3,}',line):i+=1;continue
 if re.match(r'^\d+\.\s',line):
  story.append(Paragraph(inline(line),styles['Normal']));i+=1;continue
 if line.startswith(('- ','* ')):
  story.append(Paragraph('• '+inline(line[2:]),styles['Normal']));i+=1;continue
 para=[line];i+=1
 while i<len(lines) and lines[i].strip() and not lines[i].strip().startswith(('#','|','- ','* ','```','![')) and not re.match(r'^\d+\.\s',lines[i].strip()):
  para.append(lines[i].strip());i+=1
 story.append(Paragraph(inline(' '.join(para)),styles['Normal']))
SimpleDocTemplate(str(target),pagesize=A4,rightMargin=42,leftMargin=42,topMargin=51,bottomMargin=44,title=source.stem,author='Análise independente').build(story,onFirstPage=page,onLaterPages=page)
print(target)
