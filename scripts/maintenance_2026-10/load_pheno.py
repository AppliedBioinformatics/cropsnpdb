import sys, csv, pymysql
sys.path.insert(0,'/var/www/html/cropsnpdb/snpdb/app'); import config
c=pymysql.connect(host=config.MYSQL_DATABASE_HOST,user=config.MYSQL_DATABASE_USER,password=config.MYSQL_DATABASE_PASSWORD,db=config.MYSQL_DATABASE_DB,charset='utf8mb4',autocommit=False)
cur=c.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS AccessionPhenotype (
 idPhenotype INT NOT NULL AUTO_INCREMENT PRIMARY KEY, Accession_idAccession INT NOT NULL,
 Trial VARCHAR(20) NOT NULL, Trait VARCHAR(100) NOT NULL, Value VARCHAR(255),
 Source VARCHAR(255) DEFAULT 'Australian Grains Genebank via Mason et al. 2015 Table S1',
 KEY k_acc (Accession_idAccession),
 CONSTRAINT fk_AccPheno_Accession FOREIGN KEY (Accession_idAccession) REFERENCES Accession(idAccession)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")
cur.execute("SELECT COUNT(*) FROM AccessionPhenotype"); assert cur.fetchone()[0]==0, 'already loaded'
cur.execute("SELECT Accession,idAccession FROM Accession WHERE Accession_RefID=1"); ids=dict(cur.fetchall())
n=miss=0
for r in csv.DictReader(open(sys.argv[2])):
    i=ids.get(r['Accession'])
    if not i: miss+=1; continue
    cur.execute("INSERT INTO AccessionPhenotype (Accession_idAccession,Trial,Trait,Value) VALUES (%s,%s,%s,%s)",(i,r['Trial'],r['Trait'],r['Value'])); n+=1
print('inserted',n,'unmatched',miss)
if sys.argv[1]=='commit': c.commit(); print('COMMITTED')
else: c.rollback(); print('rolled back')
