"""Register OzBarley (Baumann et al. 2026 Sci Data 13:703, doi:10.1038/s41597-026-07056-y; Figshare CC BY 4.0)
as a VCF-backed CropSNPdb species: 'Hordeum vulgare MorexV3', build MorexV3, array WheatBarley40K.
VCF: /data/cropsnpdb/barley/ozbarley/ozbarley_40k_morexv3.vcf.gz (build_barley_vcfs.py ozbarley).
Adds Reference, Specie, Cultivar + Accession (OzBarley code) per line, AccessionVcfSample, AccessionMetadata (MCPD),
AccessionPhenotype (APPN greenhouse BLUEs, X-ray CT line means), SNP + SNP_Coordinates rows.
Usage: load_ozbarley.py dryrun|commit"""
import gzip, sys, csv, re, pymysql
sys.path.insert(0, "/var/www/html/cropsnpdb/snpdb/app"); import config
exec(re.search(r"^CTY=\{.*?\}$", open('/home/appbioadm/snpdb_backup_20261017/load_agg_full_meta.py').read(), re.M|re.S).group(0))
D = "/data/cropsnpdb/barley/ozbarley"; VCF = D + "/ozbarley_40k_morexv3.vcf.gz"
SPECIES, BUILD, ARRAY = "Hordeum vulgare MorexV3", "MorexV3", "WheatBarley40K"
DOI = "10.1038/s41597-026-07056-y"
SRC = "OzBarley MCPD (Baumann et al. 2026; Figshare doi:10.25909/29104916)"
PSRC = "OzBarley (Baumann et al. 2026; Figshare doi:10.25909/28545575)"
commit = sys.argv[1:] == ["commit"]
c = pymysql.connect(host=config.MYSQL_DATABASE_HOST, user=config.MYSQL_DATABASE_USER, password=config.MYSQL_DATABASE_PASSWORD,
                    db=config.MYSQL_DATABASE_DB, charset="utf8mb4", autocommit=False)
cur = c.cursor()
def q(s, a=None): cur.execute(s, a); return cur.fetchall()

arr = q("SELECT idSNPArray FROM SNPArray WHERE SNPArrayName=%s", (ARRAY,))[0][0]
sp = q("SELECT idSpecie FROM Specie WHERE SpecieName=%s", (SPECIES,))
if sp: sp = sp[0][0]
else: cur.execute("INSERT INTO Specie (SpecieName, Specie_idSNPArray, Build) VALUES (%s,%s,%s)", (SPECIES, arr, BUILD)); sp = cur.lastrowid
ref = q("SELECT RefID FROM Reference WHERE DOI=%s", (DOI,))
if ref: ref = ref[0][0]
else:
    ref = q("SELECT MAX(RefID)+1 FROM Reference")[0][0]
    cur.execute("INSERT INTO Reference (RefID,Authors,Title,Date,Journal,Vol,Page,DOI) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                (ref, "Baumann U, Kalashyan E, Schwerdt J et al.", "OzBarley: A genetic and phenotypic data resource capturing the Australian barley breeding history",
                 2026, "Sci Data", "13", "703", DOI))

names = {r[0]: (r[1], r[2]) for r in csv.reader(open(D + "/ozbarley_samples.tsv"), delimiter="\t")}
meta = {r["code"]: r for r in csv.DictReader(open(D + "/meta.tsv"), delimiter="\t")}
with gzip.open(VCF, "rt") as f:
    for line in f:
        if line.startswith("#CHROM"): samples = line.rstrip("\n").split("\t")[9:]; break
cult = {n: i for i, n in q("SELECT idCultivar, CultivarName FROM Cultivar WHERE Specie_idSpecie=%s", (sp,))}
accs = {a: i for a, i in q("SELECT a.Accession, a.idAccession FROM Accession a JOIN Cultivar c ON c.idCultivar=a.Cultivar_idCultivar WHERE c.Specie_idSpecie=%s", (sp,))}
nmeta = 0
for s in samples:
    name, panel = names[s]
    if name not in cult:
        cur.execute("INSERT INTO Cultivar (CultivarName, Specie_idSpecie) VALUES (%s,%s)", (name, sp)); cult[name] = cur.lastrowid
    if s not in accs:
        cur.execute("INSERT INTO Accession (Accession, Cultivar_idCultivar, Accession_RefID) VALUES (%s,%s,%s)", (s, cult[name], ref)); accs[s] = cur.lastrowid
    cur.execute("REPLACE INTO AccessionVcfSample VALUES (%s,%s,%s)", (accs[s], s, VCF))
    m = meta.get(s)
    ct = ("OzBarley elite panel" if panel == "elite" else "OzBarley landrace panel") + (f"; {m['subtaxa']}" if m and m['subtaxa'] else "")
    if m:
        nmeta += 1
        url = f"https://ausgenebank.agriculture.vic.gov.au/gringlobal/search?q={m['agg_id']}" if m['agg_id'] else "https://doi.org/10.25909/c.6952545"
    cur.execute("""REPLACE INTO AccessionMetadata (Accession_idAccession,Country,Pedigree,BreedingOrganization,AGG_ID,BiologicalStatus,CropType,
                   SuppliedSpecies,Donor,ExternalURL,MetadataSource) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (accs[s], CTY.get(m['country'], m['country']) if m else None, (m['pedigree'] or None) if m else None,
                 (m['breeder'] or None) if m else None, (m['agg_id'] or None) if m else None, (m['status'] or None) if m else None,
                 ct, "Hordeum vulgare", (m['donor'] or None) if m else None,
                 url if m else "https://doi.org/10.25909/c.6952545", SRC))

cur.execute("DELETE p FROM AccessionPhenotype p JOIN Accession a ON a.idAccession=p.Accession_idAccession JOIN Cultivar c ON c.idCultivar=a.Cultivar_idCultivar WHERE c.Specie_idSpecie=%s AND p.Source=%s", (sp, PSRC))
ph = [(accs[r["code"]], r["trial"], "Australian Plant Phenomics Network, University of Adelaide", r["trait"], r["value"], None, PSRC)
      for r in csv.DictReader(open(D + "/pheno.tsv"), delimiter="\t") if r["code"] in accs]
cur.executemany("INSERT INTO AccessionPhenotype (Accession_idAccession,Trial,Location,Trait,Value,NPlots,Source) VALUES (%s,%s,%s,%s,%s,%s,%s)", ph)

have = q("SELECT COUNT(*) FROM SNP_Coordinates WHERE Specie_idSpecie=%s AND Specie_Build=%s", (sp, BUILD))[0][0]
known = {r[0] for r in q("SELECT SNPid FROM SNP WHERE SNPArray_idSNPArray=%s", (arr,))}
n = 0; ns = 0
if not have:
    snp, coo = [], []
    with gzip.open(VCF, "rt") as f:
        for line in f:
            if line[0] == "#": continue
            chrom, pos, sid, ref_a, alt = line.split("\t", 5)[:5]
            if sid not in known: snp.append((sid, f"[{ref_a}/{alt}]", arr)); known.add(sid); ns += 1
            coo.append((sid, "chr" + chrom[3:], int(pos), sp, BUILD)); n += 1
    cur.executemany("INSERT INTO SNP (SNPid, Reference, Strand, SNPArray_idSNPArray) VALUES (%s,%s,'+',%s)", snp)
    cur.executemany("INSERT INTO SNP_Coordinates VALUES (%s,%s,%s,%s,%s)", coo)
print(f"Specie {sp} ({SPECIES}), RefID {ref}, lines {len(samples)} ({len(cult)} cultivar names), metadata {nmeta}, phenotype values {len(ph)}, "
      f"coordinates {n} (SNP rows new {ns}; already {have})")
if commit: c.commit(); print("COMMITTED")
else: c.rollback(); print("dry run: rolled back")
