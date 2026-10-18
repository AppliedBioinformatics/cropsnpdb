import sys, os, csv, glob, shutil, pymysql
sys.path.insert(0,'/var/www/html/cropsnpdb/snpdb/app'); import config
D='/var/www/html/cropsnpdb/snpdb/app/data'; ST=os.path.expanduser('~/snpdb_bulk_staging'); os.makedirs(ST,exist_ok=True)
csv.field_size_limit(10**9)
ren={'7022':'07022','7094':'07094','7016':'07016','7189':'07189','7191':'07191','7037':'07037','1111':'01111','1570':'01570','1188':'01188','2354':'02354','2359':'02359','2365':'02365','Zheshuan_g6':'Zheshuang_6'}
xu={'7022':'Xu83','7094':'Xu84','7016':'Xu85','7189':'Xu89','7191':'Xu90','7037':'Xu91','1111':'Xu98','1570':'Xu99','1188':'Xu101','2354':'Xu102','2359':'Xu103','2365':'Xu104','Zheshuan_g6':'Xu224'}
colmap={f'{o}__{xu[o]}':f'{n}__{xu[o]}' for o,n in ren.items()}
J30='Hong_Ye_Qing_Cai__J30'
c=pymysql.connect(host=config.MYSQL_DATABASE_HOST,user=config.MYSQL_DATABASE_USER,password=config.MYSQL_DATABASE_PASSWORD,db=config.MYSQL_DATABASE_DB)
cur=c.cursor()
cur.execute("SELECT s.SNPid, ahs.Genotype FROM Accession a JOIN Accession_has_SNP ahs ON ahs.Accession_idAccession=a.idAccession JOIN SNP s ON s.SNPTableid=ahs.SNP_SNPTableid WHERE a.Accession='J30'")
g30=dict(cur.fetchall()); print('J30 genotypes in DB',len(g30))
stats={'renamed':0,'j30_removed':0,'j30_added':0,'j30_check_mismatch':0,'j30_check_n':0}
for f in sorted(glob.glob(D+'/*.csv')):
    name=os.path.basename(f)
    with open(f,newline='') as fh: rows=list(csv.reader(fh))
    h=rows[0]; changed=False
    for i,col in enumerate(h):
        if col in colmap: h[i]=colmap[col]; stats['renamed']+=1; changed=True
    if J30 in h and name.startswith('Brassica_napus'):
        j=h.index(J30)
        for r in rows[1:]:
            stats['j30_check_n']+=1
            if r[j] not in ('?',) and g30.get(r[0],'?')!=r[j]: stats['j30_check_mismatch']+=1
        rows=[r[:j]+r[j+1:] for r in rows]; stats['j30_removed']+=1; changed=True
    if name.startswith('Brassica_rapa') and J30 not in rows[0]:
        h=rows[0]; meta=h.index('Probe_Sequence')+1
        samples=h[meta:]; pos=meta+sum(1 for s in samples if s.lower()<J30.lower())
        rows=[ (r[:pos]+[J30]+r[pos:]) if k==0 else (r[:pos]+[g30.get(r[0],'?')]+r[pos:]) for k,r in enumerate(rows)]
        stats['j30_added']+=1; changed=True
    if changed:
        with open(os.path.join(ST,name),'w',newline='') as fh: csv.writer(fh,lineterminator='\n').writerows(rows)
print(stats); print('staged files',len(os.listdir(ST)))
