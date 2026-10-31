# Place wheat 90K SNPs on IWGSC RefSeq v2.1: v1.0 flanks (+-50 bp) mapped per chromosome with minimap2.
import sys, subprocess, re, collections, pymysql, pysam
sys.path.insert(0,'/var/www/html/cropsnpdb/snpdb/app'); import config
W='/data/cropsnpdb/wheat90k'
v1=pysam.FastaFile('/data/cropsnpdb/refseq_v1/refseq_v1.fa')
v21=pysam.FastaFile('/data/cropsnpdb/refseq_v21/refseq_v21.fa')
comp=str.maketrans('ACGTN','TGCAN')
c=pymysql.connect(host=config.MYSQL_DATABASE_HOST,user=config.MYSQL_DATABASE_USER,password=config.MYSQL_DATABASE_PASSWORD,db=config.MYSQL_DATABASE_DB)
cur=c.cursor()
cur.execute("""SELECT s.SNPid, sc.Chromosome, sc.Coordinate FROM SNP s JOIN SNP_Coordinates sc ON sc.SNP_SNPid=s.SNPid
 WHERE s.SNPArray_idSNPArray=2 AND sc.Specie_Build='RSv1' AND sc.Chromosome REGEXP '^chr[1-7][ABD]$'""")
bychr=collections.defaultdict(list)
for sid,ch,pos in cur.fetchall(): bychr[ch[3:]].append((sid,pos))
stat=collections.Counter(); out=open(f'{W}/wheat90k_v21_positions.tsv','w')
out.write('SNPid\tChr_v1\tPos_v1\tChr_v21\tPos_v21\tStrand_v1_to_v21\tMAPQ\tRefBase_v1\n')
for ch in sorted(bychr):
    q=f'{W}/q_{ch}.fa'; n=0
    with open(q,'w') as fh:
        for sid,pos in bychr[ch]:
            s=v1.fetch(ch,pos-51,pos+50).upper()
            if len(s)==101: fh.write(f'>{sid}|{pos}|{s[50]}\n{s}\n'); n+=1
    ref=f'{W}/v21_{ch}.fa'
    with open(ref,'w') as fh: fh.write(f'>{ch}\n{v21.fetch(ch)}\n')
    paf=subprocess.run(['minimap2','-x','sr','-c','-t','3','--secondary=no',ref,q],capture_output=True,text=True).stdout
    best={}
    for l in paf.splitlines():
        f=l.split('\t'); qn=f[0]
        if qn in best: stat['multi']+=1; continue
        best[qn]=f
    for qn,f in best.items():
        sid,pos,rb=qn.split('|'); ql,qs,qe,st,ts,mq=int(f[1]),int(f[2]),int(f[3]),f[4],int(f[7]),int(f[11])
        cg=[t for t in f[12:] if t.startswith('cg:Z:')][0][5:]
        if mq<20 or qe-qs<90: stat['low quality']+=1; continue
        qq= qs if st=='+' else ql-qe; tt=ts; hit=None
        for L,op in re.findall(r'(\d+)([MIDN])',cg):
            L=int(L)
            if op=='M':
                if qq<=50<qq+L: hit=tt+(50-qq); break
                qq+=L; tt+=L
            elif op=='I':
                if qq<=50<qq+L: break
                qq+=L
            else: tt+=L
        if hit is None: stat['SNP in indel/unaligned']+=1; continue
        b=v21.fetch(ch,hit,hit+1).upper()
        if st=='-': b=b.translate(comp)
        if b!=rb: stat['ref base differs']+=1; continue
        out.write(f'{sid}\tchr{ch}\t{pos}\tchr{ch}\t{hit+1}\t{st}\t{mq}\t{rb}\n'); stat['placed']+=1
    stat['unmapped']+=n-len(best)
    print(ch,n,dict(stat),flush=True)
    import os; os.remove(ref); os.remove(q)
print('DONE',dict(stat))
