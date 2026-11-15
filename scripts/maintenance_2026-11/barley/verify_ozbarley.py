# Random spot-check: genotypes served by the live API vs the OzBarley source files.
import csv, random, json, urllib.request, ssl, collections
random.seed(7); D='/data/cropsnpdb/barley/ozbarley'
IU={'A':'AA','C':'CC','G':'GG','T':'TT','R':'AG','Y':'CT','S':'CG','W':'AT','K':'GT','M':'AC'}
rows=list(csv.reader(open(f'{D}/landrace_chip.tsv'),delimiter='\t'))
mk={n:(c,int(p)) for n,c,p in zip(rows[0][1:],rows[1][1:],rows[2][1:]) if p.isdigit() and c.startswith('chr') and c!='chrUn'}
land={r[0]:dict(zip(rows[0][1:],r[1:])) for r in rows[3:]}
el=None; ep={}
for l in open(f'{D}/2025_RNASeqSNP_and_GenoData.hapmap.txt'):
    f=l.rstrip('\n').split('\t')
    if f[0]=='rs': el=f[11:]; continue
    ep[('chr'+f[2],int(f[3]))]=dict(zip(el,f[11:]))
names={r[0]:r[1] for r in csv.reader(open(f'{D}/ozbarley_samples.tsv'),delimiter='\t')}
full={'_'.join(s.split('_')[:2]):s for s in list(land)+el}
ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
res=collections.Counter()
for code in random.sample(sorted(names),30):
    for m in random.sample(sorted(mk),40):
        c,p=mk[m]; src=full[code]
        if src in land:
            g=land[src][m]; exp=None if not g else ''.join(sorted(g.replace('/','') if '/' in g else g*2))
        else:
            g=ep.get((c,p),{}).get(src); exp=''.join(sorted(IU[g])) if g in IU else None
        u=f"https://snpdb.appliedbioinformatics.com.au/api/v1/genotypes?species=barley40k&chrom={c}&start={p}&end={p}&lines={code}"
        d=json.load(urllib.request.urlopen(u,context=ctx))
        if not d.get('markers'): res['marker not served']+=1; continue
        i=[k for k,x in enumerate(d['markers']) if x['id']==m]
        if not i: res['marker not served']+=1; continue
        got=d['accessions'][0]['genotypes'][i[0]]
        got=None if got=='NC' else ''.join(sorted(got))
        res['both missing' if exp is None and got is None else ('match' if exp==got else 'MISMATCH')]+=1
        if exp!=got and exp is not None: print('MISMATCH',code,m,exp,got)
print(dict(res))
