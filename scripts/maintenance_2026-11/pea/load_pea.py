"""Register pea SNP datasets from the LIS datastore (licence Open, Cameor v2) as VCF-backed CropSNPdb species.
psppc: 'Pisum sativum Cameor v2 PSPPC' - USDA Pea Single Plant Plus Collection GBS (Beagle-imputed), 456 accessions
       (431 P. sativum, 25 P. fulvum; taxon and accession name from ENA PRJNA379298); Powers et al. 2021 G3 doi:10.1093/g3journal/jkab227.
ams:   'Pisum sativum Cameor v2 AMS' - AMS panel of Aubert et al. 2023 recalled on Cameor v2; Kreplak et al. 2026 Sci Data
       doi:10.1038/s41597-026-07347-4.
Usage: load_pea.py psppc|ams dryrun|commit"""
import gzip, sys, csv, pymysql
sys.path.insert(0, "/var/www/html/cropsnpdb/snpdb/app"); import config
D = "/data/cropsnpdb/pea"
CFG = {"psppc": dict(vcf=D + "/pea_psppc_cameor2_snps.vcf.gz", species="Pisum sativum Cameor v2 PSPPC", array="PeaGBS_PSPPC", prefix="PSPPC ",
                     doi="10.1093/g3journal/jkab227", authors="Powers S, Boatwright JL, Thavarajah D",
                     title="Genome-wide association studies of mineral and phytic acid concentrations in pea (USDA PSPPC GBS SNPs, LIS datastore)",
                     year=2021, journal="G3", vol="11", page="jkab227", url="https://data.legumeinfo.org/Pisum/sativum/diversity/Cameor.gnm2.div.Powers_Boatwright_2021/"),
       "ams": dict(vcf=D + "/pea_ams_cameor2_snps.vcf.gz", species="Pisum sativum Cameor v2 AMS", array="PeaAMS", prefix="PeaAMS ",
                   doi="10.1038/s41597-026-07347-4", authors="Kreplak J, Novak P, Avila Robledillo L et al.",
                   title="A new genome assembly of the pea cultivar Cameor (AMS panel of Aubert et al. 2023 recalled on Cameor v2, LIS datastore)",
                   year=2026, journal="Sci Data", vol="NA", page="NA", url="https://data.legumeinfo.org/Pisum/sativum/diversity/Cameor.gnm2.div.Kreplak_Novak_2026/")}
mode = sys.argv[1]; C = CFG[mode]; BUILD = "Cameor2"
commit = sys.argv[2:] == ["commit"]
c = pymysql.connect(host=config.MYSQL_DATABASE_HOST, user=config.MYSQL_DATABASE_USER, password=config.MYSQL_DATABASE_PASSWORD,
                    db=config.MYSQL_DATABASE_DB, charset="utf8mb4", autocommit=False)
cur = c.cursor()
def q(s, a=None): cur.execute(s, a); return cur.fetchall()
arr = q("SELECT idSNPArray FROM SNPArray WHERE SNPArrayName=%s", (C["array"],))
if arr: arr = arr[0][0]
else: cur.execute("INSERT INTO SNPArray (SNPArrayName) VALUES (%s)", (C["array"],)); arr = cur.lastrowid
sp = q("SELECT idSpecie FROM Specie WHERE SpecieName=%s", (C["species"],))
if sp: sp = sp[0][0]
else: cur.execute("INSERT INTO Specie (SpecieName, Specie_idSNPArray, Build) VALUES (%s,%s,%s)", (C["species"], arr, BUILD)); sp = cur.lastrowid
ref = q("SELECT RefID FROM Reference WHERE DOI=%s", (C["doi"],))
if ref: ref = ref[0][0]
else:
    ref = q("SELECT MAX(RefID)+1 FROM Reference")[0][0]
    cur.execute("INSERT INTO Reference (RefID,Authors,Title,Date,Journal,Vol,Page,DOI) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                (ref, C["authors"], C["title"], C["year"], C["journal"], C["vol"], C["page"], C["doi"]))
taxon = {}
if mode == "psppc":
    for r in csv.DictReader(open(D + "/psppc_runs.tsv"), delimiter="\t"):
        taxon[r["sample_alias"]] = "Pisum fulvum" if "fulvum" in r["experiment_title"] else "Pisum sativum"
with gzip.open(C["vcf"], "rt") as f:
    for line in f:
        if line.startswith("#CHROM"): samples = line.rstrip("\n").split("\t")[9:]; break
cult = {n: i for i, n in q("SELECT idCultivar, CultivarName FROM Cultivar WHERE Specie_idSpecie=%s", (sp,))}
accs = dict(q("SELECT Accession, idAccession FROM Accession WHERE Accession LIKE %s", (C["prefix"] + "%",)))
for s in samples:
    name = s.replace("_", " ") if mode == "psppc" else s
    if name not in cult:
        cur.execute("INSERT INTO Cultivar (CultivarName, Specie_idSpecie) VALUES (%s,%s)", (name, sp)); cult[name] = cur.lastrowid
    a = C["prefix"] + s
    if a not in accs:
        cur.execute("INSERT INTO Accession (Accession, Cultivar_idCultivar, Accession_RefID) VALUES (%s,%s,%s)", (a, cult[name], ref)); accs[a] = cur.lastrowid
    cur.execute("REPLACE INTO AccessionVcfSample VALUES (%s,%s,%s)", (accs[a], s, C["vcf"]))
    tx = taxon.get(s, "Pisum sativum")
    ext = f"https://npgsweb.ars-grin.gov/gringlobal/search?q={name}" if mode == "psppc" else C["url"]
    cur.execute("""REPLACE INTO AccessionMetadata (Accession_idAccession,CropType,SuppliedSpecies,ExternalURL,MetadataSource) VALUES (%s,%s,%s,%s,%s)""",
                (accs[a], "USDA Pea Single Plant Plus Collection" if mode == "psppc" else "AMS panel (Aubert et al. 2023)", tx, ext,
                 "ENA PRJNA379298 sample aliases" if mode == "psppc" else "LIS datastore"))
have = q("SELECT COUNT(*) FROM SNP_Coordinates WHERE Specie_idSpecie=%s AND Specie_Build=%s", (sp, BUILD))[0][0]
n = 0
if not have:
    snp, coo = [], []
    def flush():
        cur.executemany("INSERT INTO SNP (SNPid, Reference, Strand, SNPArray_idSNPArray) VALUES (%s,%s,'+',%s)", snp)
        cur.executemany("INSERT INTO SNP_Coordinates VALUES (%s,%s,%s,%s,%s)", coo); snp.clear(); coo.clear()
    with gzip.open(C["vcf"], "rt") as f:
        for line in f:
            if line[0] == "#": continue
            chrom, pos, sid, ref_a, alt = line.split("\t", 5)[:5]
            snp.append((sid, f"[{ref_a}/{alt}]", arr)); coo.append((sid, "chr" + chrom[3:], int(pos), sp, BUILD)); n += 1
            if len(snp) >= 20000: flush()
    flush()
print(f"SNPArray {arr}, Specie {sp} ({C['species']}), RefID {ref}, lines {len(samples)} ({len(cult)} names), taxa {dict((t, list(taxon.values()).count(t)) for t in set(taxon.values()))}, SNPs {n} (already {have})")
if commit: c.commit(); print("COMMITTED")
else: c.rollback(); print("dry run: rolled back")
