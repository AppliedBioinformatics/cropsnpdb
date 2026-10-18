# October 2026 maintenance scripts

Run on cropsnpdb-server-jun26 (17-18 Oct 2026). Kept for provenance; most are one-off.

- `apply_metadata.py` – data fixes (Xu line names, references, J30 moved to B. rapa) and creation of `AccessionMetadata`.
  Note: MySQL DDL commits implicitly, so its "dry run" mode is not a true dry run.
- `load_metadata.py` – loads `data/cropsnpdb_recovered_metadata.csv` into `AccessionMetadata` (878 rows).
- `load_pheno.py` – loads `data/mason_agg_phenotypes_long.csv` (AGG field data, Mason et al. 2015 Table S1) into `AccessionPhenotype`.
- `fix_bulk.py` – updates static bulk CSVs in `app/data` (renamed Xu columns; J30 moved from B. napus to B. rapa files).
- `patch_notify.py`, `test_upload.py` – upload email-alert patch and its test (fake SMTP).

Metadata sources: Mason et al. 2015 Mol Ecol Resour 15:1091 (Table S1, Australian Grains Genebank);
Xu et al. 2016 DNA Res 23:43 (Table S1); Qian et al. 2014 BMC Genomics 15:1170 (Additional file 2);
Higgins et al. 2018 G3 8:2673 (Methods); T3/Wheat BrAPI (accessed 2026-10-18).
