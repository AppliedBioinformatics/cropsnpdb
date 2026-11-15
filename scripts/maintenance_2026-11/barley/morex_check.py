import pysam, collections, sys
for vcf in ['/data/cropsnpdb/barley/t3/nsgc_50k_morexv3.vcf.gz','/data/cropsnpdb/barley/ozbarley/ozbarley_40k_morexv3.vcf.gz']:
    v=pysam.VariantFile(vcf); names={}
    try:
        names={l.split('\t')[0]:l.split('\t')[1] for l in open('/data/cropsnpdb/barley/ozbarley/ozbarley_samples.tsv')}
    except: pass
    ms=[s for s in v.header.samples if 'MOREX' in (s+names.get(s,'')).upper()]
    print(vcf.split('/')[-1], ms, [names.get(s) for s in ms])
    for s in ms:
        c=collections.Counter()
        for r in v.fetch():
            g=r.samples[s]['GT']
            c['missing' if None in g else ('homREF' if g==(0,0) else ('het' if g[0]!=g[1] else 'homALT'))]+=1
        print(s,dict(c))
