# CropSNPdb

CropSNPdb is a web database of SNP array genotypes for *Brassica* crops and hexaploid bread wheat
(*Triticum aestivum*). It hosts genotypes from the Illumina Infinium *Brassica* 60K and wheat 90K arrays
and lets users search SNPs by genomic region and line, browse line metadata, and download data in bulk.

**Live site:** https://snpdb.appliedbioinformatics.com.au

## Citation

If you use CropSNPdb, please cite:

> Scheben A, Verpaalen B, Lawley CT, Chan CK, Bayer PE, Batley J, Edwards D (2019)
> CropSNPdb: a database of SNP array data for *Brassica* crops and hexaploid bread wheat.
> *The Plant Journal* 98: 142–152. https://doi.org/10.1111/tpj.14194

## What's in the database

| Array | Reference genomes | Lines | Accessions |
|---|---|---|---|
| *Brassica* 60K | *B. napus* Darmor v8.1 and v4.1, *B. rapa* v3, *B. oleracea* v2.1, *B. juncea* v1.5 | 526 | 575 |
| Wheat 90K | IWGSC RefSeq v1.0 and wheat pangenome | 309 | 309 |

Genotypes come from published studies (Mason et al. 2015; Qian et al. 2014; Xu et al. 2016;
Higgins et al. 2018) and T3/Wheat. Line metadata (country, ecotype, breeding status, pedigree,
genebank IDs) and Australian Grains Genebank field phenotypes were added in October 2026 from the
same sources; see [`scripts/maintenance_2026-10`](scripts/maintenance_2026-10).

## Features

- **Search** – SNP genotypes for selected lines in a chromosomal region, with SNP details and genome-browser links
- **Lines** – all accessions with available metadata (`/lines`, `/lines.csv`, `/phenotypes.csv`)
- **Download** – per-chromosome genotype matrices
- **Upload** – submission of new SNP array datasets for curation

## Repository layout

```
app/
  app.py              Flask application entry (imported by snpdb.wsgi)
  views.py            routes: search, lines, download, submit
  forms.py            WTForms definitions
  ownLib/             database queries, parsing, file handling, upload alerts (notify.py)
  templates/          Jinja2 templates
  static/             CSS, JavaScript, probe sequences and example upload files
  config.py.example   settings template (copy to config.py)
snpdb.wsgi            mod_wsgi entry point
mail.cfg.example      optional SMTP settings for upload alerts
scripts/              maintenance scripts and source data
```

Not included: the MySQL database dump, the bulk download files (`app/data/`), uploaded submissions and
real configuration files. Contact the maintainers below if you need the database.

## Running it

Production runs on Ubuntu 24.04 with Apache 2.4 + `libapache2-mod-wsgi-py3`, MySQL 8.0 and Python 3.12.

1. **Database.** Create the database and an application user (use a strong password; limit privileges in production):
   ```sql
   CREATE DATABASE snpdb;
   CREATE USER 'flask'@'localhost' IDENTIFIED BY 'CHANGE_ME';
   GRANT SELECT, INSERT, UPDATE ON snpdb.* TO 'flask'@'localhost';
   ```
   then load the database dump.
2. **Python environment.**
   ```bash
   python3 -m venv venv
   venv/bin/pip install -r requirements.txt
   ```
3. **Settings.** Copy `app/config.py.example` to `app/config.py` and set the MySQL credentials.
   Keep `DEBUG = False` in production. `config.py` is ignored by git.
4. **Web server.** Point an Apache `WSGIScriptAlias` at `snpdb.wsgi` (adjust the paths in it), using a
   `WSGIDaemonProcess`, plus `Alias /data` for the bulk files. Touch `snpdb.wsgi` to reload after code changes
   (run `python3 -m py_compile` on edited files first, as a syntax error takes the whole site down).
5. **Upload alerts (optional).** Copy `mail.cfg.example` to `mail.cfg` next to `snpdb.wsgi`, fill in SMTP
   details and make it readable only by the web server (`chown root:www-data mail.cfg; chmod 640 mail.cfg`).
   Without this file uploads still work but no email is sent. Submissions are saved under `app/app/uploadFiles/`.

## History

Originally developed by Armin Scheben, Brent Verpaalen and colleagues (code first published at
[ascheben/snpdb](https://github.com/ascheben/snpdb), 2019). Moved to this repository in October 2026
after a maintenance round that fixed broken links and uploads, corrected line names and species
assignments, and added line metadata and phenotypes.

## Contact and licence

Applied Bioinformatics Group, The University of Western Australia –
Prof. David Edwards (dave.edwards@uwa.edu.au).

Code released under the [MIT Licence](LICENSE). Genotype data remain subject to the terms of their
original publications and sources.
