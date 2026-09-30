from pathlib import Path
import argparse,json,hashlib,html,re
import matplotlib
matplotlib.use('Agg')
from matplotlib import mathtext,font_manager,get_data_path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg
BASE=None
CACHE=None
FONT=Path(get_data_path())/'fonts'/'ttf'
for nm,fn in [('Body','DejaVuSerif.ttf'),('Bold','DejaVuSerif-Bold.ttf'),('Sans','DejaVuSans.ttf')]:pdfmetrics.registerFont(TTFont(nm,str(FONT/fn)))
matplotlib.rcParams.update({'mathtext.fontset':'stix','font.family':'STIXGeneral','svg.fonttype':'path'})
W,H=A4;LEFT=48;RIGHT=48;CW=W-LEFT-RIGHT;BOTTOM=48
styles={
'p':ParagraphStyle('p',fontName='Body',fontSize=10.2,leading=14.1,spaceAfter=6),
'question':ParagraphStyle('q',fontName='Bold',fontSize=10.4,leading=14.4,spaceAfter=7),
'hint':ParagraphStyle('h',fontName='Body',fontSize=9.3,leading=12.7,textColor='#555555',spaceAfter=7),
'source':ParagraphStyle('s',fontName='Sans',fontSize=7.7,leading=10.2,textColor='#666666',spaceAfter=12),
'heading':ParagraphStyle('heading',fontName='Bold',fontSize=16,leading=20,spaceAfter=7),
}
cache={}
def para(t,kind='p'):
 font=styles[kind].fontName
 missing={ch for ch in t if not ch.isspace() and ch not in '≪≫' and ord(ch) not in pdfmetrics.getFont(font).face.charToGlyph}
 if missing:raise ValueError('Unsupported text glyphs; use a vector equation: '+', '.join(f'U+{ord(ch):04X}' for ch in sorted(missing)))
 safe=html.escape(t).replace('—','-').replace('–','-').replace('\n','<br/>').replace('≪','<font name="Sans">≪</font>').replace('≫','<font name="Sans">≫</font>')
 safe=re.sub(r'(https?://[^\s;<>]+)',r'<link href="\1" color="#333333">\1</link>',safe)
 return Paragraph(safe,styles[kind])
def vector(expr):
 expr=expr.replace(r'\frac',r'\dfrac').replace(r'\mathbf R',r'\mathbf{R}').replace(r'\big(',r'\left(').replace(r'\big)',r'\right)').replace(r'\big[',r'\left[').replace(r'\big]',r'\right]')
 key=hashlib.sha256(('13.5:'+expr).encode()).hexdigest()[:20];p=CACHE/(key+'.svg')
 if not p.exists():mathtext.math_to_image('$'+expr+'$',p,prop=font_manager.FontProperties(size=13.5),format='svg',color='black')
 if key not in cache:cache[key]=svg2rlg(str(p))
 return cache[key]
def getblock(b):
 kind=b['kind']
 if kind=='link':
  para(b['text'])
  o=Paragraph('<link href="'+html.escape(b['url'],quote=True)+'" color="#222222"><b>'+html.escape(b['text'])+'</b></link>',styles['p']);_,height=o.wrap(CW,10000);return o,height+5,'paragraph',1
 if kind in ('p','question','hint'):
  o=para(b['text'],kind);_,height=o.wrap(CW,10000);return o,height+styles[kind].spaceAfter,'paragraph',1
 if kind=='eq':
  o=vector(b['text']);scale=min(1.0,(CW-10)/o.width)
  if scale<.80:raise ValueError('Split the equation into shorter lines: '+b['text'])
  return o,o.height*scale+10,'vector',scale
 if kind=='diagram':
  path=BASE/b['path']
  if not path.exists():raise ValueError('Missing diagram '+b['name'])
  o=svg2rlg(str(path));scale=min((CW-20)/o.width,120/o.height,1);return o,o.height*scale+10,'vector',scale
 if kind=='image':
  from reportlab.lib.utils import ImageReader
  from reportlab.platypus import Image
  path=BASE/b['path']; reader=ImageReader(str(path)); width,height=reader.getSize()
  scale=min((CW-20)/width,160/height,1)
  o=Image(str(path),width=width*scale,height=height*scale)
  return o,o.drawHeight+10,'image',1
 if kind=='table':
  from reportlab.platypus import Table,TableStyle
  o=Table([[para(str(c),'hint') for c in row] for row in b['rows']],colWidths=[CW/len(b['rows'][0])]*len(b['rows'][0]))
  o.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.5,'#777777'),('BOTTOMPADDING',(0,0),(-1,-1),5)]));_,height=o.wrap(CW,10000);return o,height+8,'paragraph',1
 raise ValueError(kind)


def units_from(spec):
 sections=spec['sections']
 if not sections or any(not s.get('units') for s in sections):raise ValueError('Use nonempty sections')
 units=[u for s in sections for u in s['units']]
 ids=[u['id'] for u in units]
 if len(set(ids))!=len(ids):raise ValueError('Unit IDs must be unique')
 for u in units:
  if not u['id'] or not u['title'] or not u['blocks']:raise ValueError('Incomplete unit')
  if u.get('priority') not in (None,'Start here','Core practice','Extension'):raise ValueError('Unknown priority')
 return units


def index_columns(sections):
 def height(items):return sum(32+14.5*len(s['units']) for s in items)
 if len(sections)==1:
  us=sections[0]['units'];mid=(len(us)+1)//2
  cols=[[dict(name=sections[0]['name'],units=us[:mid])]]
  cols.append([dict(name=sections[0]['name']+' (continued)',units=us[mid:])] if us[mid:] else [])
 else:
  split=min(range(1,len(sections)),key=lambda i:max(height(sections[:i]),height(sections[i:])))
  cols=[sections[:split],sections[split:]]
 if max(map(height,cols))>H-201:raise ValueError('Index overflows: use concise group-level entries or split the assessment')
 return cols


def build(spec,filename,total=None,toc=None,record=False):
 c=canvas.Canvas(str(filename),pagesize=A4,pageCompression=1)
 c.setTitle(spec['title']+' - '+spec.get('subtitle','Notes and worked solutions'))
 c.setAuthor('Abhinav Pullela . mcarkade')
 number=0;positions=[];metrics=[];has_index=spec.get('mode','full')=='full'
 def endpage():
  c.setFont('Sans',7.5);c.setFillColorRGB(.4,.4,.4)
  c.drawString(LEFT,24,'Abhinav Pullela . mcarkade')
  label='Index' if has_index else 'Start'
  c.drawCentredString(W/2,24,label)
  c.linkRect('', 'contents',(W/2-15,20,W/2+15,33),relative=0,thickness=0)
  c.drawRightString(W-RIGHT,24,str(number)+(f' / {total}' if total else ''))
  c.setFillColorRGB(0,0,0);c.showPage()
 def newpage(unit,continued=False):
  nonlocal number
  if number:endpage()
  number+=1;y=H-42
  if not has_index and number==1:c.bookmarkPage('contents')
  if not continued:
   c.bookmarkPage(unit['id']);c.addOutlineEntry(unit['id']+' '+unit['title'],unit['id'],level=0)
   positions.append(dict(id=unit['id'],title=unit['title'],page=number))
  title=unit['id']+' '+unit['title']+(' (continued)' if continued else '')
  obj=para(title,'heading');_,hh=obj.wrap(CW,1000);obj.drawOn(c,LEFT,y-hh);y-=hh+7
  source=unit.get('source','')
  if unit.get('priority'):source=unit['priority']+(' | '+source if source else '')
  obj=para(source,'source');_,hh=obj.wrap(CW,1000);obj.drawOn(c,LEFT,y-hh);y-=hh+13
  return y
 if has_index:
  number=1;c.bookmarkPage('contents');c.addOutlineEntry('Index','contents',level=0)
  c.setFont('Bold',26);c.drawString(LEFT,H-60,spec['title'])
  c.setFont('Body',12);c.drawString(LEFT,H-83,spec.get('subtitle','Notes and worked solutions'))
  c.setFont('Sans',8.5);c.setFillColorRGB(.38,.38,.38);c.drawString(LEFT,H-102,spec.get('exam_line',''))
  c.setFillColorRGB(0,0,0);colw=(CW-26)/2
  page_lookup={x['id']:x['page'] for x in (toc or [])}
  for col,sections in enumerate(index_columns(spec['sections'])):
   x=LEFT+col*(colw+26);y=H-139
   for section in sections:
    c.setFont('Bold',10);c.drawString(x,y,section['name']);y-=20
    for u in section['units']:
     label=u.get('index_title',u['title']);font_size=8.4
     while pdfmetrics.stringWidth(label,'Sans',font_size)>colw-48 and font_size>7.5:font_size-=.1
     if pdfmetrics.stringWidth(label,'Sans',font_size)>colw-48:raise ValueError('Shorten index title: '+label)
     c.setFont('Sans',7.6);c.setFillColorRGB(.4,.4,.4);c.drawString(x,y,u['id'])
     c.setFont('Sans',font_size);c.setFillColorRGB(0,0,0);c.drawString(x+29,y,label)
     c.setFont('Sans',8);c.drawRightString(x+colw,y,str(page_lookup.get(u['id'],0)))
     c.linkRect('',u['id'],(x,y-3,x+colw,y+10),relative=0,thickness=0);y-=14.5
    y-=12
  c.setFont('Sans',8);c.setFillColorRGB(.4,.4,.4)
  route=spec.get('route','Select any entry to open it. Use Index in the footer to return here.')
  if pdfmetrics.stringWidth(route,'Sans',8)>CW:raise ValueError('Shorten the study route to one line')
  c.drawString(LEFT,72,route);c.setFillColorRGB(0,0,0)
 for u in units_from(spec):
  y=newpage(u)
  for i,b in enumerate(u['blocks']):
   try:o,h,typ,scale=getblock(b)
   except Exception as ex:raise ValueError(f"{u['id']} block {i}: {ex}") from ex
   if y-h<BOTTOM:y=newpage(u,continued=True)
   if y-h<BOTTOM:raise ValueError(f"{u['id']}: block exceeds usable page height")
   if typ=='paragraph':
    _,oh=o.wrap(CW,10000);o.drawOn(c,LEFT,y-oh)
   elif typ=='image':o.drawOn(c,LEFT+(CW-o.drawWidth)/2,y-o.drawHeight)
   else:
    c.saveState();c.translate(LEFT+(CW-o.width*scale)/2,y-o.height*scale)
    c.scale(scale,scale);renderPDF.draw(o,c,0,0);c.restoreState()
   if record:metrics.append(dict(page=number,unit=u['id'],kind=b['kind'],top=y,bottom=y-h,scale=scale))
   y-=h
 if number:endpage()
 c.save();return number,positions,metrics


def main():
 global BASE,CACHE
 ap=argparse.ArgumentParser(description='Render study notes in the retained optics layout')
 ap.add_argument('input',type=Path);ap.add_argument('--output',required=True,type=Path)
 ap.add_argument('--work-dir',required=True,type=Path);args=ap.parse_args()
 BASE=args.input.resolve().parent;CACHE=args.work_dir.resolve()/'equations';CACHE.mkdir(parents=True,exist_ok=True)
 args.output.parent.mkdir(parents=True,exist_ok=True)
 spec=json.loads(args.input.read_text(encoding='utf-8-sig'))
 if spec.get('mode','full') not in ('full','cram'):raise ValueError('Mode must be full or cram')
 units=units_from(spec)
 for u in units:
  for b in u['blocks']:getblock(b)
 total,pos,_=build(spec,args.output)
 total,pos,metrics=build(spec,args.output,total,toc=pos,record=True)
 manifest=dict(pdf=str(args.output.resolve()),pages=total,mode=spec.get('mode','full'),units=pos,blocks=metrics)
 (args.work_dir/'layout.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
 print(f'{args.output}: {total} pages, {len(units)} units')

if __name__=='__main__':main()
