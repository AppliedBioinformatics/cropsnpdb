# CAIGE 40K wheat genotypes (2026-11)

Source: CSIRO Data Access Portal csiro:65245, doi:10.25919/3x88-4p26 (CC BY 4.0); Fradgley et al. 2025 TAG 138:241.
Files in /data/cropsnpdb/caige/.

1. `python3 xlsx2tsv.py Sample_details.xlsx sample_details.tsv`
2. `venv/bin/python build_vcf.py`: IWGSC v2.0 calls -> caige_40k_v2.1.vcf.gz on the AGG RefSeq v2.1 marker set
   (17,755 shared markers, AGG positions and REF/ALT; Replicate 2 samples dropped; 376 lines).
3. `venv/bin/python load_caige_meta.py dryrun|commit`: Reference 7, Cultivar `CAIGE <nursery>-<entry> (GID <gid>)`,
   Accession `CAIGE GID <gid>`, AccessionMetadata (selection history, breeding programme from its prefix),
   AccessionVcfSample -> CAIGE VCF. Species 6 (Triticum aestivum RefSeq v2.1).

## B. napus pangenome WGS SNPs (2026-11-12)
- filter_pansnp.py: brassicagenome.net BnaPan.SNPs.vcf.gz -> biallelic SNPs, QUAL>=30, GT only, <=20% missing, MAF>=0.05, placed chromosomes A01..C09 (1,358,868 SNPs, 53 lines). Run on wheatis-01.
- load_bnapus_pangenome.py dryrun|commit: registers species "Brassica napus pangenome v81" (Build v81pan, array BnapusPangenomeWGS, Hurgobin et al. 2018 doi:10.1111/pbi.12867) as VCF-backed; VCF at /data/cropsnpdb/bnapus_pangenome/.
- app/ownLib/vcfBackend.py VCF_SPECIES and app/genoapi.py ALIASES (bnapus_pangenome) updated.
- 2026-11-12: VCF IDs rewritten to BnaPan_<chrom>_<pos> to match SNP.SNPid (original in /data/cropsnpdb/bnapus_pangenome/orig/).
