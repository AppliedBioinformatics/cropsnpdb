"""Register the CAIGE 40K lines (CSIRO DAP csiro:65245, CC BY 4.0) in the VCF-backed WheatBarley40K species (idSpecie 6).
Genotypes stay in /data/cropsnpdb/caige/caige_40k_v2.1.vcf.gz (built by build_vcf.py on the AGG v2.1 marker set).
Usage: load_caige_meta.py dryrun|commit"""
import sys, csv, re, collections, pymysql
sys.path.insert(0, "/var/www/html/cropsnpdb/snpdb/app"); import config
D = "/data/cropsnpdb/caige"; VCF = D + "/caige_40k_v2.1.vcf.gz"; SP_ID = 6
SRC = "CSIRO DAP csiro:65245 doi:10.25919/3x88-4p26 (CC BY 4.0); breeding programme inferred from selection history"
PROG = [(r"^(CM|PT|CG|SD|CA)", "CIMMYT"), (r"^(ICW|ICAR|ISBW|AISBW)", "ICARDA"), (r"^(TCI|TIC)", "IWWIP (Türkiye-CIMMYT-ICARDA)")]
rows = [r for r in csv.DictReader(open(D + "/sample_details.tsv"), delimiter="\t") if r["Sample Type"] != "Replicate 2"]
c = pymysql.connect(host=config.MYSQL_DATABASE_HOST, user=config.MYSQL_DATABASE_USER, password=config.MYSQL_DATABASE_PASSWORD,
                    db=config.MYSQL_DATABASE_DB, charset="utf8mb4", autocommit=False)
cur = c.cursor()
def q(s, a=None): cur.execute(s, a); return cur.fetchall()
ref = q("SELECT RefID FROM Reference WHERE DOI=%s", ("10.25919/3x88-4p26",))
if ref: REF_ID = ref[0][0]
else:
    REF_ID = q("SELECT MAX(RefID)+1 FROM Reference")[0][0]
    cur.execute("INSERT INTO Reference (RefID,Authors,Title,Date,Journal,Vol,Page,DOI) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                (REF_ID, "Fradgley N (CSIRO)", "40K SNP array genotype data for CAIGE wheat lines (Infinium Wheat Barley 40K); see Fradgley et al. 2025 Theor Appl Genet 138:241 doi:10.1007/s00122-025-05023-6",
                 2025, "CSIRO Data Access Portal", "1", "NA", "10.25919/3x88-4p26"))
cult = {n: i for i, n in q("SELECT idCultivar,CultivarName FROM Cultivar WHERE Specie_idSpecie=%s", (SP_ID,))}
accs = dict(q("SELECT Accession,idAccession FROM Accession"))
new_c = new_a = clash = 0; prog = collections.Counter()
for r in rows:
    entry, nursery = r["QnoQcode"].split(":")
    name = f"CAIGE {nursery}-{entry} (GID {r['Supplied Sample GID']})"; acc = "CAIGE GID " + r["Supplied Sample GID"]
    if name in cult: clash += 1
    else:
        cur.execute("INSERT INTO Cultivar (CultivarName,Specie_idSpecie) VALUES (%s,%s)", (name, SP_ID)); cult[name] = cur.lastrowid; new_c += 1
    if acc not in accs:
        cur.execute("INSERT INTO Accession (Accession,Cultivar_idCultivar,Accession_RefID) VALUES (%s,%s,%s)", (acc, cult[name], REF_ID)); accs[acc] = cur.lastrowid; new_a += 1
    org = next((o for p, o in PROG if re.match(p, r["SEL HIST"])), None); prog[org] += 1
    cur.execute("""REPLACE INTO AccessionMetadata (Accession_idAccession,Pedigree,BreedingOrganization,BiologicalStatus,Donor,ExternalURL,MetadataSource)
        VALUES (%s,%s,%s,%s,%s,%s,%s)""", (accs[acc], "Selection history: " + r["SEL HIST"], org, "Breeding/research material",
        f"CAIGE (Australia-CIMMYT-ICARDA) nursery {nursery}, entry {entry}", "https://doi.org/10.25919/3x88-4p26", SRC))
    cur.execute("REPLACE INTO AccessionVcfSample VALUES (%s,%s,%s)", (accs[acc], "CAIGE_" + r["Supplied Sample GID"], VCF))
print("RefID", REF_ID, "lines", len(rows), "new cultivars", new_c, "name clashes", clash, "new accessions", new_a, "programme", dict(prog))
print("example", q("""SELECT c.CultivarName,a.Accession,v.SampleID,m.BreedingOrganization,m.Pedigree FROM Cultivar c JOIN Accession a ON a.Cultivar_idCultivar=c.idCultivar
   JOIN AccessionVcfSample v ON v.Accession_idAccession=a.idAccession JOIN AccessionMetadata m ON m.Accession_idAccession=a.idAccession WHERE a.Accession_RefID=%s LIMIT 3""", (REF_ID,)))
print("VCF samples registered", q("SELECT VcfPath,COUNT(*) FROM AccessionVcfSample GROUP BY VcfPath"))
if sys.argv[1] == "commit": c.commit(); print("COMMITTED")
else: c.rollback(); print("DRY RUN - rolled back")
