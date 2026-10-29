"""Register all AGG Wheat Release 260619 accessions (32,656) for the VCF-backed WheatBarley40K species.
Lines, accessions, passport metadata (Genesys MCPD) and VCF sample mapping go into MySQL; genotypes stay in the VCF.
Usage: load_agg_full_meta.py dryrun|commit"""
import sys, csv, pymysql
sys.path.insert(0,'/var/www/html/cropsnpdb/snpdb/app'); import config
D='/data/cropsnpdb/agg'; VCF=D+'/v2.1_raw_unique.vcf.gz'; SP_ID=6; REF_ID=6
SRC='Genesys MCPD (Australian Grains Genebank AUS165), accessed 2026-10-26'
CTY={'AFG':'Afghanistan','AGO':'Angola','ALB':'Albania','ARG':'Argentina','ARM':'Armenia','AUS':'Australia','AUT':'Austria','AZE':'Azerbaijan','BEL':'Belgium','BGD':'Bangladesh','BGR':'Bulgaria','BIH':'Bosnia and Herzegovina','BLR':'Belarus','BOL':'Bolivia','BRA':'Brazil','BTN':'Bhutan','CAN':'Canada','CHE':'Switzerland','CHL':'Chile','CHN':'China','CMR':'Cameroon','COL':'Colombia','CSK':'Czechoslovakia (former)','CYP':'Cyprus','CZE':'Czechia','DEU':'Germany','DNK':'Denmark','DZA':'Algeria','ECU':'Ecuador','EGY':'Egypt','ERI':'Eritrea','ESP':'Spain','EST':'Estonia','ETH':'Ethiopia','FIN':'Finland','FRA':'France','GBR':'United Kingdom','GEO':'Georgia','GRC':'Greece','GTM':'Guatemala','GUF':'French Guiana','HND':'Honduras','HRV':'Croatia','HUN':'Hungary','IDN':'Indonesia','IND':'India','IRN':'Iran','IRQ':'Iraq','ISR':'Israel','ITA':'Italy','JOR':'Jordan','JPN':'Japan','KAZ':'Kazakhstan','KEN':'Kenya','KGZ':'Kyrgyzstan','KOR':'South Korea','LBN':'Lebanon','LBR':'Liberia','LBY':'Libya','LVA':'Latvia','MAR':'Morocco','MDA':'Moldova','MEX':'Mexico','MKD':'North Macedonia','MLT':'Malta','MMR':'Myanmar','MNE':'Montenegro','MNG':'Mongolia','MOZ':'Mozambique','MWI':'Malawi','NLD':'Netherlands','NOR':'Norway','NPL':'Nepal','NZL':'New Zealand','OMN':'Oman','PAK':'Pakistan','PER':'Peru','PHL':'Philippines','POL':'Poland','PRT':'Portugal','PRY':'Paraguay','PSE':'Palestine','REU':'Réunion','ROM':'Romania','ROU':'Romania','RUS':'Russia','SAU':'Saudi Arabia','SDN':'Sudan','SRB':'Serbia','SUN':'USSR (former)','SVK':'Slovakia','SWE':'Sweden','SYR':'Syria','THA':'Thailand','TJK':'Tajikistan','TKM':'Turkmenistan','TUN':'Tunisia','TUR':'Türkiye','TWN':'Taiwan','TZA':'Tanzania','UKR':'Ukraine','URY':'Uruguay','USA':'United States','UZB':'Uzbekistan','VEN':'Venezuela','YEM':'Yemen','YUG':'Yugoslavia (former)','ZAF':'South Africa','ZAR':'Zaire (former; DR Congo)','ZWE':'Zimbabwe'}
SAMP={'100':'Wild','200':'Weedy','300':'Traditional cultivar/landrace','400':'Breeding/research material','410':"Breeder's line",'411':'Synthetic population','412':'Hybrid','413':'Founder stock/base population','414':'Inbred line','415':'Segregating population','416':'Clonal selection','420':'Genetic stock','421':'Mutant','422':'Cytogenetic stock','423':'Other genetic stock','500':'Advanced/improved cultivar','600':'GMO','999':'Other'}
def n(x): x=(x or '').strip(); return x or None
mc={r['DOI']:r for r in csv.DictReader(open(D+'/agg_wheat_mcpd.tsv'),delimiter='\t')}
bs=list(csv.DictReader(open(D+'/biosample.tsv'),delimiter='\t'))
c=pymysql.connect(host=config.MYSQL_DATABASE_HOST,user=config.MYSQL_DATABASE_USER,password=config.MYSQL_DATABASE_PASSWORD,db=config.MYSQL_DATABASE_DB,charset='utf8mb4',autocommit=False)
cur=c.cursor()
def q(s,a=None): cur.execute(s,a); return cur.fetchall()
# --- schema (DDL auto-commits; idempotent) ---
if q("SELECT CHARACTER_MAXIMUM_LENGTH FROM information_schema.COLUMNS WHERE TABLE_SCHEMA='snpdb' AND TABLE_NAME='Cultivar' AND COLUMN_NAME='CultivarName'")[0][0] < 150:
    cur.execute("ALTER TABLE Cultivar MODIFY CultivarName VARCHAR(150) NOT NULL")
cur.execute("""CREATE TABLE IF NOT EXISTS AccessionVcfSample (Accession_idAccession INT NOT NULL PRIMARY KEY, SampleID VARCHAR(64) NOT NULL, VcfPath VARCHAR(255) NOT NULL,
  CONSTRAINT fk_AccVcf_Accession FOREIGN KEY (Accession_idAccession) REFERENCES Accession(idAccession)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")
c.commit()
# --- data (one transaction) ---
cult={name:cid for cid,name in q("SELECT idCultivar,CultivarName FROM Cultivar WHERE Specie_idSpecie=%s",(SP_ID,))}
accs=dict(q("SELECT Accession,idAccession FROM Accession WHERE Accession_RefID=%s",(REF_ID,)))
new_c=new_a=0; nometa=0; stat={}
for b in bs:
    p=mc.get(b['material source DOI'].replace('https://doi.org/',''))
    agg=b['accession name']
    name=(n(p['ACCENAME']) if p else None) or agg
    name=name.split(';')[0].strip()[:150]
    if name not in cult:
        cur.execute("INSERT INTO Cultivar (CultivarName,Specie_idSpecie) VALUES (%s,%s)",(name,SP_ID)); cult[name]=cur.lastrowid; new_c+=1
    if agg not in accs:
        cur.execute("INSERT INTO Accession (Accession,Cultivar_idCultivar,Accession_RefID) VALUES (%s,%s,%s)",(agg,cult[name],REF_ID)); accs[agg]=cur.lastrowid; new_a+=1
    aid=accs[agg]
    if p:
        sc=str(int(float(p['SAMPSTAT']))) if n(p['SAMPSTAT']) else None; st=SAMP.get(sc,sc)
        stat[st]=stat.get(st,0)+1
        cur.execute("""REPLACE INTO AccessionMetadata (Accession_idAccession,Country,BiologicalStatus,Pedigree,AGG_ID,SuppliedSpecies,Donor,ExternalURL,MetadataSource)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",(aid,CTY.get(p['ORIGCTY'],n(p['ORIGCTY'])),st,n(p['ANCEST']),agg,n(p['GRIN_NAME']),n(p['DONORNAME']),'https://doi.org/'+p['DOI'],SRC))
    else:
        nometa+=1
        cur.execute("REPLACE INTO AccessionMetadata (Accession_idAccession,AGG_ID,MetadataSource) VALUES (%s,%s,%s)",(aid,agg,'AGG biosample sheet (no Genesys passport record)'))
    cur.execute("REPLACE INTO AccessionVcfSample VALUES (%s,%s,%s)",(aid,b['biological material ID'],VCF))
print('samples',len(bs),'new cultivars',new_c,'new accessions',new_a,'total cultivars',len(cult),'accessions',len(accs),'no passport',nometa)
print('status',sorted(stat.items(),key=lambda x:-x[1]))
print(q("SELECT COUNT(*) FROM AccessionVcfSample"), q("SELECT COUNT(*) FROM Accession WHERE Accession_RefID=%s",(REF_ID,)))
if sys.argv[1]=='commit': c.commit(); print('COMMITTED')
else: c.rollback(); print('DRY RUN - rolled back')
