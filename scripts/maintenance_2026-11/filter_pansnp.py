"""Filter the B. napus pangenome SNP VCF (BnaPan.SNPs.vcf.gz, brassicagenome.net) for CropSNPdb.
The source FORMAT is GT:PL but some genotypes carry extra fields and the header defines no GT, so it is parsed
directly: placed chromosomes only (renamed A01..C09), biallelic SNPs, QUAL >= 30, GT only, <= 20% missing, MAF >= 0.05.
Usage: python filter_pansnp.py BnaPan.SNPs.vcf.gz out.vcf"""
import gzip, re, sys

src, out = sys.argv[1:3]
CHR = re.compile(r"^chr([AC]\d\d)_contigs_placed_v81$")
n_in = n_out = 0
with gzip.open(src, "rt") as f, open(out, "w") as o:
    for line in f:
        if line.startswith("##"):
            continue
        if line.startswith("#CHROM"):
            samples = line.rstrip("\n").split("\t")[9:]
            o.write("##fileformat=VCFv4.2\n")
            for c in [f"{g}{i:02d}" for g in "AC" for i in range(1, 11) if not (g == "C" and i == 10)]:
                o.write(f"##contig=<ID={c}>\n")
            o.write('##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">\n')
            o.write("##source=BnaPan.SNPs.vcf.gz (Hurgobin et al. 2018 doi:10.1111/pbi.12867), filtered: biallelic SNPs, "
                    "QUAL>=30, missing<=20%, MAF>=0.05, placed chromosomes\n")
            o.write("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t" + "\t".join(samples) + "\n")
            continue
        n_in += 1
        c = line.split("\t", 9)
        m = CHR.match(c[0])
        if not m or len(c[3]) != 1 or len(c[4]) != 1 or c[4] == "." or c[5] == "." or float(c[5]) < 30:
            continue
        gts = [g.split(":", 1)[0] for g in c[9].rstrip("\n").split("\t")]
        called = [g for g in gts if g in ("0/0", "0/1", "1/1", "0|0", "0|1", "1|0", "1|1")]
        if len(called) < 0.8 * len(gts):
            continue
        alt = sum(g.count("1") for g in called)
        af = alt / (2 * len(called))
        if min(af, 1 - af) < 0.05:
            continue
        chrom = m.group(1)
        o.write(f"{chrom}\t{c[1]}\t{chrom}_{c[1]}\t{c[3]}\t{c[4]}\t{c[5]}\tPASS\t.\tGT\t"
                + "\t".join(g if g in called else "./." for g in gts) + "\n")
        n_out += 1
print(f"records {n_in}, kept {n_out}", flush=True)
