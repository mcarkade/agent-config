"""Render reusable study guides in the established warm dark layout."""
from pathlib import Path
import argparse,json,hashlib,html,re,copy
import matplotlib
matplotlib.use('Agg')
from matplotlib import mathtext,font_manager,get_data_path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg
import xml.etree.ElementTree as ET
from PIL import Image

PALETTE={'background':'#211D19','body':'#F2E8DB','heading':'#FFF2DF','secondary':'#C8B6A1','muted':'#B8A48D','link':'#DDB079','border':'#B88959'}
W,H=A4;LEFT=48;RIGHT=48;CW=W-LEFT-RIGHT;BOTTOM=48;CACHE=None;BASE=None
FONT=Path(get_data_path())/'fonts'/'ttf'
for nm,fn in [('Body','DejaVuSerif.ttf'),('Bold','DejaVuSerif-Bold.ttf'),('Sans','DejaVuSans.ttf')]:pdfmetrics.registerFont(TTFont(nm,str(FONT/fn)))
matplotlib.rcParams.update({'mathtext.fontset':'stix','font.family':'STIXGeneral','svg.fonttype':'path'})
styles={
 'p':ParagraphStyle('p',fontName='Body',fontSize=10.2,leading=14.1,textColor=PALETTE['body'],spaceAfter=7),
 'secondary':ParagraphStyle('secondary',fontName='Body',fontSize=10.2,leading=14.1,textColor=PALETTE['secondary'],spaceAfter=7),
 'question':ParagraphStyle('question',fontName='Bold',fontSize=10.4,leading=14.4,textColor=PALETTE['body'],spaceAfter=9),
 'hint':ParagraphStyle('hint',fontName='Body',fontSize=9.3,leading=12.7,textColor=PALETTE['secondary'],spaceAfter=7),
 'source':ParagraphStyle('source',fontName='Sans',fontSize=7.7,leading=10.2,textColor=PALETTE['muted'],spaceAfter=10),
 'heading':ParagraphStyle('heading',fontName='Bold',fontSize=16,leading=20,textColor=PALETTE['heading'],spaceAfter=7),
 'solution_label':ParagraphStyle('solution_label',fontName='Bold',fontSize=9.6,leading=13,textColor=PALETTE['heading'],spaceAfter=8),
 'example_label':ParagraphStyle('example_label',fontName='Sans',fontSize=8.8,leading=12,textColor=PALETTE['link'],spaceAfter=6),
}
cache={}
def inline_markup(text):
    """Typeset explicit plain-source powers/subscripts without exposing delimiters."""
    out=[];i=0
    while i<len(text):
        ch=text[i]
        if ch in '^_' and i+1<len(text):
            j=i+1
            if text[j]=='(':
                level=1;k=j+1
                while k<len(text) and level:
                    level+=(text[k]=='(')-(text[k]==')');k+=1
                if level==0: token=text[j+1:k-1];end=k
                else:out.append(html.escape(ch));i+=1;continue
            else:
                m=re.match(r'(?:[−+\-]?\d+|[A-Za-z]|in\b|out\b)',text[j:])
                if not m:out.append(html.escape(ch));i+=1;continue
                token=m.group(0);end=j+len(token)
                if ch=='_' and text[j:].startswith(('in','out')):
                    token='out' if text[j:].startswith('out') else 'in';end=j+len(token)
            tag='super' if ch=='^' else 'sub'
            out.append('<'+tag+'>'+html.escape(token)+'</'+tag+'>');i=end;continue
        out.append('<br/>' if ch=='\n' else html.escape(ch));i+=1
    return ''.join(out)
def para(text,kind='p',math_segments=None,bold=False):
    font=pdfmetrics.getFont(styles[kind].fontName)
    missing={ch for ch in text if not ch.isspace() and ord(ch) not in font.face.charToGlyph}
    if missing:raise ValueError('Unsupported text glyphs: '+str(missing))
    inline_drawings=[]
    if math_segments is not None:
        safe=''
        placeholder=CACHE.parent/'inline-placeholder.png'
        if not placeholder.exists():Image.new('RGBA',(1,1),(0,0,0,0)).save(placeholder)
        for segment in math_segments:
            if 'text' in segment:safe+=inline_markup(segment['text'])
            else:
                expr=segment['math'];drawing=vector(expr,size=styles[kind].fontSize)
                _,_,depth,_,_=mathtext.MathTextParser('path').parse('$'+normalize(expr)+'$',dpi=72,prop=font_manager.FontProperties(size=styles[kind].fontSize))
                safe+='<img src="'+html.escape(str(placeholder),quote=True)+'" width="'+str(drawing.width)+'" height="'+str(drawing.height)+'" valign="'+str(-depth)+'"/>'
                inline_drawings.append(drawing)
    else:safe=inline_markup(text)
    safe=re.sub(r'(https?://[^\s;<>]+)',r'<link href="\1" color="'+PALETTE['link']+r'"><u width="0.35">\1</u></link>',safe)
    sty=copy.copy(styles[kind])
    if bold:sty.fontName='Bold'
    if math_segments is not None:sty.autoLeading='max'
    paragraph=Paragraph(safe,sty)
    images=[f.cbDefn for f in paragraph.frags if getattr(getattr(f,'cbDefn',None),'kind',None)=='img']
    if len(images)!=len(inline_drawings):raise ValueError('Inline math fragment mismatch')
    for fragment,drawing in zip(images,inline_drawings):fragment.image._study_vector=drawing
    return paragraph
def normalize(expr):
    return expr.replace(r'\frac',r'\dfrac').replace(r'\mathbf R',r'\mathbf{R}').replace(r'\big(',r'\left(').replace(r'\big)',r'\right)').replace(r'\big[',r'\left[').replace(r'\big]',r'\right]')
def vector(expr,size=13.5):
    expr=normalize(expr);key=hashlib.sha256((str(size)+':'+PALETTE['body']+':'+expr).encode()).hexdigest()[:20];p=CACHE/(key+'.svg')
    if not p.exists():
        mathtext.math_to_image('$'+expr+'$',p,prop=font_manager.FontProperties(size=size),format='svg',color=PALETTE['body'])
        ET.register_namespace('', 'http://www.w3.org/2000/svg');ET.register_namespace('xlink','http://www.w3.org/1999/xlink')
        tree=ET.parse(p)
        for parent in tree.getroot().iter():
            for child in list(parent):
                if child.get('id')=='patch_1':parent.remove(child)
        tree.write(p,encoding='utf8',xml_declaration=True)
    if key not in cache:cache[key]=svg2rlg(str(p))
    return cache[key]
def getblock(b,width=CW):
    kind=b['kind']
    if kind=='spacer':return None,b['height'],'spacer',1
    if kind=='eq':
        o=vector(b.get('display_text',b['text']));scale=min(1,(width-2)/o.width)
        if scale<.8:raise ValueError('Split the equation instead of shrinking: '+b['text'])
        return o,o.height*scale+10,'vector',scale
    if kind=='diagram':
        path=BASE/b['path']
        if not path.exists():raise ValueError('Missing diagram '+str(path))
        o=svg2rlg(str(path));scale=min((width-20)/o.width,b.get('max_height',180)/o.height,1)
        return o,o.height*scale+10,'vector',scale
    if kind=='image':
        from reportlab.platypus import Image as PDFImage
        from reportlab.lib.utils import ImageReader
        path=BASE/b['path'];iw,ih=ImageReader(str(path)).getSize()
        scale=min((width-20)/iw,b.get('max_height',160)/ih,1)
        o=PDFImage(str(path),width=iw*scale,height=ih*scale)
        return o,o.drawHeight+10,'image',1
    if kind=='table':
        from reportlab.platypus import Table,TableStyle
        o=Table([[para(str(v),'hint') for v in row] for row in b['rows']],colWidths=[width/len(b['rows'][0])]*len(b['rows'][0]))
        o.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.5,PALETTE['border']),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
        _,oh=o.wrap(width,10000);return o,oh+8,'paragraph',1
    if kind=='link':
        o=Paragraph('<link href="'+html.escape(b['url'],quote=True)+'" color="'+PALETTE['link']+'"><u width="0.35"><b>'+html.escape(b['text'])+'</b></u></link>',styles['p'])
    else:
        o=para(b['text'],kind,b.get('math_segments'),b.get('bold',False))
    _,oh=o.wrap(width,10000)
    before=8 if kind in ('solution_label','example_label') else 0
    return o,oh+styles.get(kind,styles['p']).spaceAfter+before,'paragraph',1
def units_from(spec):
    sections=spec.get('sections',[])
    if not sections or any(not s.get('units') for s in sections):raise ValueError('Use nonempty sections')
    units=[u for s in sections for u in s['units']]
    if len({u['id'] for u in units})!=len(units):raise ValueError('Unit IDs must be unique')
    for u in units:
        if not u['id'] or not u['title'] or not u['blocks']:raise ValueError('Incomplete unit')
        if u.get('role') not in (None,'notes','question','formula','reference'):raise ValueError('Unknown unit role')
        if u.get('estimated_minutes') is not None and (not isinstance(u['estimated_minutes'],(int,float)) or u['estimated_minutes']<0):raise ValueError('Use nonnegative unit minutes')
        for i,b in enumerate(u['blocks']):
            if u.get('role')=='formula' and b['kind']=='eq' and 'box' not in b:b['box']=True
            if b.get('box') is True:b['box']=u['id']+':'+str(i)
    minutes=sum(u.get('estimated_minutes') or 0 for u in units)
    if spec.get('estimated_minutes') is not None and spec['estimated_minutes']!=minutes:raise ValueError('Total time differs from unit estimates')
    spec['estimated_minutes']=minutes
    return units

def index_columns(spec):
    flat=[(section['name'],unit) for section in spec['sections'] for unit in section['units']]
    def group(entries):
        out=[]
        for name,unit in entries:
            if not out or out[-1]['name']!=name:out.append({'name':name,'units':[]})
            out[-1]['units'].append(unit)
        return out
    def height(entries):return sum(32+12.7*len(s['units']) for s in group(entries))
    split=min(range(1,len(flat)),key=lambda i:max(height(flat[:i]),height(flat[i:]))) if len(flat)>1 else 1
    return [group(flat[:split]),group(flat[split:])]

def box_geometry(blocks):
    equations=[vector(b.get('display_text',b['text'])).width for b in blocks if b['kind']=='eq']
    prose=[b for b in blocks if b['kind'] not in ('eq','spacer')]
    natural=max(equations or [0])
    for b in prose:
        sty=styles[b['kind']]
        length=max(pdfmetrics.stringWidth(line,sty.fontName,sty.fontSize) for line in b['text'].splitlines() or [''])
        natural=max(natural,min(length,360))
    content_width=min(CW,max(natural+2,40))
    height=sum(getblock(b,content_width)[1] for b in blocks)
    return content_width,height

def flow_height(blocks,index,with_end=False):
    """Keep an example opening, its data and Solution with the first worked step."""
    target=min(index+3,len(blocks)-1)
    if blocks[index]['kind'] in ('example_label','question'):
        questions=0
        for k in range(index+1,min(len(blocks),index+22)):
            if blocks[k]['kind']=='example_label':break
            if blocks[k]['kind']=='question':
                questions+=1
                if blocks[index]['kind']=='question' or questions>1:break
            if blocks[k]['kind']=='solution_label':target=min(k+3,len(blocks)-1);break
    for k in range(index+1,target+1):
        if blocks[k]['kind'] in ('question','example_label') and blocks[index]['kind'] not in ('example_label','question'):
            target=k-1;break
    total=0;k=index
    while k<len(blocks):
        b=blocks[k];end=k+1
        if b.get('box'):
            while end<len(blocks) and blocks[end].get('box')==b['box']:end+=1
            total+=box_geometry(blocks[k:end])[1]+13
        else:total+=getblock(b)[1]
        last=blocks[end-1]
        keep=last.get('keep_next') or last['kind'] in ('example_label','question','solution_label','source') or (last['kind'] in ('p','hint','secondary') and len(last['text'])<220 and last['text'].rstrip().endswith(':'))
        if end-1>=target and not keep:break
        k=end
    return (total,end-1) if with_end else total
class MathCanvas(canvas.Canvas):
    def drawImage(self,image,x,y,width=None,height=None,*args,**kwargs):
        drawing=getattr(image,'_study_vector',None)
        if drawing is None:return super().drawImage(image,x,y,width,height,*args,**kwargs)
        self.saveState();self.translate(x,y);self.scale(width/drawing.width,height/drawing.height);renderPDF.draw(drawing,self,0,0);self.restoreState()
        return width,height

def build(spec,filename,total=None,toc=None,record=False):
    c=MathCanvas(str(filename),pagesize=A4,pageCompression=1)
    c.setTitle(spec['title']+' - '+spec.get('subtitle','Notes and worked solutions'));c.setAuthor('Abhinav Pullela . mcarkade')
    number=0;positions=[];metrics=[];rectangles=[];has_index=spec.get('mode','full')=='full'
    def background():
        c.setFillColor(HexColor(PALETTE['background']));c.rect(0,0,W,H,stroke=0,fill=1);c.setFillColor(HexColor(PALETTE['body']))
    def endpage():
        c.setFont('Sans',7.5);c.setFillColor(HexColor(PALETTE['muted']));c.drawString(LEFT,24,'Abhinav Pullela . mcarkade')
        label='Index' if has_index else 'Start'
        c.setFillColor(HexColor(PALETTE['link']));c.drawCentredString(W/2,24,label)
        c.setStrokeColor(HexColor(PALETTE['link']));c.setLineWidth(.35);index_width=pdfmetrics.stringWidth(label,'Sans',7.5);c.line((W-index_width)/2,22.3,(W+index_width)/2,22.3)
        c.linkRect('','contents',(W/2-15,20,W/2+15,33),relative=0,thickness=0)
        c.setFillColor(HexColor(PALETTE['muted']));c.drawRightString(W-RIGHT,24,str(number)+(f' / {total}' if total else ''));c.showPage()
    def newpage(unit,continued=False):
        nonlocal number
        if number:endpage()
        number+=1;background();y=H-48
        if not has_index and number==1:c.bookmarkPage('contents',fit='XYZ',left=0,top=H,zoom=None)
        if continued:return y
        return unit_heading(unit,H-42)
    def unit_heading(unit,y):
        c.bookmarkPage(unit['id'],fit='XYZ',left=0,top=H,zoom=None);c.addOutlineEntry(unit['id']+' '+unit['title'],unit['id'],level=0)
        positions.append({'id':unit['id'],'title':unit['title'],'page':number,'start_top':y,'estimated_minutes':unit.get('estimated_minutes')})
        if unit.get('estimated_minutes') is not None:
            c.setFont('Sans',8.5);c.setFillColor(HexColor(PALETTE['muted']));c.drawRightString(W-RIGHT,y+18,'~'+format(unit['estimated_minutes'],'g')+' min')
        o=para(unit['id']+' '+unit['title'],'heading');_,oh=o.wrap(CW,1000);o.drawOn(c,LEFT,y-oh);y-=oh+7
        o=para(unit.get('source',''),'source');_,oh=o.wrap(CW,1000);o.drawOn(c,LEFT,y-oh);return y-oh-13
    if has_index:
        number=1;background();c.bookmarkPage('contents',fit='XYZ',left=0,top=H,zoom=None);c.addOutlineEntry('Index','contents',level=0)
        if spec['estimated_minutes']:
            c.setFont('Sans',8.5);c.setFillColor(HexColor(PALETTE['muted']));c.drawRightString(W-RIGHT,H-24,'~'+format(spec['estimated_minutes'],'g')+' min total')
        c.setFillColor(HexColor(PALETTE['heading']));c.setFont('Bold',26);c.drawString(LEFT,H-60,spec['title'])
        c.setFillColor(HexColor(PALETTE['body']));c.setFont('Body',12);c.drawString(LEFT,H-83,spec.get('subtitle','Notes and worked solutions'))
        c.setFillColor(HexColor(PALETTE['muted']));c.setFont('Sans',8.5);c.drawString(LEFT,H-102,spec.get('exam_line',''))
        colw=(CW-26)/2;lookup={x['id']:x['page'] for x in toc or []}
        for col,sections in enumerate(index_columns(spec)):
            x=LEFT+col*(colw+26);y=H-139
            for section in sections:
                c.setFillColor(HexColor(PALETTE['heading']));c.setFont('Bold',10);c.drawString(x,y,section['name']);y-=20
                for u in section['units']:
                    label=u.get('index_title',u['title']);size=8.4
                    while pdfmetrics.stringWidth(label,'Sans',size)>colw-48 and size>7.5:size-=.1
                    if pdfmetrics.stringWidth(label,'Sans',size)>colw-48:raise ValueError('Shorten index title '+label)
                    c.setFillColor(HexColor(PALETTE['link']));c.setFont('Sans',7.6);c.drawString(x,y,u['id']);c.setFont('Sans',size);c.drawString(x+29,y,label)
                    page_text=str(lookup.get(u['id'],0));c.setFont('Sans',8);c.drawRightString(x+colw,y,page_text)
                    c.setStrokeColor(HexColor(PALETTE['link']));c.setLineWidth(.35)
                    for left,right in [(x,x+pdfmetrics.stringWidth(u['id'],'Sans',7.6)),(x+29,x+29+pdfmetrics.stringWidth(label,'Sans',size)),(x+colw-pdfmetrics.stringWidth(page_text,'Sans',8),x+colw)]:c.line(left,y-1.6,right,y-1.6)
                    c.linkRect('',u['id'],(x,y-3,x+colw,y+9),relative=0,thickness=0);y-=12.7
                y-=12
            if y<95:raise ValueError('Index needs more space: use concise topic entries or extend index pagination; keep necessary content')
        c.setFillColor(HexColor(PALETTE['muted']));c.setFont('Sans',8);c.drawString(LEFT,72,spec.get('route','Read the learning modules, then work through the bank. Use Index to return.'));c.drawString(LEFT,60,spec.get('estimate_basis','Approximate time to read and follow the worked steps.' if spec['estimated_minutes'] else ''))
    y=None
    for u in units_from(spec):
        y=newpage(u)
        i=0;protected_until=-1
        while i<len(u['blocks']):
            b=u['blocks'][i];width=CW;end=i+1;boxed=b.get('box')
            if boxed:
                while end<len(u['blocks']) and u['blocks'][end].get('box')==boxed:end+=1
                width,group_height=box_geometry(u['blocks'][i:end])
                needed=group_height+12
                boxed_follow_end=-1
                last=u['blocks'][end-1]
                if end<len(u['blocks']) and last['kind'] in ('p','hint','secondary') and len(last['text'])<220 and last['text'].rstrip().endswith(':'):
                    follow_height,boxed_follow_end=flow_height(u['blocks'],end,True)
                    needed+=follow_height
                if end==len(u['blocks'])-1 and u['blocks'][end]['kind'] in ('p','hint','secondary') and len(u['blocks'][end]['text'])<220:
                    needed+=getblock(u['blocks'][end])[1]
                if y-needed<BOTTOM:y=newpage(u,True)
                if boxed_follow_end>=end:protected_until=max(protected_until,boxed_follow_end)
                if y-group_height-12<BOTTOM:raise ValueError('Oversized box '+boxed)
                y-=6;x=(W-width)/2
                c.saveState();c.setStrokeColor(HexColor(PALETTE['border']));c.setLineWidth(.6);c.rect(x-6,y-group_height+4,width+12,group_height+2,fill=0,stroke=1);c.restoreState()
                rectangles.append({'page':number,'box':boxed,'unit':u['id'],'left':x-6,'width':width+12,'top':y+6,'bottom':y-group_height+4})
            else:x=LEFT
            for index in range(i,end):
                block=u['blocks'][index];o,height,typ,scale=getblock(block,width)
                keep=block.get('keep_next',False) or block['kind'] in ('question','solution_label','example_label') or (block['kind'] in ('p','hint','secondary') and len(block['text'])<220 and block['text'].rstrip().endswith(':'))
                if index==len(u['blocks'])-2 and u['blocks'][index+1]['kind'] in ('p','hint','secondary') and len(u['blocks'][index+1]['text'])<220:keep=True
                if not boxed and keep and index+1<len(u['blocks']) and index>protected_until:
                    needed,group_end=flow_height(u['blocks'],index,True)
                    if y-needed<BOTTOM:y=newpage(u,True)
                    # The opening has already reserved its data and initial
                    # working. A later lookahead must not split that group.
                    has_solution=any(v['kind']=='solution_label' for v in u['blocks'][index:group_end+1])
                    if not has_solution:
                        next_opening=next((k for k in range(index+1,group_end+1) if u['blocks'][k]['kind'] in ('example_label','question')),group_end+1)
                        group_end=min(group_end,next_opening-1)
                    short_intro=block['kind'] in ('p','hint','secondary') and len(block['text'])<220 and block['text'].rstrip().endswith(':')
                    if block['kind'] in ('example_label','question','solution_label') or short_intro:
                        protected_until=group_end
                if y-height<BOTTOM:y=newpage(u,True)
                if y-height<BOTTOM:raise ValueError('Oversized block '+str(block))
                if typ=='paragraph':
                    _,oh=o.wrap(width,10000);before=8 if block['kind'] in ('solution_label','example_label') else 0;o.drawOn(c,x,y-oh-before)
                elif typ=='image':o.drawOn(c,x+(width-o.drawWidth)/2,y-o.drawHeight)
                elif typ=='vector':
                    c.saveState();c.translate((W-o.width*scale)/2,y-o.height*scale);c.scale(scale,scale);renderPDF.draw(o,c,0,0);c.restoreState()
                if record:metrics.append({'page':number,'unit':u['id'],'kind':block['kind'],'block_index':index,'source_id':block.get('source_id'),'part':block.get('part'),'box':block.get('box'),'top':y,'bottom':y-height,'scale':scale,'left':x,'width':width})
                y-=height
            if boxed:y-=7
            i=end
    endpage();c.save();return number,positions,metrics,rectangles
def main():
    global BASE,CACHE
    ap=argparse.ArgumentParser();ap.add_argument('input',type=Path);ap.add_argument('--output',required=True,type=Path);ap.add_argument('--work-dir',required=True,type=Path);args=ap.parse_args()
    BASE=args.input.resolve().parent;CACHE=args.work_dir/'equations';CACHE.mkdir(parents=True,exist_ok=True);args.output.parent.mkdir(parents=True,exist_ok=True)
    spec=json.loads(args.input.read_text(encoding='utf-8-sig'))
    if spec.get('mode','full') not in ('full','cram'):raise ValueError('Mode must be full or cram')
    for u in units_from(spec):
        for b in u['blocks']:getblock(b)
    count,positions,_,_=build(spec,args.output)
    count,positions,metrics,boxes=build(spec,args.output,count,positions,True)
    (args.work_dir/'layout.json').write_text(json.dumps({'pdf':str(args.output.resolve()),'pages':count,'mode':spec.get('mode','full'),'estimated_minutes':spec['estimated_minutes'],'units':positions,'blocks':metrics},indent=2),encoding='utf8')
    (args.work_dir/'boxes.json').write_text(json.dumps(boxes,indent=2),encoding='utf8')
    (args.work_dir/'palette.json').write_text(json.dumps(PALETTE,indent=2),encoding='utf8')
    print(f'{args.output}: {count} pages, {len(positions)} units, {len(boxes)} fitted boxes')
if __name__=='__main__':main()
