import sys, csv, pymysql
sys.path.insert(0,'/var/www/html/cropsnpdb/snpdb/app'); import config
COMMIT = len(sys.argv)>1 and sys.argv[1]=='commit'
c=pymysql.connect(host=config.MYSQL_DATABASE_HOST,user=config.MYSQL_DATABASE_USER,password=config.MYSQL_DATABASE_PASSWORD,db=config.MYSQL_DATABASE_DB,charset='utf8mb4',autocommit=False)
cur=c.cursor()
def one(sql,args=None):
    cur.execute(sql,args); return cur.fetchall()
# 4. metadata table
cur.execute("""CREATE TABLE IF NOT EXISTS AccessionMetadata (
 Accession_idAccession INT NOT NULL PRIMARY KEY,
 Country VARCHAR(100), Ecotype VARCHAR(100), Subpopulation VARCHAR(20), Pedigree TEXT,
 BreedingOrganization VARCHAR(255), GrainHardness VARCHAR(30), GrainColour VARCHAR(30),
 AGG_ID VARCHAR(20), BiologicalStatus VARCHAR(100), CropType VARCHAR(255),
 SuppliedSpecies VARCHAR(100), SNPConfirmedSpecies VARCHAR(100), SpeciesMisclassified VARCHAR(5),
 Donor VARCHAR(255), ExternalURL VARCHAR(255), MetadataSource VARCHAR(255),
 CONSTRAINT fk_AccMeta_Accession FOREIGN KEY (Accession_idAccession) REFERENCES Accession(idAccession)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")
def cl(v):
    v=(v or '').strip()
    return None if v in ('','NA','nan','None','Unknown','_') else v
rows=0
for r in csv.DictReader(open(sys.argv[2] if len(sys.argv)>2 else '/home/appbioadm/snpdb_backup_20261017/cropsnpdb_recovered_metadata.csv',encoding='utf-8')):
    st=cl(r.get('Status')); st=st[0].upper()+st[1:] if st else st
    if st and st.lower()=='advanced cultivar': st='Advanced cultivar'
    cur.execute("""INSERT INTO AccessionMetadata VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
      (int(r['idAccession']),cl(r['Country']),cl(r['Ecotype']),cl(r['Subpopulation']),cl(r['Pedigree']),cl(r.get('Organization')),cl(r.get('Hardness')),cl(r.get('Color')),
       cl(r.get('AGG_ID')),st,cl(r.get('CropType')),cl(r.get('SuppliedSpecies')),cl(r.get('ActualSpecies')),cl(r.get('Misclassified')),cl(r.get('Donor')),cl(r.get('T3_URL')),cl(r['MetadataSource'])))
    rows+=1
print('metadata rows',rows)
assert rows==878
print(one("SELECT COUNT(*),COUNT(Country),COUNT(Ecotype),COUNT(Subpopulation),COUNT(Pedigree),COUNT(BreedingOrganization),COUNT(AGG_ID) FROM AccessionMetadata"))
print(one("SELECT a.Accession,c.CultivarName,s.SpecieName FROM Accession a JOIN Cultivar c ON a.Cultivar_idCultivar=c.idCultivar JOIN Specie s ON s.idSpecie=c.Specie_idSpecie WHERE a.Accession IN ('J29','J30','Xu83','Xu224') GROUP BY a.Accession,c.CultivarName,s.SpecieName"))
if COMMIT: c.commit(); print('COMMITTED')
else: c.rollback(); print('DRY RUN - rolled back')
