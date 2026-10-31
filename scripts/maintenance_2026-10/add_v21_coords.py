# Add IWGSC RefSeq v2.1 coordinates for wheat 90K SNPs (SNP_Coordinates, species 2, build RSv21 - not used by
# searches, which use the species' own build RSv1) and write the public v1<->v2.1 table.
import sys, csv, pymysql
sys.path.insert(0,'/var/www/html/cropsnpdb/snpdb/app'); import config
W='/data/cropsnpdb/wheat90k'; comp=str.maketrans('ACGT','TGCA')
flip={'+':'-','-':'+'}
ori={r['SNPid']:r for r in csv.DictReader(open(f'{W}/wheat90k_reference_alleles.tsv'),delimiter='\t')}
rows=list(csv.DictReader(open(f'{W}/wheat90k_v21_positions.tsv'),delimiter='\t'))
out=open('/var/www/html/cropsnpdb/snpdb/app/data/Wheat90k_RefSeq_v2.1_positions.tsv','w')
out.write('SNPid\tChr_v21\tPos_v21\tChr_v1\tPos_v1\tStrand_v1_to_v21\tREF_v21\tALT_v21\tCallStrand_v21\n')
key=lambda r:(r['Chr_v21'],int(r['Pos_v21']),r['SNPid'])
for r in sorted(rows,key=key):
    o=ori.get(r['SNPid']); ref=alt=cs='NA'
    if o and o['CallStrand'] in ('+','-','ambiguous'):
        m=r['Strand_v1_to_v21']=='-'
        ref=o['REF'].translate(comp) if m else o['REF']; alt=o['ALT'].translate(comp) if m else o['ALT']
        cs=flip[o['CallStrand']] if m and o['CallStrand'] in flip else o['CallStrand']
    out.write(f"{r['SNPid']}\t{r['Chr_v21']}\t{r['Pos_v21']}\t{r['Chr_v1']}\t{r['Pos_v1']}\t{r['Strand_v1_to_v21']}\t{ref}\t{alt}\t{cs}\n")
out.close()
print('rows',len(rows))
if '--apply' not in sys.argv: sys.exit()
c=pymysql.connect(host=config.MYSQL_DATABASE_HOST,user=config.MYSQL_DATABASE_USER,password=config.MYSQL_DATABASE_PASSWORD,db=config.MYSQL_DATABASE_DB,autocommit=False)
cur=c.cursor()
n=cur.executemany("INSERT INTO SNP_Coordinates (SNP_SNPid,Chromosome,Coordinate,Specie_idSpecie,Specie_Build) VALUES (%s,%s,%s,2,'RSv21') ON DUPLICATE KEY UPDATE Chromosome=VALUES(Chromosome),Coordinate=VALUES(Coordinate)",[(r['SNPid'],r['Chr_v21'],int(r['Pos_v21'])) for r in rows])
c.commit(); print('DB rows', n)
cur.execute("select Specie_idSpecie,Specie_Build,count(*) from SNP_Coordinates group by 1,2"); print(cur.fetchall())
