import sys
A=sys.argv[1]
p=A+"/views.py"; s=open(p).read()
old='''	cur.execute("SELECT a.Accession, c.CultivarName, p.Trial, p.Trait, p.Value, p.Source FROM AccessionPhenotype p JOIN Accession a ON a.idAccession=p.Accession_idAccession JOIN Cultivar c ON c.idCultivar=a.Cultivar_idCultivar ORDER BY a.idAccession, p.Trial, p.Trait")
	rows = getResult(cur, con)
	buf = io.StringIO(); w = csv.writer(buf)
	w.writerow(['Accession','Line','Trial','Trait','Value','Source']); w.writerows(rows)'''
new='''	cur.execute("SELECT a.Accession, c.CultivarName, p.Trial, p.Location, p.Trait, p.Value, p.NPlots, p.Source FROM AccessionPhenotype p JOIN Accession a ON a.idAccession=p.Accession_idAccession JOIN Cultivar c ON c.idCultivar=a.Cultivar_idCultivar ORDER BY a.idAccession, p.Trial, p.Trait")
	rows = getResult(cur, con)
	buf = io.StringIO(); w = csv.writer(buf)
	w.writerow(['Accession','Line','Trial','Location','Trait','Value','NPlots','Source']); w.writerows(rows)'''
assert s.count(old)==1; s=s.replace(old,new)
s=s.replace('filename=CropSNPdb_AGG_field_phenotypes.csv','filename=CropSNPdb_field_phenotypes.csv')
open(p+".new","w").write(s)
p=A+"/templates/Lines.html"; s=open(p).read()
s=s.replace('Genebank field phenotypes (CSV)','Field phenotypes (CSV)')
old='Field phenotypes (2009&ndash;2012) are available for 118 Australian Grains Genebank accessions.'
new='Field phenotypes are available for 102 Australian Grains Genebank <i>Brassica</i> accessions (2009&ndash;2012) and 295 wheat lines (T3/Wheat trial means: yield, heading, height, test weight, Fusarium head blight and more).'
assert old in s; s=s.replace(old,new)
open(p+".new","w").write(s)
print("ok")
