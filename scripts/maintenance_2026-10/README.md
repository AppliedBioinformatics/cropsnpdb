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
- `load_t3_pheno.py` – adds Location/NPlots columns to `AccessionPhenotype` and loads `data/t3_wheat_phenotypes_for_db.csv`:
  T3/Wheat field-trial means (per line x trial x trait) for 295 wheat lines, 51,984 values, 2,378 trials, 151 traits (accessed 2026-10-21 via BrAPI).
- `patch_pheno2.py` – adds Location and NPlots to `/phenotypes.csv`; updates Lines page text.
- `load_agg_40k.py` – AGG Wheat Release 260619 pilot (doi:10.7910/DVN/MOBTA8, CC BY 4.0): new array WheatBarley40K (id 3), species "Triticum aestivum RefSeq v2.1" (id 6, build RSv21), Reference 6;
  18,569 anchored markers, 1,728 accessions of 1,205 released Australian varieties (`data/agg40k_pilot_samples.tsv`, selected from Genesys MCPD: ORIGCTY=AUS, SAMPSTAT=500),
  32,087,232 genotype calls. Adds index idx_region on SNP_Coordinates.
- `patch_40k_code.py` – search robustness for new arrays (probe lookup, default NA browser link), line filter box on the Search page.
- `patch_40k_text.py` – Home/Lines/Download text and Genesys/AGG attribution.
- **Full AGG wheat 40K set (2026-10-29), VCF-backed:** `load_agg_full_meta.py` registers all 32,656 accessions (28,863 line names; passport data from Genesys MCPD incl. country, biological status, pedigree, donor) and maps each to its VCF sample in new table `AccessionVcfSample` (Cultivar.CultivarName widened to 150). Genotypes are read at query time from the bgzipped VCF (`/data/cropsnpdb/agg/v2.1_raw_unique.vcf.gz`, CSI index) by `app/ownLib/vcfBackend.py` (pysam; cap 3M genotypes/search).
  Search page uses type-ahead (`/api/lines`) for species with >5,000 lines; Lines page loads rows from `/lines.json`. `drop_pilot_rows.py` removed the 32M pilot rows after a 290,528-call comparison showed 0 differences.
