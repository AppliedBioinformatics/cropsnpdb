"""Register the OzBarley elite RNA-seq SNPs (Baumann et al. 2026, Figshare doi:10.25909/29104916) as a second barley
VCF-backed species 'Hordeum vulgare MorexV3 RNA-seq' (build MorexV3, array OzBarleyRNAseq): 214 elite lines,
108,970 SNPs not on the 40K chip, SnpEff gene/effect/impact in the VCF INFO. Accessions are '<OzB code>-RNAseq';
passport metadata copied from the 40K accessions (load_ozbarley.py must run first).
Usage: load_ozbarley_rnaseq.py dryrun|commit"""
import gzip, sys, pymysql
sys.path.insert(0, "/var/www/html/cropsnpdb/snpdb/app"); import config
VCF = "/data/cropsnpdb/barley/ozbarley/ozbarley_rnaseq_morexv3.vcf.gz"
SPECIES, BUILD, ARRAY, DOI = "Hordeum vulgare MorexV3 RNA-seq", "MorexV3", "OzBarleyRNAseq", "10.1038/s41597-026-07056-y"
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
ref = q("SELECT RefID FROM Reference WHERE DOI=%s", (DOI,))[0][0]
with gzip.open(VCF, "rt") as f:
    for line in f:
        if line.startswith("#CHROM"): samples = line.rstrip("\n").split("\t")[9:]; break
src = {a: (i, cn) for a, i, cn in q("""SELECT a.Accession, a.idAccession, c.CultivarName FROM Accession a JOIN Cultivar c ON c.idCultivar=a.Cultivar_idCultivar
                                       JOIN Specie s ON s.idSpecie=c.Specie_idSpecie WHERE s.SpecieName='Hordeum vulgare MorexV3'""")}
cult = {n: i for i, n in q("SELECT idCultivar, CultivarName FROM Cultivar WHERE Specie_idSpecie=%s", (sp,))}
accs = dict(q("SELECT Accession, idAccession FROM Accession WHERE Accession LIKE %s", ("%-RNAseq",)))
for s in samples:
    sid, name = src[s]
    if name not in cult:
        cur.execute("INSERT INTO Cultivar (CultivarName, Specie_idSpecie) VALUES (%s,%s)", (name, sp)); cult[name] = cur.lastrowid
    a = s + "-RNAseq"
    if a not in accs:
        cur.execute("INSERT INTO Accession (Accession, Cultivar_idCultivar, Accession_RefID) VALUES (%s,%s,%s)", (a, cult[name], ref)); accs[a] = cur.lastrowid
    cur.execute("REPLACE INTO AccessionVcfSample VALUES (%s,%s,%s)", (accs[a], s, VCF))
    cur.execute("""REPLACE INTO AccessionMetadata (Accession_idAccession,Country,Ecotype,Subpopulation,Pedigree,BreedingOrganization,GrainHardness,GrainColour,
                   AGG_ID,BiologicalStatus,CropType,SuppliedSpecies,SNPConfirmedSpecies,SpeciesMisclassified,Donor,ExternalURL,MetadataSource)
                   SELECT %s,Country,Ecotype,Subpopulation,Pedigree,BreedingOrganization,GrainHardness,GrainColour,AGG_ID,BiologicalStatus,
                   REPLACE(CropType,'OzBarley elite panel','OzBarley elite panel (RNA-seq SNPs)'),SuppliedSpecies,SNPConfirmedSpecies,SpeciesMisclassified,
                   Donor,ExternalURL,MetadataSource FROM AccessionMetadata WHERE Accession_idAccession=%s""", (accs[a], sid))
have = q("SELECT COUNT(*) FROM SNP_Coordinates WHERE Specie_idSpecie=%s AND Specie_Build=%s", (sp, BUILD))[0][0]
n = 0
if not have:
    snp, coo = [], []
    with gzip.open(VCF, "rt") as f:
        for line in f:
            if line[0] == "#": continue
            chrom, pos, sid, ref_a, alt = line.split("\t", 5)[:5]
            snp.append((sid, f"[{ref_a}/{alt}]", arr)); coo.append((sid, "chr" + chrom[3:], int(pos), sp, BUILD)); n += 1
    for i in range(0, len(snp), 20000):
        cur.executemany("INSERT INTO SNP (SNPid, Reference, Strand, SNPArray_idSNPArray) VALUES (%s,%s,'+',%s)", snp[i:i+20000])
        cur.executemany("INSERT INTO SNP_Coordinates VALUES (%s,%s,%s,%s,%s)", coo[i:i+20000])
print(f"SNPArray {arr}, Specie {sp} ({SPECIES}), RefID {ref}, lines {len(samples)}, SNPs {n} (already {have})")
if commit: c.commit(); print("COMMITTED")
else: c.rollback(); print("dry run: rolled back")
