"""Build bgzipped, CSI-indexed MorexV3 VCFs for CropSNPdb barley datasets.
ozbarley: OzBarley Wheat Barley 40K chip markers (AVRIG IDs) for 499 landraces (SNPchip xlsx) + 214 elite lines
          (HapMap; chip markers matched by MorexV3 position; chip calls partly Beagle-imputed by the authors).
nsgc:     T3 UMN_NSGC_GWAS (748 NSGC accessions), array markers only (S#H_ position-named SNPs, chrUn and
          A/T|C/G SNPs dropped: T3 alleles are on mixed strands, so palindromic SNPs cannot be oriented).
REF is checked against MorexV3 (Ensembl Plants); calls on the other strand are complemented.
rnaseq:   OzBarley elite HapMap SNPs that are not 40K chip positions (RNA-seq SNPs, 214 elite lines), with SnpEff
          gene/effect/impact from snp_descriptions.csv in INFO.
Usage: build_barley_vcfs.py ozbarley|nsgc|rnaseq"""
import sys, csv, gzip, re, collections, pysam
B='/data/cropsnpdb/barley'; fa=pysam.FastaFile(f'{B}/morexv3/morexv3.fa')
CH=[f'chr{i}H' for i in range(1,8)]
comp=str.maketrans('ACGT','TGCA')
IUPAC={'A':'AA','C':'CC','G':'GG','T':'TT','R':'AG','Y':'CT','S':'CG','W':'AT','K':'GT','M':'AC'}
st=collections.Counter()

def header(samples, src):
    h=['##fileformat=VCFv4.2', f'##source={src}', '##reference=MorexV3 (Ensembl Plants Hordeum_vulgare.MorexV3_pseudomolecules_assembly)',
       '##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">']
    h+=[f'##contig=<ID=Chr{c[3:]},length={fa.get_reference_length(c)}>' for c in CH]
    h.append('#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t'+'\t'.join(samples))
    return '\n'.join(h)+'\n'

def orient(ref, alleles):
    """Return (flip, alts) or None: alleles observed in calls vs MorexV3 ref base."""
    a=set(alleles)
    if ref in a: return False, sorted(a-{ref})
    c={x.translate(comp) for x in a}
    if ref in c and not (a & c and len(a)>1 and a==c): return True, sorted(c-{ref})
    return None

def gt(pair, ref, alts, flip):
    if pair is None: return './.'
    p=pair.translate(comp) if flip else pair
    al=[ref]+alts
    try: return '/'.join(sorted(str(al.index(b)) for b in p))
    except ValueError: st['call allele not in REF/ALT -> missing']+=1; return './.'

def write(out, recs, samples, src, info=None):
    recs.sort(key=lambda r:(CH.index(r[0]), r[1]))
    tmp=out[:-3]
    with open(tmp,'w') as fh:
        hd=header(samples, src)
        if info: hd=hd.replace('##FORMAT', info+'\n##FORMAT',1)
        fh.write(hd)
        for r in recs:
            c,p,i,ref,alts,gts=r[:6]; inf=r[6] if len(r)>6 else '.'
            fh.write(f'Chr{c[3:]}\t{p}\t{i}\t{ref}\t{",".join(alts) or "."}\t.\tPASS\t{inf}\tGT\t'+'\t'.join(gts)+'\n')
    pysam.tabix_index(tmp, preset='vcf', csi=True, force=True)
    print('wrote', out, len(recs), 'markers', len(samples), 'samples')

def ozbarley():
    D=f'{B}/ozbarley'
    rows=list(csv.reader(open(f'{D}/landrace_chip.tsv'),delimiter='\t'))
    names,chrs,poss=rows[0][1:],rows[1][1:],rows[2][1:]
    lr=[r[0] for r in rows[3:]]; lg=[r[1:] for r in rows[3:]]
    el=None; ep={}
    for l in open(f'{D}/2025_RNASeqSNP_and_GenoData.hapmap.txt'):
        f=l.rstrip('\n').split('\t')
        if f[0]=='rs': el=f[11:]; continue
        ep[(f'chr{f[2]}', int(f[3]))]=f[11:]
    code=lambda s: '_'.join(s.split('_')[:2])
    # replicate DNA samples of one OzBarley line: keep the first (4 landrace replicates dropped)
    seen=set(); keepL=[]; keepE=[]
    for i,s in enumerate(lr):
        if code(s) in seen: st['replicate sample dropped']+=1; continue
        seen.add(code(s)); keepL.append(i)
    for i,s in enumerate(el):
        if code(s) in seen: st['replicate sample dropped']+=1; continue
        seen.add(code(s)); keepE.append(i)
    lr=[lr[i] for i in keepL]; lg=[lg[i] for i in keepL]
    samples=[code(s) for s in lr]+[code(el[i]) for i in keepE]
    with open(f'{D}/ozbarley_samples.tsv','w') as fh:
        for s in lr: fh.write(f"{code(s)}\t{re.sub(r' [(]DNA[^)]*[)]$','',s.split('_',2)[2])}\tlandrace\n")
        for i in keepE: fh.write(f"{code(el[i])}\t{el[i].split('_',2)[2]}\telite\n")
    recs=[]
    for j,(n,c,p) in enumerate(zip(names,chrs,poss)):
        if c not in CH or not p.isdigit(): st['unplaced']+=1; continue
        p=int(p); ref=fa.fetch(c,p-1,p).upper()
        lcalls=[(g[j].replace('/','') if len(g[j].replace('/',''))==2 else g[j]*2) if g[j] else None for g in lg]
        ecalls=[IUPAC.get(ep[(c,p)][i]) for i in keepE] if (c,p) in ep else [None]*len(keepE)
        st['elite present' if (c,p) in ep else 'elite absent']+=1
        la={b for x in lcalls if x for b in x}; ea={b for x in ecalls if x for b in x}
        ol=orient(ref, la) if la else (False, [])
        oe=orient(ref, ea) if ea else (False, [])
        if ol is None or oe is None: st['REF not among alleles -> dropped']+=1; continue
        if ol[0]: st['landrace calls complemented']+=1
        if oe[0]: st['elite calls complemented']+=1
        alts=sorted(set(ol[1])|set(oe[1]))
        if len(alts)>1: st['multiallelic']+=1
        gts=[gt(x,ref,alts,ol[0]) for x in lcalls]+[gt(x,ref,alts,oe[0]) for x in ecalls]
        recs.append((c,p,n,ref,alts,gts))
    write(f'{D}/ozbarley_40k_morexv3.vcf.gz', recs, samples, 'OzBarley Figshare doi:10.25909/29104916 (landrace SNPchip xlsx + elite HapMap chip positions)')

def nsgc():
    D=f'{B}/t3'; recs=[]; samples=None
    for l in gzip.open(f'{D}/UMN_NSGC_GWAS.vcf.gz','rt'):
        if l.startswith('##'): continue
        f=l.rstrip('\n').split('\t')
        if l.startswith('#'): samples=f[9:]; continue
        c='chr'+f[0]
        if c not in CH: st['chrUn dropped']+=1; continue
        if re.match(r'^S[1-7]H_',f[2]): st['non-array S#H_ SNP dropped']+=1; continue
        p=int(f[1]); ref=fa.fetch(c,p-1,p).upper(); al=[f[3]]+f[4].split(',')
        calls=[None if g[0]=='.' else ''.join(al[int(x)] for x in re.split('[/|]',g)) for g in f[9:]]
        if set(al) in ({'A','T'},{'C','G'}): st['A/T or C/G SNP (strand unknown) dropped']+=1; continue
        o=orient(ref, set(al))
        if o is None: st['REF not among alleles -> dropped']+=1; continue
        st['REF ok' if f[3]==ref else ('alleles swapped' if not o[0] else 'complemented')]+=1
        recs.append((c,p,f[2],ref,o[1],[gt(x,ref,o[1],o[0]) for x in calls]))
    write(f'{D}/nsgc_50k_morexv3.vcf.gz', recs, samples, 'T3 Barley UMN_NSGC_GWAS (files.triticeaetoolbox.org/download/barley/UMN_NSGC_GWAS.vcf.gz)')

def rnaseq():
    D=f'{B}/ozbarley'
    chip={(c,int(p)) for c,p in zip(*list(csv.reader(open(f'{D}/landrace_chip.tsv'),delimiter='\t'))[1:3]) if p.isdigit()}
    ann={}
    for r in csv.DictReader(open(f'{D}/snp_descriptions.csv')):
        e=r['Effect'].replace('&','+'); g=r['Gene-ID']
        if r['CHR'] and r['POS_CHR']: ann[('chr'+r['CHR'],int(r['POS_CHR']))]=f"GENE={g};EFFECT={e};IMPACT={r['Impact']}" if g else '.'
    el=None; recs=[]
    for l in open(f'{D}/2025_RNASeqSNP_and_GenoData.hapmap.txt'):
        f=l.rstrip('\n').split('\t')
        if f[0]=='rs': el=f[11:]; samples=['_'.join(x.split('_')[:2]) for x in el]; continue
        c='chr'+f[2]; p=int(f[3])
        if (c,p) in chip: st['40K chip position (already in OzBarley 40K) skipped']+=1; continue
        ref=fa.fetch(c,p-1,p).upper(); calls=[IUPAC.get(x) for x in f[11:]]
        a={b for x in calls if x for b in x}
        if not a: st['no calls']+=1; continue
        o=orient(ref,a)
        if o is None or o[0]: st['REF not among alleles -> dropped']+=1; continue
        if len(o[1])>1: st['multiallelic']+=1
        if not o[1]: st['monomorphic REF']+=1
        recs.append((c,p,f[0],ref,o[1],[gt(x,ref,o[1],False) for x in calls],ann.get((c,p),'.')))
        st['annotated' if ann.get((c,p),'.')!='.' else 'no annotation']+=1
    assert len(set(samples))==len(samples)
    write(f'{D}/ozbarley_rnaseq_morexv3.vcf.gz', recs, samples, 'OzBarley elite RNA-seq SNPs (Figshare doi:10.25909/29104916 HapMap; SnpEff from snp_descriptions.csv)',
          info='##INFO=<ID=GENE,Number=1,Type=String,Description="MorexV3 gene (SnpEff)">\n##INFO=<ID=EFFECT,Number=1,Type=String,Description="SnpEff effect">\n##INFO=<ID=IMPACT,Number=1,Type=String,Description="SnpEff impact">')

{'ozbarley':ozbarley,'nsgc':nsgc,'rnaseq':rnaseq}[sys.argv[1]]()
print(dict(st))
