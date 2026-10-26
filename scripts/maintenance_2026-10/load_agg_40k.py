"""Load AGG Wheat Release 260619 pilot (Australian released cultivars) into CropSNPdb.
Usage: load_agg_40k.py meta|genotypes|status"""
import sys, csv, gzip, time, pymysql
sys.path.insert(0,'/var/www/html/cropsnpdb/snpdb/app'); import config
D='/data/cropsnpdb/agg'; VCF=D+'/v2.1_raw_unique.vcf.gz'
ARRAY_ID, ARRAY='3','WheatBarley40K'; SP_ID, SP_NAME, BUILD=6,'Triticum aestivum RefSeq v2.1','RSv21'; REF_ID=6
MD_SRC='Genesys MCPD (Australian Grains Genebank AUS165), accessed 2026-10-26'
def conn(): return pymysql.connect(host=config.MYSQL_DATABASE_HOST,user=config.MYSQL_DATABASE_USER,password=config.MYSQL_DATABASE_PASSWORD,db=config.MYSQL_DATABASE_DB,charset='utf8mb4',autocommit=False)
samples=list(csv.DictReader(open(D+'/pilot_samples.tsv'),delimiter='\t'))
mode=sys.argv[1]
c=conn(); cur=c.cursor()
def q(s,a=None): cur.execute(s,a); return cur.fetchall()
if mode=='meta':
    # DDL first (auto-commits): region index for faster searches
    if not q("SHOW INDEX FROM SNP_Coordinates WHERE Key_name='idx_region'"):
        cur.execute("CREATE INDEX idx_region ON SNP_Coordinates (Specie_idSpecie, Specie_Build, Chromosome(20), Coordinate)"); print('index created')
    assert not q("SELECT 1 FROM SNPArray WHERE idSNPArray=%s",(ARRAY_ID,)), 'array exists'
    cur.execute("INSERT INTO SNPArray (idSNPArray,SNPArrayName) VALUES (%s,%s)",(ARRAY_ID,ARRAY))
    cur.execute("INSERT INTO Specie (idSpecie,SpecieName,Specie_idSNPArray,Build) VALUES (%s,%s,%s,%s)",(SP_ID,SP_NAME,ARRAY_ID,BUILD))
    cur.execute("INSERT INTO Reference VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",(REF_ID,'Australian Grains Genebank','AGG Wheat - Release 260619 (Infinium Wheat Barley 40K v1.1)',2026,'Harvard Dataverse','3','NA','10.7910/DVN/MOBTA8'))
    existing=dict(q("SELECT SNPid,SNPTableid FROM SNP")); new=reused=0; coords=[]
    with gzip.open(VCF,'rt') as f:
        for line in f:
            if line[0]=='#': continue
            ch,pos,sid,ref,alt=line.split('\t',5)[:5]
            if sid not in existing:
                cur.execute("INSERT INTO SNP (SNPid,Reference,Strand,SNPArray_idSNPArray) VALUES (%s,%s,%s,%s)",(sid,f'[{ref}/{alt}]','NA',ARRAY_ID)); new+=1
            else: reused+=1
            coords.append((sid,'chr'+ch[3:] if ch.startswith('Chr') else ch,int(pos),SP_ID,BUILD))
    cur.executemany("INSERT INTO SNP_Coordinates (SNP_SNPid,Chromosome,Coordinate,Specie_idSpecie,Specie_Build) VALUES (%s,%s,%s,%s,%s)",coords)
    print('SNPs new',new,'reused',reused,'coords',len(coords))
    cult={}
    for s in samples:
        if s['Line'] not in cult:
            cur.execute("INSERT INTO Cultivar (CultivarName,Specie_idSpecie) VALUES (%s,%s)",(s['Line'][:45],SP_ID)); cult[s['Line']]=cur.lastrowid
        cur.execute("INSERT INTO Accession (Accession,Cultivar_idCultivar,Accession_RefID) VALUES (%s,%s,%s)",(s['AGG_ID'],cult[s['Line']],REF_ID)); aid=cur.lastrowid
        cur.execute("""INSERT INTO AccessionMetadata (Accession_idAccession,Country,BiologicalStatus,Pedigree,AGG_ID,SNPConfirmedSpecies,ExternalURL,MetadataSource)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",(aid,s['Country'],s['Status'],s['Pedigree'] or None,s['AGG_ID'],s['Species'],'https://doi.org/'+s['DOI'],MD_SRC))
    print('cultivars',len(cult),'accessions',len(samples))
    c.commit(); print('META COMMITTED')
elif mode=='genotypes':
    acc=dict(q("SELECT Accession,idAccession FROM Accession WHERE Accession_RefID=%s",(REF_ID,)))
    sid2tid=dict(q("SELECT SNPid,SNPTableid FROM SNP"))
    done=q("SELECT COUNT(*) FROM Accession_has_SNP h JOIN Accession a ON a.idAccession=h.Accession_idAccession WHERE a.Accession_RefID=%s",(REF_ID,))[0][0]
    assert done==0, f'genotypes already present ({done}); clean up first'
    want={s['SampleID']:acc[s['AGG_ID']] for s in samples}
    t0=time.time(); batch=[]; n=0; m=0
    with gzip.open(VCF,'rt') as f:
        for line in f:
            if line.startswith('##'): continue
            parts=line.rstrip('\n').split('\t')
            if line.startswith('#CHROM'):
                cols=[(i,want[x]) for i,x in enumerate(parts) if x in want]; print('sample columns found',len(cols),'of',len(want),flush=True); continue
            ref,alt=parts[3],parts[4]; al=[ref]+alt.split(','); tid=sid2tid[parts[2]]; m+=1
            for i,aid in cols:
                gt=parts[i].split(':',1)[0].replace('|','/')
                if '.' in gt: g='NC'
                else:
                    a,b=gt.split('/'); g=al[int(a)]+al[int(b)]
                batch.append((aid,tid,g))
            if len(batch)>=50000:
                cur.executemany("INSERT INTO Accession_has_SNP (Accession_idAccession,SNP_SNPTableid,Genotype) VALUES (%s,%s,%s)",batch); n+=len(batch); batch=[]
                if n % 1000000 < 50000: c.commit(); print(f'{n:,} calls, {m:,} markers, {time.time()-t0:.0f}s',flush=True)
    if batch: cur.executemany("INSERT INTO Accession_has_SNP (Accession_idAccession,SNP_SNPTableid,Genotype) VALUES (%s,%s,%s)",batch); n+=len(batch)
    c.commit(); print(f'GENOTYPES DONE: {n:,} calls, {m:,} markers, {time.time()-t0:.0f}s',flush=True)
elif mode=='status':
    print(q("SELECT COUNT(*) FROM Accession WHERE Accession_RefID=%s",(REF_ID,)), q("SELECT COUNT(*) FROM Accession_has_SNP h JOIN Accession a ON a.idAccession=h.Accession_idAccession WHERE a.Accession_RefID=%s",(REF_ID,)))
