#!/bin/bash
# von Wettberg & Chang 2018 Cicer WGS VCF (LIS datastore, CDC Frontier v1) -> CropSNPdb VCF:
# FILTER PASS, biallelic SNPs on Ca1-Ca8, <=20% missing, MAF>=0.05, GT only, IDs CaFr1_<chr>_<pos>.
set -e
cd /data/cropsnpdb/chickpea/vonwettberg
IN=cicar.CDCFrontier.div.vonWettberg_Chang_2018.vcf.gz
for i in 1 2 3 4 5 6 7 8; do echo -e "cicar.CDCFrontier.gnm1.Ca$i\tCa$i"; done > chrmap.txt
T=$(for i in 1 2 3 4 5 6 7 8; do printf "cicar.CDCFrontier.gnm1.Ca$i,"; done | sed 's/,$//')
bcftools view -t "$T" -f PASS,. -m2 -M2 -v snps $IN -Ou \
 | bcftools view -i 'F_MISSING<=0.2 && MAF>=0.05' -Ou \
 | bcftools annotate -x INFO,^FORMAT/GT --rename-chrs chrmap.txt -Ou \
 | bcftools annotate --set-id 'CaFr1_%CHROM\_%POS' -Oz -o cicer_wgs_cdcfrontier1_snps.vcf.gz
bcftools index --csi cicer_wgs_cdcfrontier1_snps.vcf.gz
bcftools view -h cicer_wgs_cdcfrontier1_snps.vcf.gz | grep -v "^##contig=<ID=cicar" > hdr.txt
bcftools reheader -h hdr.txt -o tmp.vcf.gz cicer_wgs_cdcfrontier1_snps.vcf.gz && mv tmp.vcf.gz cicer_wgs_cdcfrontier1_snps.vcf.gz && bcftools index -f --csi cicer_wgs_cdcfrontier1_snps.vcf.gz
echo "SNPs: $(bcftools index -n cicer_wgs_cdcfrontier1_snps.vcf.gz)"
echo ALL DONE
