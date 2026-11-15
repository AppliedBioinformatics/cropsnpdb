#!/bin/bash
# Download barley MorexV3 chromosomes (Ensembl Plants) and index; contigs renamed chr1H..chr7H.
set -e
mkdir -p /data/cropsnpdb/barley/morexv3; cd /data/cropsnpdb/barley/morexv3
B=https://ftp.ebi.ac.uk/ensemblgenomes/pub/plants/current/fasta/hordeum_vulgare/dna
echo 1H 2H 3H 4H 5H 6H 7H | tr ' ' '\n' | xargs -P 4 -I{} bash -c "f=Hordeum_vulgare.MorexV3_pseudomolecules_assembly.dna.primary_assembly.{}.fa; [ -s \$f ] || (curl -s --retry 5 -m 3600 -o \$f.gz $B/\$f.gz && gunzip -f \$f.gz && echo \$(date +%T) {} done)"
for c in 1H 2H 3H 4H 5H 6H 7H; do sed "1s/^>.*/>chr$c/" Hordeum_vulgare.MorexV3_pseudomolecules_assembly.dna.primary_assembly.$c.fa; done > morexv3.fa
rm Hordeum_vulgare.*.fa
/var/www/html/cropsnpdb/snpdb/venv/bin/python3 -c "import pysam; pysam.faidx('morexv3.fa')"
echo "$(date +%T) ALL DONE"; ls -lh
