import pysam, re, collections
oz=pysam.VariantFile('/data/cropsnpdb/barley/ozbarley/ozbarley_40k_morexv3.vcf.gz')
ns=pysam.VariantFile('/data/cropsnpdb/barley/t3/nsgc_50k_morexv3.vcf.gz')
names={l.split('\t')[0]:l.split('\t')[1] for l in open('/data/cropsnpdb/barley/ozbarley/ozbarley_samples.tsv')}
norm=lambda s: re.sub(r'[^a-z0-9]','',s.lower())
nsn=collections.defaultdict(list)
for s in ns.header.samples:
    for part in s.split('|'): nsn[norm(part)].append(s)
pairs=[(o,nsn[norm(names[o])][0]) for o in oz.header.samples if norm(names[o]) in nsn and len(norm(names[o]))>3]
print('shared line names',len(pairs),pairs[:12])
npos={(r.chrom,r.pos):r for r in ns.fetch()}
m=collections.Counter(); shared=0; per=collections.defaultdict(collections.Counter)
for r in oz.fetch():
    n=npos.get((r.chrom,r.pos))
    if not n: continue
    shared+=1
    for o,s in pairs:
        a=r.samples[o]['GT']; b=n.samples[s]['GT']
        if None in a or None in b: continue
        ga=sorted(r.alleles[i] for i in a); gb=sorted(n.alleles[i] for i in b)
        m[ga==gb]+=1; per[(o,s)][ga==gb]+=1
print('shared positions',shared,'concordance',dict(m), round(m[True]/max(1,sum(m.values())),4))
print(sorted(((round(c[True]/max(1,sum(c.values())),3),k) for k,c in per.items()))[:10])
pm=collections.defaultdict(collections.Counter)
for r in oz.fetch():
    n=npos.get((r.chrom,r.pos))
    if not n: continue
    for o,s in pairs:
        a=r.samples[o]['GT']; b=n.samples[s]['GT']
        if None in a or None in b: continue
        pm[r.id][sorted(r.alleles[i] for i in a)==sorted(n.alleles[i] for i in b)]+=1
fr=[c[True]/sum(c.values()) for c in pm.values() if sum(c.values())>=8]
print('markers',len(fr),'hist', collections.Counter(round(x,1) for x in fr))
# same alleles at shared positions?
d=collections.Counter()
for r in oz.fetch():
    n=npos.get((r.chrom,r.pos))
    if n: d[(r.ref==n.ref, set(r.alts or ())==set(n.alts or ()))]+=1
print('REF same / ALT same',d)
import gzip
fa=pysam.FastaFile('/data/cropsnpdb/barley/morexv3/morexv3.fa'); comp=str.maketrans('ACGT','TGCA')
orig={}
for l in gzip.open('/data/cropsnpdb/barley/t3/UMN_NSGC_GWAS.vcf.gz','rt'):
    if l[0]=='#': continue
    f=l.split('\t',6); orig[f[2]]=(f[0],f[1],f[3],f[4])
cat=collections.Counter()
for r in oz.fetch():
    n=npos.get((r.chrom,r.pos))
    if not n or r.id not in pm or sum(pm[r.id].values())<8: continue
    c,p,R,A=orig[n.id]; ref=fa.fetch('chr'+c,int(p)-1,int(p)).upper()
    k='REF ok' if R==ref else ('swapped' if A==ref else 'complemented')
    low=pm[r.id][True]/sum(pm[r.id].values())<0.5
    cat[(k,'LOW' if low else 'ok')]+=1
print(sorted(cat.items()))
lowm={k for k,c in pm.items() if sum(c.values())>=8 and c[True]/sum(c.values())<0.5}
pt=collections.Counter()
for r in oz.fetch():
    if r.id not in lowm: continue
    n=npos[(r.chrom,r.pos)]
    for o,s in pairs:
        a=r.samples[o]['GT']; b=n.samples[s]['GT']
        if None in a or None in b: continue
        pt[(o.startswith('OzBL'), sorted(r.alleles[i] for i in a)==sorted(n.alleles[i] for i in b))]+=1
print('low markers by panel (landrace?, match)',sorted(pt.items()))
def af(r, ss=None):
    n=a=0
    for s in (ss or r.samples):
        g=r.samples[s]['GT']
        if None in g: continue
        n+=2; a+=sum(1 for x in g if x>0)
    return round(a/n,2) if n else None
k=0
for r in oz.fetch():
    if r.id not in lowm: continue
    n=npos[(r.chrom,r.pos)]
    print(r.id, n.id, r.chrom, r.pos, r.ref, r.alts, 'ozAF',af(r),'nsgcAF',af(n), 'orig', orig[n.id][2:])
    k+=1
    if k>=8: break
