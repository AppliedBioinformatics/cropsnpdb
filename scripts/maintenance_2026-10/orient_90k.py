"""Orient CropSNPdb wheat 90K SNPs against IWGSC RefSeq v1.0 (local Ensembl Plants FASTA) and derive REF/ALT.
Output: wheat90k_reference_alleles.tsv"""
import csv, glob, json, re, time, urllib.request, collections, sys
csv.field_size_limit(10**9)
D='/var/www/html/cropsnpdb/snpdb/app/data'; OUT=sys.argv[1]
COMP=str.maketrans('ACGTRYKMSWNacgt','TGCAYRMKSWNtgca'); rc=lambda s:s.translate(COMP)[::-1]
IUPAC={'A':'A','C':'C','G':'G','T':'T','R':'AG','Y':'CT','K':'GT','M':'AC','S':'CG','W':'AT','N':'ACGT'}
def sim(a,b):
    n=min(len(a),len(b)); return sum(1 for x,y in zip(a[:n],b[:n]) if y in IUPAC.get(x,x) or x in IUPAC.get(y,y))/max(n,1)
snps=[]
for f in sorted(glob.glob(D+'/Triticum_aestivum_RefSeq_v1_and_Pan_*.csv')):
    r=csv.reader(open(f)); h=next(r); i=h.index('Probe_Sequence')
    for row in r:
        g=[x for x in row[i+1:] if x not in ('NC','?','')]
        snps.append(dict(id=row[0],chr=row[3],pos=int(row[6]),probe=row[i],calls=set(''.join(g))))
regions=[s for s in snps if re.fullmatch(r'chr[1-7][ABD]',s['chr'])]
print('SNPs',len(snps),'on chr1A-7D',len(regions),flush=True)
seqs={}
import pysam
fa=pysam.FastaFile('/data/cropsnpdb/refseq_v1/refseq_v1.fa')
for sn in regions:
    seqs[sn['id']]=fa.fetch(sn['chr'][3:], sn['pos']-51, sn['pos']+50).upper()   # 0-based; SNP at index 50
print('sequences',len(seqs),'of',len(regions),flush=True)
out=[]; stat=collections.Counter()
for s in snps:
    rec=dict(SNPid=s['id'],Chr=s['chr'],Pos_RefSeqv1=s['pos'],ProbeAlleles='',ProbeStrand='NA',REF='NA',ALT='NA',CallAlleles=''.join(sorted(s['calls'])),CallStrand='NA',Note='')
    m=re.match(r'([^\[]*)\[(\w)/(\w)\](.*)',s['probe'].upper()); L,a1,a2,R=m.groups(); rec['ProbeAlleles']=a1+'/'+a2
    W=seqs.get(s['id'])
    if not W: rec['Note']='not on chr1A-7D (no RefSeq v1 position)'; stat['unplaced']+=1; out.append(rec); continue
    k=30; fwd=(sim(L[-k:],W[50-k:50])+sim(R[:k],W[51:51+k]))/2; rev=(sim(rc(R[:k]),W[50-k:50])+sim(rc(L[-k:]),W[51:51+k]))/2
    if max(fwd,rev)<0.9: rec['Note']='flanks do not match reference at this position'; stat['flank mismatch']+=1; out.append(rec); continue
    strand='+' if fwd>=rev else '-'; rec['ProbeStrand']=strand
    fa={a1,a2} if strand=='+' else {a1.translate(COMP),a2.translate(COMP)}
    ref=W[50]
    if ref not in fa: rec['Note']='reference base %s not among SNP alleles'%ref; stat['ref not allele']+=1; out.append(rec); continue
    rec['REF']=ref; rec['ALT']=(fa-{ref}).pop()
    calls=s['calls']; comp={x.translate(COMP) for x in fa}
    if fa==comp: rec['CallStrand']='ambiguous'; rec['Note']='A/T or C/G SNP: call strand cannot be inferred from alleles'; stat['ambiguous']+=1
    elif calls<=fa: rec['CallStrand']='+'; stat['calls +']+=1
    elif calls<=comp: rec['CallStrand']='-'; stat['calls -']+=1
    else: rec['Note']='call alleles do not match SNP alleles'; stat['call mismatch']+=1
    out.append(rec)
w=csv.DictWriter(open(OUT,'w',newline=''),fieldnames=list(out[0].keys()),delimiter='\t'); w.writeheader(); w.writerows(out)
print(stat)
