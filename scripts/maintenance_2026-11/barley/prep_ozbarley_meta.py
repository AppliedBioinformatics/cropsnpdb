"""OzBarley xlsx -> TSVs for the CropSNPdb loader (system python3 + openpyxl).
meta.tsv: OzB code, MCPD fields; pheno.tsv: OzB code, trial, trait, value."""
import openpyxl, csv, collections, statistics
D='/data/cropsnpdb/barley/ozbarley'
SAMP={'100':'Wild','110':'Natural','200':'Weedy','300':'Traditional cultivar/landrace','400':'Breeding/research material',
      '410':"Breeder's line",'411':'Synthetic population','412':'Hybrid','413':'Founder stock/base population','414':'Inbred line',
      '415':'Segregating population','416':'Clonal selection','420':'Genetic stock','421':'Mutant','422':'Cytogenetic stock',
      '423':'Other genetic stock','500':'Advanced or improved cultivar','600':'GMO','999':'Other'}
rows=list(openpyxl.load_workbook(f'{D}/OzBarley_Multi-Crop_Passport_Descriptors.xlsx',read_only=True)['OzBarley MCPD'].iter_rows(values_only=True))
h=rows[0]; recs=collections.defaultdict(dict)
for r in rows[1:]:
    d={k:(str(v).strip() if v not in (None,'NULL','N/A') else '') for k,v in zip(h,r)}
    m=recs[d['COLLNUMB']]
    for k,v in d.items():
        if v and not m.get(k): m[k]=v
with open(f'{D}/meta.tsv','w') as fh:
    w=csv.writer(fh,delimiter='\t',lineterminator='\n')
    w.writerow(['code','name','country','status','pedigree','agg_id','breeder','subtaxa','donor','instcode','remarks','othernumb'])
    for code,m in recs.items():
        agg=m.get('ACCENAME','') if m.get('ACCENAME','').startswith('AGG') else m.get('DONORNUMB','')
        w.writerow([code,m.get('ACCENUMB',''),m.get('ORIGCTY',''),SAMP.get(m.get('SAMPSTAT',''),m.get('SAMPSTAT','')),m.get('ANCEST',''),
                    agg if agg.startswith('AGG') else '',m.get('BREDNAME') or m.get('BREDCODE',''),m.get('SUBTAXA',''),m.get('DONORCODE',''),
                    m.get('INSTCODE',''),m.get('REMARKS',''),m.get('OTHERNUMB','')])
print('MCPD lines',len(recs))
out=[]; TR='OzBarley APPN greenhouse (BLUEs)'
wb=openpyxl.load_workbook(f'{D}/OzBarley_imaging_tiller_data_BLUES.xlsx',read_only=True)
def terms(sheet):
    t={}
    for r in list(wb[sheet].iter_rows(values_only=True))[1:]:
        if r[1]: t[str(r[1])]=(str(r[0]),str(r[5] or ''))
    return t
for sheet,tsheet in [('BLUEs imaging','Trait terms imaging'),('BLUEs per tiller','Trait terms tillers')]:
    t=terms(tsheet); rows=list(wb[sheet].iter_rows(values_only=True)); h=rows[0]
    for r in rows[1:]:
        if r[0] is None: continue
        code='OzB_%03d'%int(r[0])
        for k,v in zip(h[2:],r[2:]):
            if v is None or not str(k).endswith('.BLUE'): continue
            short=str(k)[:-5]; long,unit=t.get(str(k),t.get(short,(short,'')))
            out.append((code,TR,(long.replace('_',' ')+(f" ({unit})" if unit and unit!='None' else ''))[:100],round(float(v),4)))
wb=openpyxl.load_workbook(f'{D}/OzBarley_X-ray_raw_data.xlsx',read_only=True)
agg=collections.defaultdict(list)
for sheet,cols in [('raw data spikes',{'SeedCount_Spike':'Seeds per spike','EstimatedSeedWeight_Spike':'Seed weight per spike (g)','SpikeLength':'Spike length (mm)'}),
                   ('raw seed data',{'SeedSphericalRatio':'Seed spherical ratio','SeedLength':'Seed length (mm)','EstimatedSeedWeight':'Seed weight (g)','SeedSurfaceArea':'Seed surface area (mm2)','SeedVolume':'Seed volume (mm3)'})]:
    rows=list(wb[sheet].iter_rows(values_only=True)); h=[str(x) for x in rows[0]]
    for r in rows[1:]:
        d=dict(zip(h,r))
        if d.get('OzBarleyID') is None: continue
        for c,lab in cols.items():
            k=[x for x in h if x.startswith(c)]
            if k and d[k[0]] not in (None,''): agg[('OzB_%03d'%int(d['OzBarleyID']),'X-ray CT: '+lab+' (line mean)')].append(float(d[k[0]]))
for (code,trait),v in agg.items(): out.append((code,'OzBarley X-ray CT spikes',trait,round(statistics.mean(v),4)))
with open(f'{D}/pheno.tsv','w') as fh:
    w=csv.writer(fh,delimiter='\t',lineterminator='\n'); w.writerow(['code','trial','trait','value']); w.writerows(out)
print('phenotype values',len(out),'traits',len({o[2] for o in out}),'lines',len({o[0] for o in out}))
