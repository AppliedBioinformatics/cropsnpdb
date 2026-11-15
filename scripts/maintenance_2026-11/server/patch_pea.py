import os
os.chdir('/var/www/html/cropsnpdb/snpdb/app')
def rep(p,old,new,dest=None):
    s=open(p).read(); assert s.count(old)==1,(p,old[:60]); open(dest or p,"w").write(s.replace(old,new))
rep("ownLib/vcfBackend.py","'Cicer arietinum CDC Frontier v1'}","'Cicer arietinum CDC Frontier v1', 'Pisum sativum Cameor v2 PSPPC', 'Pisum sativum Cameor v2 AMS'}")
s=open("genoapi.py").read()
old="'cicer_wgs': 'Cicer arietinum CDC Frontier v1',"; assert s.count(old)==1
s=s.replace(old,old+" 'pea': 'Pisum sativum Cameor v2 PSPPC', 'pea_psppc': 'Pisum sativum Cameor v2 PSPPC', 'pea_ams': 'Pisum sativum Cameor v2 AMS',")
s=s.replace("chickpea/cicer_wgs (von Wettberg 2018 WGS, CDC Frontier v1).","chickpea/cicer_wgs (von Wettberg 2018 WGS, CDC Frontier v1), pea/pea_psppc (USDA PSPPC GBS, Cameor v2), pea_ams (AMS panel, Cameor v2).")
open("/tmp/genoapi.py","w").write(s); print("ok")
