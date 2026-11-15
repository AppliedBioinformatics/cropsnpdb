"""Register the AGILE Lentil Diversity Panel exome-capture SNPs (KnowPulse experiment AGILE-LDP-ExomeCapture;
Ogutcen et al. 2018 exome capture array; Guerra-Garcia et al. 2022 Evol Appl doi:10.1111/eva.13467) as VCF-backed
species 'Lens culinaris CDC Redberry v2' (build Lcu2RBY, array LentilExomeCapture). 324 lines.
Usage: load_ldp.py dryrun|commit"""
import gzip, sys, pymysql
sys.path.insert(0, "/var/www/html/cropsnpdb/snpdb/app"); import config
VCF = "/data/cropsnpdb/lentil/ldp/ldp_exome_lcu2rby_snps.vcf.gz"
SPECIES, BUILD, ARRAY, DOI = "Lens culinaris CDC Redberry v2", "Lcu2RBY", "LentilExomeCapture", "10.1111/eva.13467"
URL = "https://knowpulse.usask.ca/experiment/AGILE-LDP-ExomeCapture"
commit = sys.argv[1:] == ["commit"]
c = pymysql.connect(host=config.MYSQL_DATABASE_HOST, user=config.MYSQL_DATABASE_USER, password=config.MYSQL_DATABASE_PASSWORD,
                    db=config.MYSQL_DATABASE_DB, charset="utf8mb4", autocommit=False)
cur = c.cursor()
def q(s, a=None): cur.execute(s, a); return cur.fetchall()
arr = q("SELECT idSNPArray FROM SNPArray WHERE SNPArrayName=%s", (ARRAY,))
if arr: arr = arr[0][0]
else: cur.execute("INSERT INTO SNPArray (SNPArrayName) VALUES (%s)", (ARRAY,)); arr = cur.lastrowid
sp = q("SELECT idSpecie FROM Specie WHERE SpecieName=%s", (SPECIES,))
if sp: sp = sp[0][0]
else: cur.execute("INSERT INTO Specie (SpecieName, Specie_idSNPArray, Build) VALUES (%s,%s,%s)", (SPECIES, arr, BUILD)); sp = cur.lastrowid
ref = q("SELECT RefID FROM Reference WHERE DOI=%s", (DOI,))
if ref: ref = ref[0][0]
else:
    ref = q("SELECT MAX(RefID)+1 FROM Reference")[0][0]
    cur.execute("INSERT INTO Reference (RefID,Authors,Title,Date,Journal,Vol,Page,DOI) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                (ref, "Guerra-Garcia A, Haile T, Ogutcen E et al.", "An evolutionary look into the history of lentil reveals unexpected diversity (AGILE LDP exome capture SNPs, KnowPulse)",
                 2022, "Evol Appl", "15", "NA", DOI))
with gzip.open(VCF, "rt") as f:
    for line in f:
        if line.startswith("#CHROM"): samples = line.rstrip("\n").split("\t")[9:]; break
cult = {n: i for i, n in q("SELECT idCultivar, CultivarName FROM Cultivar WHERE Specie_idSpecie=%s", (sp,))}
accs = dict(q("SELECT Accession, idAccession FROM Accession WHERE Accession LIKE 'LDP %%'"))
for s in samples:
    name = (s[:-4] if s.endswith("_AGL") else s).replace("_", " ")
    if name not in cult:
        cur.execute("INSERT INTO Cultivar (CultivarName, Specie_idSpecie) VALUES (%s,%s)", (name, sp)); cult[name] = cur.lastrowid
    a = "LDP " + s
    if a not in accs:
        cur.execute("INSERT INTO Accession (Accession, Cultivar_idCultivar, Accession_RefID) VALUES (%s,%s,%s)", (a, cult[name], ref)); accs[a] = cur.lastrowid
    cur.execute("REPLACE INTO AccessionVcfSample VALUES (%s,%s,%s)", (accs[a], s, VCF))
    cur.execute("""REPLACE INTO AccessionMetadata (Accession_idAccession,CropType,SuppliedSpecies,ExternalURL,MetadataSource)
                   VALUES (%s,%s,%s,%s,%s)""", (accs[a], "AGILE Lentil Diversity Panel", "Lens culinaris", URL, "KnowPulse (University of Saskatchewan)"))
have = q("SELECT COUNT(*) FROM SNP_Coordinates WHERE Specie_idSpecie=%s AND Specie_Build=%s", (sp, BUILD))[0][0]
n = 0
if not have:
    snp, coo = [], []
    def flush():
        cur.executemany("INSERT INTO SNP (SNPid, Reference, Strand, SNPArray_idSNPArray) VALUES (%s,%s,'+',%s)", snp)
        cur.executemany("INSERT INTO SNP_Coordinates VALUES (%s,%s,%s,%s,%s)", coo); snp.clear(); coo.clear()
    with gzip.open(VCF, "rt") as f:
        for line in f:
            if line[0] == "#": continue
            chrom, pos, sid, ref_a, alt = line.split("\t", 5)[:5]
            snp.append((sid, f"[{ref_a}/{alt}]", arr)); coo.append((sid, "chr" + chrom[3:], int(pos), sp, BUILD)); n += 1
            if len(snp) >= 20000: flush()
    flush()
print(f"SNPArray {arr}, Specie {sp} ({SPECIES}, {BUILD}), RefID {ref}, lines {len(samples)} ({len(cult)} names), SNPs {n} (already {have})")
if commit: c.commit(); print("COMMITTED")
else: c.rollback(); print("dry run: rolled back")
