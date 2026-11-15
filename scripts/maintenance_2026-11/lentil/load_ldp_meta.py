"""AGILE LDP passport data and phenology for CropSNPdb lentil accessions (load_ldp.py first).
Source: Wright DM et al. (2021) Understanding photothermal interactions will help expand production range and increase
genetic diversity of lentil. Plants People Planet, doi:10.1002/ppp3.10158; data from
github.com/derekmichaelwright/AGILE_LDP_Phenology (data/data_ldp.csv = Supplemental Table 1; data/data_raw.csv plots).
Phenotypes: site-year means over reps of days from sowing to emergence, flowering, swollen pods and maturity (18 site-years).
Usage: load_ldp_meta.py dryrun|commit"""
import sys, csv, collections, statistics, pymysql
sys.path.insert(0, "/var/www/html/cropsnpdb/snpdb/app"); import config
W = "/data/cropsnpdb/lentil/ldp/wright"
SRC = "AGILE LDP phenology (Wright et al. 2021 Plants People Planet doi:10.1002/ppp3.10158)"
TR = {"DTE": "Days to emergence", "DTF": "Days to flowering", "DTS": "Days to swollen pods", "DTM": "Days to maturity"}
commit = sys.argv[1:] == ["commit"]
c = pymysql.connect(host=config.MYSQL_DATABASE_HOST, user=config.MYSQL_DATABASE_USER, password=config.MYSQL_DATABASE_PASSWORD,
                    db=config.MYSQL_DATABASE_DB, charset="utf8mb4", autocommit=False)
cur = c.cursor()
cur.execute("SELECT Accession, idAccession FROM Accession WHERE Accession LIKE 'LDP %%'"); accs = dict(cur.fetchall())
nm = 0
for r in csv.DictReader(open(f"{W}/data_ldp.csv")):
    a = accs["LDP " + r["Name"].replace(" ", "_")]
    cur.execute("UPDATE AccessionMetadata SET Country=%s, Donor=%s, MetadataSource=%s WHERE Accession_idAccession=%s",
                (r["Origin"] or None, r["Source"] or None, "KnowPulse; origin/source from Wright et al. 2021 Supplemental Table 1", a)); nm += cur.rowcount
vals = collections.defaultdict(list); loc = {}
for r in csv.DictReader(open(f"{W}/data_raw.csv")):
    for k in TR:
        v = r[k]
        if v not in ("", "NA"): vals[(r["Name"], r["Expt"], k)].append(float(v))
    loc[r["Expt"]] = r["Location"]
cur.execute("DELETE FROM AccessionPhenotype WHERE Source=%s", (SRC,))
rows = [(accs["LDP " + n.replace(" ", "_")], e, loc[e], TR[k], round(statistics.mean(v), 2), len(v), SRC) for (n, e, k), v in vals.items()]
cur.executemany("INSERT INTO AccessionPhenotype (Accession_idAccession,Trial,Location,Trait,Value,NPlots,Source) VALUES (%s,%s,%s,%s,%s,%s,%s)", rows)
print(f"metadata updated {nm}; phenotype values {len(rows)}; trials {len(loc)}; traits {len({r[3] for r in rows})}")
if commit: c.commit(); print("COMMITTED")
else: c.rollback(); print("dry run: rolled back")
