"""Seed protein and amino acid concentrations (NIRS predictions) for the AGILE LDP lentil accessions:
4 site-years (Rosthern and Sutherland, Canada, 2016-2017). Source: Wright DM, Hang J, House JD, Bett KE (2025)
Crop Sci 65:e70085, doi:10.1002/csc2.70085; data github.com/derekmichaelwright/AGILE_LDP_Protein Data/myY_NIRS.csv.
Usage: load_ldp_protein.py dryrun|commit"""
import sys, csv, re, pymysql
sys.path.insert(0, "/var/www/html/cropsnpdb/snpdb/app"); import config
F = "/data/cropsnpdb/lentil/ldp/protein/myY_NIRS.csv"
SRC = "AGILE LDP protein/amino acids by NIRS (Wright et al. 2025 Crop Sci doi:10.1002/csc2.70085)"
SITE = {"Ro": "Rosthern, Canada", "Su": "Sutherland, Canada"}
commit = sys.argv[1:] == ["commit"]
c = pymysql.connect(host=config.MYSQL_DATABASE_HOST, user=config.MYSQL_DATABASE_USER, password=config.MYSQL_DATABASE_PASSWORD,
                    db=config.MYSQL_DATABASE_DB, charset="utf8mb4", autocommit=False)
cur = c.cursor()
cur.execute("SELECT Accession, idAccession FROM Accession WHERE Accession LIKE 'LDP %%'")
norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
accs = {norm(a[4:]): i for a, i in cur.fetchall()}
rows, miss = [], []
for r in csv.DictReader(open(F)):
    n = r["Name"]; n = n[1:] if re.match(r"^X\d", n) else n
    a = accs.get(norm(n))
    if a is None: miss.append(r["Name"]); continue
    for k, v in r.items():
        if k == "Name" or v in ("", "NA"): continue
        trait, se = k.rsplit("_", 1)
        site = SITE[se[:2]]; year = "20" + se[2:]
        rows.append((a, f"{site} {year}", site, f"Seed {trait.lower()} (%, NIRS)" if trait != "Protein" else "Seed protein (%, NIRS)", v, None, SRC))
cur.execute("DELETE FROM AccessionPhenotype WHERE Source=%s", (SRC,))
cur.executemany("INSERT INTO AccessionPhenotype (Accession_idAccession,Trial,Location,Trait,Value,NPlots,Source) VALUES (%s,%s,%s,%s,%s,%s,%s)", rows)
print(f"values {len(rows)}, lines {len({r[0] for r in rows})}, traits {len({r[3] for r in rows})}, unmatched {miss}")
if commit: c.commit(); print("COMMITTED")
else: c.rollback(); print("dry run: rolled back")
