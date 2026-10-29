# Genotype queries served from bgzipped, indexed VCF files (added 2026-10-29).
# Used for large genebank datasets (AGG Wheat 40K) instead of one MySQL row per call.
import pysam
from mysqlQuerys import getCursor, getResult

VCF_SPECIES = {'Triticum aestivum RefSeq v2.1'}
MAX_CALLS = 3000000   # accessions x markers per search

def handles(species):
	return species in VCF_SPECIES

def _q(sql, args=None):
	cur, con = getCursor()
	cur.execute(sql, args)
	return getResult(cur, con)

def search(species, cultivars, chrom, start, end):
	start, end = int(start), int(end)
	rows = _q("""SELECT c.CultivarName, a.Accession, v.SampleID, v.VcfPath, r.DOI, arr.SNPArrayName, s.idSpecie, s.Build
		FROM Cultivar c JOIN Specie s ON s.idSpecie = c.Specie_idSpecie
		JOIN SNPArray arr ON arr.idSNPArray = s.Specie_idSNPArray
		JOIN Accession a ON a.Cultivar_idCultivar = c.idCultivar
		JOIN Reference r ON r.RefID = a.Accession_RefID
		JOIN AccessionVcfSample v ON v.Accession_idAccession = a.idAccession
		WHERE s.SpecieName = %s AND c.CultivarName IN %s""", (species, tuple(cultivars)))
	if not rows:
		return ()
	nmark = _q("""SELECT COUNT(*) FROM SNP_Coordinates WHERE Specie_idSpecie=%s AND Specie_Build=%s
		AND Chromosome=%s AND Coordinate BETWEEN %s AND %s""", (rows[0][6], rows[0][7], chrom, start, end))[0][0]
	if nmark == 0:
		return ()
	if nmark * len(rows) > MAX_CALLS:
		raise ValueError("Search too large: {:,} accessions x {:,} markers. Please select fewer lines or a smaller region (limit {:,} genotypes).".format(len(rows), nmark, MAX_CALLS))
	vchrom = 'Chr' + chrom[3:] if chrom.startswith('chr') else chrom
	by_vcf = {}
	for r in rows:
		by_vcf.setdefault(r[3], {})[r[2]] = r
	out = []
	for vcf, info in by_vcf.items():
		vf = pysam.VariantFile(vcf)
		present = [s for s in info if s in vf.header.samples]
		if not present:
			continue
		vf.subset_samples(present)
		for rec in vf.fetch(vchrom, start - 1, end):
			alleles = rec.alleles
			ref = '[{}/{}]'.format(rec.ref, ','.join(rec.alts or ()))
			for smp in present:
				gt = rec.samples[smp]['GT']
				if gt is None or None in gt:
					g = 'NC'
				else:
					g = alleles[gt[0]] + alleles[gt[1]]
				r = info[smp]
				out.append((r[5], species, r[0], r[1], rec.id, ref, 'NA', chrom, rec.pos, g, r[4]))
		vf.close()
	return out
