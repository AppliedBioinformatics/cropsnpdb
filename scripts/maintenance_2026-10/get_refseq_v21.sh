#!/bin/bash
# Download IWGSC RefSeq v2.1 chromosomes (Ensembl Plants, 4 in parallel) and index.
set -e
mkdir -p /data/cropsnpdb/refseq_v21; cd /data/cropsnpdb/refseq_v21
export B=https://ftp.ebi.ac.uk/ensemblgenomes/pub/plants/current/fasta/triticum_aestivum_refseqv2/dna
echo 1A 1B 1D 2A 2B 2D 3A 3B 3D 4A 4B 4D 5A 5B 5D 6A 6B 6D 7A 7B 7D | tr ' ' '\n' | xargs -P 4 -I{} bash -c '
  f=Triticum_aestivum_refseqv2.IWGSC_RefSeq_v2.1.dna.chromosome.{}.fa
  [ -s $f ] && exit 0
  curl -s --retry 5 -m 3600 -o $f.gz $B/$f.gz && gunzip -f $f.gz && echo "$(date +%T) {} done"'
for c in 1A 1B 1D 2A 2B 2D 3A 3B 3D 4A 4B 4D 5A 5B 5D 6A 6B 6D 7A 7B 7D; do cat Triticum_aestivum_refseqv2.IWGSC_RefSeq_v2.1.dna.chromosome.$c.fa; done > refseq_v21.fa
rm Triticum_aestivum_refseqv2.*.fa
/var/www/html/cropsnpdb/snpdb/venv/bin/python3 -c "import pysam; pysam.faidx('refseq_v21.fa')"
echo "$(date +%T) ALL DONE"; ls -lh
