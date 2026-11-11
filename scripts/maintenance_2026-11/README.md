# CAIGE 40K wheat genotypes (2026-11)

Source: CSIRO Data Access Portal csiro:65245, doi:10.25919/3x88-4p26 (CC BY 4.0); Fradgley et al. 2025 TAG 138:241.
Files in /data/cropsnpdb/caige/.

1. `python3 xlsx2tsv.py Sample_details.xlsx sample_details.tsv`
2. `venv/bin/python build_vcf.py`: IWGSC v2.0 calls -> caige_40k_v2.1.vcf.gz on the AGG RefSeq v2.1 marker set
   (17,755 shared markers, AGG positions and REF/ALT; Replicate 2 samples dropped; 376 lines).
3. `venv/bin/python load_caige_meta.py dryrun|commit`: Reference 7, Cultivar `CAIGE <nursery>-<entry> (GID <gid>)`,
   Accession `CAIGE GID <gid>`, AccessionMetadata (selection history, breeding programme from its prefix),
   AccessionVcfSample -> CAIGE VCF. Species 6 (Triticum aestivum RefSeq v2.1).
