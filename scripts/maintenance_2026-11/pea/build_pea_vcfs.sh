#!/bin/bash
# Pea VCFs (LIS datastore, Cameor v2) -> CropSNPdb: biallelic SNPs on chr1-chr7, GT only, contigs Chr1..Chr7.
# psppc: USDA Pea Single Plant Plus Collection GBS (Powers et al. 2021 G3; Beagle-imputed), samples renamed SRR -> ENA sample alias.
# ams:   Aubert et al. 2023 AMS panel recalled on Cameor v2 (Kreplak et al. 2026): FILTER PASS, <=20% missing, MAF>=0.05.
set -e
cd /data/cropsnpdb/pea
for i in 1 2 3 4 5 6 7; do echo -e "pissa.Cameor.gnm2.chr$i\tChr$i"; done > chrmap.txt
T=$(for i in 1 2 3 4 5 6 7; do printf "pissa.Cameor.gnm2.chr$i,"; done | sed 's/,$//')
clean_hdr() { bcftools view -h $1 | grep -v "^##contig=<ID=pissa" > hdr.txt; bcftools reheader -h hdr.txt -o tmp.vcf.gz $1 && mv tmp.vcf.gz $1 && bcftools index -f --csi $1; }
if [ "$1" = psppc ]; then
  awk -F'\t' 'NR>1{print $1"\t"$3}' psppc_runs.tsv > psppc_rename.txt
  bcftools view -r "$T" -m2 -M2 -v snps pissa.Cameor.gnm2.div.Powers_Boatwright_2021.vcf.gz -Ou \
   | bcftools annotate -x INFO,^FORMAT/GT --rename-chrs chrmap.txt -Ou \
   | bcftools annotate --set-id 'PSPPC_%CHROM\_%POS' -Ou \
   | bcftools reheader -s psppc_rename.txt | bcftools view -Oz -o pea_psppc_cameor2_snps.vcf.gz
  bcftools index --csi pea_psppc_cameor2_snps.vcf.gz; clean_hdr pea_psppc_cameor2_snps.vcf.gz
  echo "PSPPC SNPs: $(bcftools index -n pea_psppc_cameor2_snps.vcf.gz)"
fi
if [ "$1" = ams ]; then
  bcftools view -r "$T" -f PASS,. -m2 -M2 -v snps pissa.Cameor.gnm2.div.Kreplak_Novak_2026.vcf.gz -Ou \
   | bcftools view -i 'F_MISSING<=0.2 && MAF>=0.05' -Ou \
   | bcftools annotate -x INFO,^FORMAT/GT --rename-chrs chrmap.txt -Ou \
   | bcftools annotate --set-id 'PsAMS_%CHROM\_%POS' -Oz -o pea_ams_cameor2_snps.vcf.gz
  bcftools index --csi pea_ams_cameor2_snps.vcf.gz; clean_hdr pea_ams_cameor2_snps.vcf.gz
  echo "AMS SNPs: $(bcftools index -n pea_ams_cameor2_snps.vcf.gz)"
fi
echo ALL DONE
