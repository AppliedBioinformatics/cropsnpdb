import sys, csv, glob, os, shutil, collections, pymysql
sys.path.insert(0,'/var/www/html/cropsnpdb/snpdb/app'); import config
TSV='/data/cropsnpdb/wheat90k/wheat90k_reference_alleles.tsv'
DATA='/var/www/html/cropsnpdb/snpdb/app/data'
BK=os.path.expanduser('~/snpdb_backup_20261017/wheat90k_csv_orig')
apply='--apply' in sys.argv
comp=str.maketrans('ACGT','TGCA')
ori={}
for r in csv.DictReader(open(TSV),delimiter='\t'):
    if r['CallStrand'] in ('+','-','ambiguous'):
        ori[r['SNPid']]=(f"[{r['REF']}/{r['ALT']}]", r['CallStrand'], r['REF'])
print('oriented SNPs', len(ori))
# sanity: is the reference allele the major allele in the TCAP panel?
maj=collections.Counter()
files=sorted(glob.glob(f'{DATA}/Triticum_aestivum_RefSeq_v1_and_Pan_*.csv'))
out={}
for f in files:
    rows=list(csv.reader(open(f)))
    for row in rows[1:]:
        o=ori.get(row[0])
        if not o: continue
        row[4],row[5]=o[0],o[1]
        if o[1] in '+-':
            c=collections.Counter(a for g in row[8:] if len(g)==2 and 'N' not in g for a in g)
            if c:
                a=c.most_common(1)[0][0]
                if o[1]=='-': a=a.translate(comp)
                maj[(o[1],a==o[2])]+=1
    out[f]=rows
print(maj)
if not apply: sys.exit()
os.makedirs(BK,exist_ok=True)
for f,rows in out.items():
    if not os.path.exists(f'{BK}/{os.path.basename(f)}'): shutil.copy2(f,BK)
    tmp=f+'.tmp'
    with open(tmp,'w',newline='') as fh: csv.writer(fh,lineterminator='\n').writerows(rows)
    shutil.copymode(f,tmp); os.replace(tmp,f)
c=pymysql.connect(host=config.MYSQL_DATABASE_HOST,user=config.MYSQL_DATABASE_USER,password=config.MYSQL_DATABASE_PASSWORD,db=config.MYSQL_DATABASE_DB,autocommit=False)
cur=c.cursor()
n=cur.executemany("UPDATE SNP SET Reference=%s, Strand=%s WHERE SNPid=%s AND SNPArray_idSNPArray=2",[(v[0],v[1],k) for k,v in ori.items()])
c.commit(); print('DB rows updated', n)
