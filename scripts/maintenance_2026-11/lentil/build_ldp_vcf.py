"""AGILE Lentil Diversity Panel exome-capture SNPs (KnowPulse, CDC Redberry v2.0 / Lcu.2RBY) -> CropSNPdb VCF.
Keeps biallelic SNPs on Lcu.2RBY.Chr1-7 (indels and unitigs dropped), GT only, contigs renamed Chr1..Chr7,
IDs LcRBY2_<chr>_<pos>. Source filters (KnowPulse): QUAL>=30, mean depth>=3, <=10% missing, MAF>=5%, CNV SNPs removed."""
import gzip, collections, pysam
D='/data/cropsnpdb/lentil/ldp'; SRC=f'{D}/LDP-Lc2.0-Oct8_maf05-95_x90_minSNPQ30.recode.vcf.gz'
OUT=f'{D}/ldp_exome_lcu2rby_snps.vcf'
st=collections.Counter(); keep={f'Lcu.2RBY.Chr{i}' for i in range(1,8)}; lens={}
with gzip.open(SRC,'rt') as f, open(OUT,'w') as o:
    for l in f:
        if l.startswith('##contig'):
            cid=l.split('ID=')[1].split(',')[0]
            if cid in keep: lens[cid]=l.split('length=')[1].split('>')[0]
            continue
        if l.startswith('##'): continue
        if l.startswith('#CHROM'):
            o.write('##fileformat=VCFv4.2\n##source=KnowPulse AGILE-LDP-ExomeCapture LDP-Lc2.0-Oct8_maf05-95_x90_minSNPQ30 (biallelic SNPs, Chr1-7, GT only)\n')
            o.write('##reference=Lens culinaris CDC Redberry v2.0 (Lcu.2RBY)\n##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">\n')
            for c in sorted(lens): o.write(f'##contig=<ID={c.replace("Lcu.2RBY.","")},length={lens[c]}>\n')
            o.write('\t'.join(l.rstrip('\n').split('\t')[:9]).replace('FORMAT','FORMAT')+'\t'+'\t'.join(l.rstrip('\n').split('\t')[9:])+'\n'); continue
        f9=l.split('\t',9)
        if f9[0] not in keep: st['unitig']+=1; continue
        if len(f9[3])!=1 or len(f9[4])!=1 or f9[4]=='.': st['indel/multiallelic']+=1; continue
        c=f9[0].replace('Lcu.2RBY.','')
        gts=[g.split(':',1)[0] for g in f9[9].rstrip('\n').split('\t')]
        o.write(f'{c}\t{f9[1]}\tLcRBY2_{c}_{f9[1]}\t{f9[3]}\t{f9[4]}\t{f9[5]}\tPASS\t.\tGT\t'+'\t'.join(gts)+'\n'); st['SNP']+=1
print(dict(st), flush=True)
pysam.tabix_index(OUT, preset='vcf', csi=True, force=True)
print('DONE')
