"""Register the B. napus pangenome WGS SNPs (Hurgobin et al. 2018 doi:10.1111/pbi.12867; brassicagenome.net
BnaPan.SNPs.vcf.gz, filtered by filter_pansnp.py: biallelic SNPs, QUAL>=30, <=20% missing, MAF>=0.05, placed
chromosomes A01..C09) as a VCF-backed CropSNPdb species.
Genotypes stay in /data/cropsnpdb/bnapus_pangenome/bnapus_pangenome_v81.vcf.gz (53 lines, 1,358,868 SNPs).
Adds: SNPArray, Specie 'Brassica napus pangenome v81' (Build v81pan), Reference, one Cultivar + Accession per line,
AccessionVcfSample, and SNP + SNP_Coordinates rows (needed for marker counts and /markers).
Usage: load_bnapus_pangenome.py dryrun|commit"""
import gzip, sys, pymysql
sys.path.insert(0, "/var/www/html/cropsnpdb/snpdb/app"); import config
D = "/data/cropsnpdb/bnapus_pangenome"; VCF = D + "/bnapus_pangenome_v81.vcf.gz"
SPECIES, BUILD, ARRAY = "Brassica napus pangenome v81", "v81pan", "BnapusPangenomeWGS"
DOI = "10.1111/pbi.12867"
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
                (ref, "Hurgobin B et al.", "Homoeologous exchange is a major cause of gene presence/absence variation in the amphidiploid Brassica napus (pangenome WGS SNPs, brassicagenome.net)",
                 2018, "Plant Biotechnol J", "16", "1265-1274", DOI))

samples = None
with gzip.open(VCF, "rt") as f:
    for line in f:
        if line.startswith("#CHROM"):
            samples = line.rstrip("\n").split("\t")[9:]; break
cult = {n: i for i, n in q("SELECT idCultivar, CultivarName FROM Cultivar WHERE Specie_idSpecie=%s", (sp,))}
accs = dict(q("SELECT Accession, idAccession FROM Accession"))
for s in samples:
    if s not in cult:
        cur.execute("INSERT INTO Cultivar (CultivarName, Specie_idSpecie) VALUES (%s,%s)", (s, sp)); cult[s] = cur.lastrowid
    acc = "BnaPan " + s
    if acc not in accs:
        cur.execute("INSERT INTO Accession (Accession, Cultivar_idCultivar, Accession_RefID) VALUES (%s,%s,%s)", (acc, cult[s], ref)); accs[acc] = cur.lastrowid
    cur.execute("REPLACE INTO AccessionVcfSample VALUES (%s,%s,%s)", (accs[acc], s, VCF))

have = q("SELECT COUNT(*) FROM SNP_Coordinates WHERE Specie_idSpecie=%s AND Specie_Build=%s", (sp, BUILD))[0][0]
n = 0
if not have:
    snp, coo = [], []
    def flush():
        cur.executemany("INSERT INTO SNP (SNPid, Reference, Strand, SNPArray_idSNPArray) VALUES (%s,%s,'NA',%s)", snp)
        cur.executemany("INSERT INTO SNP_Coordinates VALUES (%s,%s,%s,%s,%s)", coo)
        snp.clear(); coo.clear()
    with gzip.open(VCF, "rt") as f:
        for line in f:
            if line[0] == "#": continue
            chrom, pos, sid, ref_a, alt = line.split("\t", 5)[:5]
            sid = sid if sid.startswith("BnaPan_") else "BnaPan_" + sid
            snp.append((sid, f"[{ref_a}/{alt}]", arr)); coo.append((sid, chrom, int(pos), sp, BUILD)); n += 1
            if len(snp) >= 20000: flush()
    flush()
print(f"SNPArray {arr}, Specie {sp} ({SPECIES}, {BUILD}), RefID {ref}, lines {len(samples)}, SNPs inserted {n} (already {have})")
print("VCF samples registered", q("SELECT VcfPath, COUNT(*) FROM AccessionVcfSample GROUP BY VcfPath"))
if commit: c.commit(); print("COMMITTED")
else: c.rollback(); print("dry run: rolled back")
