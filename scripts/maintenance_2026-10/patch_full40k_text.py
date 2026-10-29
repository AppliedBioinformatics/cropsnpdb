import sys
A=sys.argv[1]
def edit(path,pairs):
    s=open(path).read()
    for a,b in pairs:
        assert s.count(a)==1,(path,a[:60]); s=s.replace(a,b)
    open(path+".new","w").write(s); print("ok",path)
edit(A+"/templates/Home.html",[
 ("plus 1,728 Australian Grains Genebank accessions of 1,205 released Australian wheat varieties genotyped with the Wheat Barley 40K array",
  "plus all 32,656 Australian Grains Genebank wheat accessions (landraces, cultivars, breeding lines and genetic stocks from 110 countries) genotyped with the Wheat Barley 40K array"),
])
edit(A+"/templates/Download.html",[
 ("; CropSNPdb hosts the 1,728 accessions of released Australian varieties for searching.</p>",
  "; all of these accessions can be searched in CropSNPdb.</p>"),
])
