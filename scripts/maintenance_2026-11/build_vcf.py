"""CAIGE 40K (CSIRO DAP csiro:65245, IWGSC v2.0 calls) -> VCF on the AGG RefSeq v2.1 marker set, AGG REF/ALT orientation.
Markers not in the AGG VCF are dropped; replicate 2 samples are dropped; samples renamed CAIGE_<GID>."""
import pysam, csv, collections, random
D = "/data/cropsnpdb/caige"; AGG = "/data/cropsnpdb/agg/v2.1_raw_unique.vcf.gz"
OUT = D + "/caige_40k_v2.1.vcf.gz"
comp = str.maketrans("ACGT", "TGCA")
agg = pysam.VariantFile(AGG)
A = {r.id: (r.chrom, r.pos, r.ref, r.alts[0]) for r in agg.fetch()}
order = {c: i for i, c in enumerate(agg.header.contigs)}
meta = list(csv.DictReader(open(D + "/sample_details.tsv"), delimiter="\t"))
keep = {m["AVR Sample ID"]: m for m in meta if m["Sample Type"] != "Replicate 2"}
rep = {m["Supplied Sample GID"]: m["AVR Sample ID"] for m in meta if m["Sample Type"] == "Replicate 2"}
v = pysam.VariantFile(D + "/240430_AVR-00123_Raw_IWGSC-v2.0_FINAL.vcf.gz")
samples = [s for s in v.header.samples if s in keep]
assert len(samples) == 376, len(samples)
names = ["CAIGE_" + keep[s]["Supplied Sample GID"] for s in samples]
st = collections.Counter(); recs = []; repcmp = collections.Counter(); seen = set()
def letters(r, s, flip):
    gt = r.samples[s]["GT"]
    if gt is None or None in gt: return None
    a = [r.alleles[i] for i in gt]
    return [x.translate(comp) for x in a] if flip else a
for r in v:
    a = A.get(r.id)
    if not a: st["not_in_agg"] += 1; continue
    if r.id in seen: st["dup_id"] += 1; continue
    seen.add(r.id)
    alt = r.alts[0] if r.alts else None
    flip = {r.ref, alt} != {a[2], a[3]}
    if flip and {r.ref.translate(comp), (alt or "").translate(comp)} != {a[2], a[3]}:
        st["allele_mismatch_dropped"] += 1; continue
    idx = {a[2]: 0, a[3]: 1}
    gts = []
    for s in samples:
        L = letters(r, s, flip)
        gts.append(None if L is None or any(x not in idx for x in L) else tuple(sorted(idx[x] for x in L)))
    for gid, s2 in rep.items():
        s1 = next(x for x in samples if keep[x]["Supplied Sample GID"] == gid)
        g1, g2 = letters(r, s1, False), letters(r, s2, False)
        if g1 and g2: repcmp["same" if sorted(g1) == sorted(g2) else "diff"] += 1
    st["kept_flipped" if flip else "kept"] += 1
    if (r.ref, alt) == (a[3], a[2]) or (flip and (r.ref.translate(comp), (alt or "").translate(comp)) == (a[3], a[2])): st["ref_alt_swapped"] += 1
    recs.append((order[a[0]], a[1], r.id, a, gts))
recs.sort()
h = pysam.VariantHeader()
for c in agg.header.contigs.values(): h.contigs.add(c.name, length=c.length)
h.add_line("##FORMAT=<ID=GT,Number=1,Type=String,Description=\"Genotype\">")
h.add_line("##source=CAIGE 40K genotypes, CSIRO Data Access Portal csiro:65245 doi:10.25919/3x88-4p26 (CC BY 4.0); Fradgley et al. 2025 TAG 138:241 doi:10.1007/s00122-025-05023-6; positions and REF/ALT from AGG RefSeq v2.1 VCF")
for n in names: h.add_sample(n)
o = pysam.VariantFile(OUT, "wz", header=h)
calls = collections.Counter()
for _, pos, mid, a, gts in recs:
    rec = o.new_record(contig=a[0], start=pos - 1, alleles=(a[2], a[3]), id=mid)
    for n, g in zip(names, gts):
        rec.samples[n]["GT"] = g if g else (None, None); calls["called" if g else "missing"] += 1
        if g: calls["het" if g[0] != g[1] else "hom"] += 1
    o.write(rec)
o.close(); pysam.tabix_index(OUT, preset="vcf", force=True, csi=True)
# orientation check: alt allele frequency CAIGE vs 2000 random AGG samples
agg = pysam.VariantFile(AGG); random.seed(1); sub = random.sample(list(agg.header.samples), 2000); agg.subset_samples(sub)
af = {}
for r in agg.fetch():
    n = x = 0
    for s in r.samples.values():
        g = s["GT"]
        if g and None not in g: n += 2; x += sum(g)
    if n: af[r.id] = x / n
cv = pysam.VariantFile(OUT); diffs = []
for r in cv:
    n = x = 0
    for s in r.samples.values():
        g = s["GT"]
        if g and None not in g: n += 2; x += sum(g)
    if n and r.id in af: diffs.append((r.id, x / n, af[r.id]))
import statistics
xs, ys = [d[1] for d in diffs], [d[2] for d in diffs]
print("markers", dict(st), "\nsamples", len(names), "calls", dict(calls), "\nreplicate concordance", dict(repcmp))
print("AF correlation CAIGE vs AGG", round(statistics.correlation(xs, ys), 3), "markers with |dAF|>0.6:", sum(abs(a - b) > 0.6 for _, a, b in diffs))
print("examples |dAF|>0.6", [(i, round(a, 2), round(b, 2)) for i, a, b in diffs if abs(a - b) > 0.6][:10])
print("unique cultivar names", len({keep[s]["QnoQcode"] for s in samples}), "GIDs", len({keep[s]["Supplied Sample GID"] for s in samples}))
