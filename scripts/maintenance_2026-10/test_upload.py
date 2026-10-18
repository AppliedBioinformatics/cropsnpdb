import sys, io, os, tempfile, smtplib, time
sys.path.insert(0,"/var/www/html/cropsnpdb/snpdb/app")
from app import app
import notify
sent=[]
class FakeSMTP:
    def __init__(s,*a,**k): pass
    def starttls(s,**k): pass
    def login(s,u,p): pass
    def send_message(s,m): sent.append(m)
    def quit(s): pass
smtplib.SMTP=FakeSMTP
cfg=tempfile.NamedTemporaryFile("w",suffix=".cfg",delete=False); cfg.write("[smtp]\nhost=x\nport=587\nfrom=a@b.c\nto=d@e.f\n"); cfg.close()
up=tempfile.mkdtemp(prefix="up.load.")
app.config["UPLOAD_FOLDER"]=up
c=app.test_client()
def post():
    d={"Email":"test@uwa.edu.au","SNPArray":"Brassica60k","SNPFile":(io.BytesIO(b"a,b\n"),"my.snps.v1.5.csv"),"CultivarFile":(io.BytesIO(b"a,b\n"),"cult.csv")}
    return c.post("/submit",data=d,content_type="multipart/form-data")
notify.CFG="/nonexistent"; r=post(); print("no cfg:",r.status_code,"sent",len(sent))
notify.CFG=cfg.name; r=post(); time.sleep(1)
print("with cfg:",r.status_code,"sent",len(sent)); print(sent[0]["Subject"]); print(sent[0].get_content())
for root,d,f in os.walk(up):
    if f: print(sorted(f))
for u in ["/home","/search","/lines","/submit"]: print(u, c.get(u).status_code)
