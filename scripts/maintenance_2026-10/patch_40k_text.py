import sys
A=sys.argv[1]
def edit(path,pairs):
    s=open(path).read()
    for a,b in pairs:
        assert s.count(a)==1,(path,a[:60]); s=s.replace(a,b)
    open(path+".new","w").write(s); print("ok",path)
edit(A+"/templates/Home.html",[
 ("genotypes from the <i>Brassica</i> 60k and the wheat 90k Illumina arrays.</p>",
  "genotypes from the <i>Brassica</i> 60k, the wheat 90k and the Infinium Wheat Barley 40K Illumina arrays.</p>"),
 ('and 309 wheat lines from <a href = "https://triticeaetoolbox.org/wheat/">T3 Wheat</a>.<p>',
  'and 309 wheat lines from <a href = "https://triticeaetoolbox.org/wheat/">T3 Wheat</a>, plus 1,728 Australian Grains Genebank accessions of 1,205 released Australian wheat varieties genotyped with the Wheat Barley 40K array (<a href="https://doi.org/10.7910/DVN/MOBTA8">AGG Wheat Release 260619</a>).</p>'),
 ('<a href ="https://urgi.versailles.inrae.fr/download/iwgsc/IWGSC_RefSeq_Assemblies/v1.0/">RefSeq v1</a></li>',
  '<a href ="https://urgi.versailles.inrae.fr/download/iwgsc/IWGSC_RefSeq_Assemblies/v1.0/">RefSeq v1</a>, <a href="https://www.ncbi.nlm.nih.gov/datasets/genome/GCF_018294505.1/">RefSeq v2.1</a> (40K array)</li>'),
])
edit(A+"/templates/Lines.html",[
 ("and T3/Wheat. Field phenotypes are",
  "and T3/Wheat; passport data for the wheat 40K accessions were obtained from Genesys. Field phenotypes are"),
 ("</p>\n		<p><a class=\"btn btn-default\" href=\"/lines.csv\">",
  "</p>\n		<p style=\"font-size:12px\">Plant genetic resources accession level data provided by: Australian Grains Genebank (AUS165), Horsham, Australia. All intellectual property rights (including copyright) in the Data are owned and retained by the said institution. Data accessed through GENESYS Global Portal on Plant Genetic Resources, <a href=\"http://www.genesys-pgr.org\">http://www.genesys-pgr.org</a>, 2026-10-26. Genotypes: Australian Grains Genebank (2026) AGG Wheat &ndash; Release 260619, Harvard Dataverse, <a href=\"https://doi.org/10.7910/DVN/MOBTA8\">doi:10.7910/DVN/MOBTA8</a> (CC BY 4.0).</p>\n		<p><a class=\"btn btn-default\" href=\"/lines.csv\">"),
])
edit(A+"/templates/Download.html",[
 ("<p>Download genotype matrices for all canola and wheat samples in the database by chromosome.</p></br>",
  "<p>Download genotype matrices for all canola and wheat samples in the database by chromosome.</p>\n		<p>Wheat Barley 40K genotypes for all 32,656 Australian Grains Genebank wheat accessions (VCF, IWGSC RefSeq v2.1) are available from <a href=\"https://doi.org/10.7910/DVN/MOBTA8\">AGG Wheat &ndash; Release 260619</a>; CropSNPdb hosts the 1,728 accessions of released Australian varieties for searching.</p></br>"),
])
