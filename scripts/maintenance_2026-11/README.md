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

## Barley (2026-11-15) – scripts in barley/
- get_morexv3.sh: MorexV3 chromosomes (Ensembl Plants) -> /data/cropsnpdb/barley/morexv3/morexv3.fa (contigs chr1H..chr7H).
- OzBarley (Baumann et al. 2026 Sci Data 13:703; Figshare collection doi:10.25909/c.6952545, CC BY 4.0), files in /data/cropsnpdb/barley/ozbarley/.
  build_barley_vcfs.py ozbarley: landrace SNPchip xlsx (499 lines, AVRIG 40K markers with MorexV3 positions; exported to landrace_chip.tsv) + elite HapMap (214 lines; chip markers matched by position, partly Beagle-imputed by the authors) -> ozbarley_40k_morexv3.vcf.gz: 11,509 markers, 709 lines (4 replicate DNA samples dropped; 118 markers whose MorexV3 base is not an allele dropped). No strand flips were needed.
  prep_ozbarley_meta.py (system python3 + openpyxl): MCPD -> meta.tsv; imaging/tiller BLUEs + X-ray CT line means -> pheno.tsv.
  load_ozbarley.py dryrun|commit: species "Hordeum vulgare MorexV3" (build MorexV3, array WheatBarley40K), Reference 9, AccessionMetadata, 12,954 AccessionPhenotype values (61 traits, 220 elite lines).
  Checks: Morex (OzB_170) 8,401 hom-REF / 3 hom-ALT; verify_ozbarley.py: 1,074/1,074 random API genotypes match the source files.
- T3 UMN_NSGC_GWAS (748 NSGC accessions, 50K/9K iSelect): build_barley_vcfs.py nsgc -> /data/cropsnpdb/barley/t3/nsgc_50k_morexv3.vcf.gz (18,673 array markers; chrUn, S#H_ SNPs and A/T|C/G SNPs dropped). NOT LOADED: at 397 positions shared with OzBarley, ~12% of NSGC markers have allele letters inverted relative to OzBarley (Morex-validated); T3 REF = major allele (TASSEL) with mixed-strand letters (cross_check.py, morex_check.py).
