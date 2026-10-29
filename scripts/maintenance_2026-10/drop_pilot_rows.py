import sys, time, pymysql
sys.path.insert(0,'/var/www/html/cropsnpdb/snpdb/app'); import config
c=pymysql.connect(host=config.MYSQL_DATABASE_HOST,user=config.MYSQL_DATABASE_USER,password=config.MYSQL_DATABASE_PASSWORD,db=config.MYSQL_DATABASE_DB,autocommit=False); cur=c.cursor()
cur.execute("SELECT a.idAccession FROM Accession a JOIN AccessionVcfSample v ON v.Accession_idAccession=a.idAccession WHERE a.Accession_RefID=6")
ids=[r[0] for r in cur.fetchall()]; t0=time.time(); n=0
for i,aid in enumerate(ids):
    n+=cur.execute("DELETE FROM Accession_has_SNP WHERE Accession_idAccession=%s",(aid,)); c.commit()
    if i%200==0: print(f'{i}/{len(ids)} accessions checked, {n:,} rows deleted, {time.time()-t0:.0f}s',flush=True)
print(f'DONE: {n:,} rows deleted in {time.time()-t0:.0f}s',flush=True)
