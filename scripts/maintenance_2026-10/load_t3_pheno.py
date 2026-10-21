import sys, csv, pymysql
sys.path.insert(0,'/var/www/html/cropsnpdb/snpdb/app'); import config
c=pymysql.connect(host=config.MYSQL_DATABASE_HOST,user=config.MYSQL_DATABASE_USER,password=config.MYSQL_DATABASE_PASSWORD,db=config.MYSQL_DATABASE_DB,charset='utf8mb4',autocommit=False)
cur=c.cursor()
SRC='T3/Wheat (accessed 2026-10-21); mean of plots per trial'
# schema (DDL auto-commits, so done before the data transaction; idempotent)
cur.execute("SHOW COLUMNS FROM AccessionPhenotype"); cols={r[0]:r[1] for r in cur.fetchall()}
if cols['Trial'].lower()!='varchar(100)': cur.execute("ALTER TABLE AccessionPhenotype MODIFY Trial VARCHAR(100) NOT NULL")
if 'Location' not in cols: cur.execute("ALTER TABLE AccessionPhenotype ADD COLUMN Location VARCHAR(255) NULL AFTER Trial")
if 'NPlots' not in cols: cur.execute("ALTER TABLE AccessionPhenotype ADD COLUMN NPlots INT NULL AFTER Value")
c.commit()
cur.execute("SELECT COUNT(*) FROM AccessionPhenotype WHERE Source=%s",(SRC,)); assert cur.fetchone()[0]==0,'already loaded'
rows=[(int(r['idAccession']),r['Trial'],r['Location'] or None,r['Trait'],r['Value'],int(r['NPlots']),SRC) for r in csv.DictReader(open(sys.argv[2]))]
cur.executemany("INSERT INTO AccessionPhenotype (Accession_idAccession,Trial,Location,Trait,Value,NPlots,Source) VALUES (%s,%s,%s,%s,%s,%s,%s)",rows)
cur.execute("SELECT Source,COUNT(*),COUNT(DISTINCT Accession_idAccession) FROM AccessionPhenotype GROUP BY Source"); print(cur.fetchall())
if sys.argv[1]=='commit': c.commit(); print('COMMITTED')
else: c.rollback(); print('rolled back')
