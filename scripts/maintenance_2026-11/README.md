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
- OzBarley elite RNA-seq SNPs: build_barley_vcfs.py rnaseq -> /data/cropsnpdb/barley/ozbarley/ozbarley_rnaseq_morexv3.vcf.gz (108,970 SNPs not at 40K chip positions, 214 elite lines, SnpEff GENE/EFFECT/IMPACT in INFO; 27 dropped as REF not an allele). load_ozbarley_rnaseq.py: species "Hordeum vulgare MorexV3 RNA-seq" (array OzBarleyRNAseq), accessions <OzB code>-RNAseq with metadata copied from the 40K accessions. Morex: 108,682 hom-REF / 207 hom-ALT / 36 het.

## Lentil (2026-11-15) – scripts in lentil/
- Source: KnowPulse experiment AGILE-LDP-ExomeCapture, LDP-Lc2.0-Oct8_maf05-95_x90_minSNPQ30.recode.vcf.gz (CDC Redberry v2.0 = Lcu.2RBY; QUAL>=30, depth>=3, <=10% missing, MAF>=5%, CNV SNPs removed). No licence stated on the page; cite the data source and Guerra-Garcia et al. 2022 (doi:10.1111/eva.13467). In /data/cropsnpdb/lentil/ldp/.
- build_ldp_vcf.py: biallelic SNPs on Chr1-7, GT only, IDs LcRBY2_<chr>_<pos> -> ldp_exome_lcu2rby_snps.vcf.gz (459,938 SNPs, 324 lines; 106,495 indels/multiallelic and 12,457 unitig sites dropped). 1,590/1,590 random genotypes match the source.
- load_ldp.py: species "Lens culinaris CDC Redberry v2" (build Lcu2RBY, array LentilExomeCapture), Reference (Guerra-Garcia 2022), Cultivar = germplasm name without _AGL, Accession "LDP <sample>", minimal metadata (link to KnowPulse). API aliases lentil, lentil_ldp. No passport data or phenotypes yet.
- load_ldp_meta.py: origin + source genebank for all 324 LDP lines and 20,903 phenology values (site-year means of days to emergence/flowering/swollen pods/maturity, 18 site-years) from Wright et al. 2021 Plants People Planet doi:10.1002/ppp3.10158 (github.com/derekmichaelwright/AGILE_LDP_Phenology data_ldp.csv, data_raw.csv; in /data/cropsnpdb/lentil/ldp/wright/).

## Chickpea (2026-11-15) – scripts in chickpea/
- Source: LIS datastore Cicer/arietinum/diversity/CDCFrontier.div.vonWettberg_Chang_2018 (licence Open; von Wettberg et al. 2018 Nat Commun 9:649, doi:10.1038/s41467-018-02867-z), 279 accessions, WGS GATK calls on CDC Frontier v1. CicerSeq (3,366 genomes) has no downloadable SNP VCF (query tool only).
- build_cicer_vcf.sh (bcftools 1.19, apt): FILTER PASS, biallelic SNPs on Ca1-Ca8, F_MISSING<=0.2, MAF>=0.05, GT only, IDs CaFr1_<chr>_<pos> -> /data/cropsnpdb/chickpea/vonwettberg/cicer_wgs_cdcfrontier1_snps.vcf.gz (2,008,314 SNPs). 1,500/1,500 random genotypes match the source.
- load_cicer.py: species "Cicer arietinum CDC Frontier v1" (build CaFrontier1, array CicerWGS; chromosomes Ca1..Ca8 used as-is), 166 C. reticulatum + 63 C. echinospermum (species/site from sample-ID prefix per the paper) + 50 cultivated/other. API aliases chickpea, cicer_wgs.
