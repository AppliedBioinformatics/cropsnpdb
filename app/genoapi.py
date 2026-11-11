"""Read-only JSON API for programmatic access (askWheat MCP tools, scripts).

/api/v1/datasets                      species/builds, arrays, line counts, markers per chromosome
/api/v1/lines?species=&q=             find lines (cultivar names) and their accessions
/api/v1/markers?species=&chrom=&start=&end=
/api/v1/genotypes?species=&chrom=&start=&end=&lines=a,b[&format=csv]
/api/v1/compare?species=&line_a=&line_b=&chrom=[&start=&end=]
/api/v1/haplotype?species=&line=&chrom=&start=&end=[&max_mismatch=0]
/api/v1/phenotypes?line=&trait=
species may be the full name or an alias: wheat40k (AGG, RefSeq v2.1), wheat90k (RefSeq v1).
"""
import csv
import io
from collections import defaultdict

from flask import Response, jsonify, request

from app import app
from dataHandeler import useInputToSearchv2
from mysqlQuerys import getCursor, getResult

ALIASES = {'wheat40k': 'Triticum aestivum RefSeq v2.1', 'agg': 'Triticum aestivum RefSeq v2.1',
           'wheat90k': 'Triticum aestivum RefSeq v1 and Pan'}
DEFAULT_SPECIES = 'Triticum aestivum RefSeq v2.1'
MAX_LIMIT = 1000


def _q(sql, args=None):
    cur, con = getCursor()
    cur.execute(sql, args)
    return getResult(cur, con)


def _json(payload, status=200):
    r = jsonify(payload)
    r.status_code = status
    r.headers['Access-Control-Allow-Origin'] = '*'
    return r


def _species():
    s = request.args.get('species', DEFAULT_SPECIES).strip()
    s = ALIASES.get(s.lower(), s)
    row = _q("SELECT idSpecie, Build FROM Specie WHERE SpecieName=%s", (s,))
    if not row:
        raise ValueError(f"unknown species {s!r}; see /api/v1/datasets")
    return s, row[0][0], row[0][1]


def _int(name, default=None):
    v = request.args.get(name)
    if v in (None, ''):
        if default is None:
            raise ValueError(f"{name} is required")
        return default
    return int(v)


def _chrom():
    c = request.args.get('chrom', '').strip()
    if not c:
        raise ValueError("chrom is required (e.g. chr1B or 1B)")
    return c if c.lower().startswith('chr') or not c[:1].isdigit() else 'chr' + c.upper()


def _resolve_lines(species, names):
    """Line names or accession IDs (case-insensitive) -> {CultivarName: [accessions]}."""
    out = defaultdict(list)
    for n in names:
        rows = _q("""SELECT c.CultivarName, a.Accession FROM Cultivar c JOIN Specie s ON s.idSpecie=c.Specie_idSpecie
                     JOIN Accession a ON a.Cultivar_idCultivar=c.idCultivar
                     WHERE s.SpecieName=%s AND (c.CultivarName=%s OR a.Accession=%s)""", (species, n, n))
        for line, acc in rows:
            if acc not in out[line]:
                out[line].append(acc)
    return dict(out)


def _calls(species, lines, chrom, start, end):
    """-> markers {id: (pos, alleles)}, calls {accession: {marker: genotype}}, accession -> line."""
    rows = useInputToSearchv2(species, list(lines), chrom, start, end) or ()
    markers, calls, line_of = {}, defaultdict(dict), {}
    for arr, sp, line, acc, snp, ref, strand, ch, pos, gt, doi in rows:
        markers[snp] = (int(pos), ref)
        calls[acc][snp] = gt
        line_of[acc] = line
    return markers, calls, line_of


def _err(e):
    return _json({'error': str(e)}, 400)


@app.route('/api/v1/datasets', methods=['GET'])
def api_datasets():
    rows = _q("""SELECT s.idSpecie, s.SpecieName, s.Build, arr.SNPArrayName,
                 (SELECT COUNT(*) FROM Cultivar c WHERE c.Specie_idSpecie=s.idSpecie)
                 FROM Specie s LEFT JOIN SNPArray arr ON arr.idSNPArray=s.Specie_idSNPArray""")
    chroms = defaultdict(dict)
    for sid, build, ch, n in _q("""SELECT Specie_idSpecie, Specie_Build, Chromosome, COUNT(*) FROM SNP_Coordinates
                                   GROUP BY Specie_idSpecie, Specie_Build, Chromosome"""):
        chroms[(sid, build)][ch] = n
    return _json({'datasets': [{'species': name, 'build': build, 'array': arr, 'lines': n,
                                'markers_per_chromosome': chroms.get((sid, build), {}),
                                'aliases': [k for k, v in ALIASES.items() if v == name]}
                               for sid, name, build, arr, n in rows],
                  'site': 'https://snpdb.appliedbioinformatics.com.au'})


@app.route('/api/v1/lines', methods=['GET'])
def api_lines_v1():
    try:
        species, _, _ = _species()
    except ValueError as e:
        return _err(e)
    q = request.args.get('q', '').strip()
    limit = min(int(request.args.get('limit', 50)), MAX_LIMIT)
    like = '%' + q.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_') + '%'
    rows = _q("""SELECT c.CultivarName, a.Accession, m.Country, m.BiologicalStatus, m.Pedigree,
                        m.BreedingOrganization, m.Donor
                 FROM Cultivar c JOIN Specie s ON s.idSpecie=c.Specie_idSpecie
                 JOIN Accession a ON a.Cultivar_idCultivar=c.idCultivar
                 LEFT JOIN AccessionMetadata m ON m.Accession_idAccession=a.idAccession
                 WHERE s.SpecieName=%s AND (c.CultivarName LIKE %s OR a.Accession LIKE %s)
                 ORDER BY (c.CultivarName=%s) DESC, c.CultivarName LIMIT %s""", (species, like, like, q, limit))
    return _json({'species': species, 'n': len(rows), 'lines': [
        {'line': r[0], 'accession': r[1], 'country': r[2], 'status': r[3], 'pedigree': r[4],
         'breeding_organization': r[5], 'donor': r[6]} for r in rows]})


@app.route('/api/v1/markers', methods=['GET'])
def api_markers():
    try:
        species, sid, build = _species()
        chrom, start, end = _chrom(), _int('start', 0), _int('end', 1_000_000_000)
    except ValueError as e:
        return _err(e)
    limit = min(int(request.args.get('limit', 200)), 5000)
    n = _q("""SELECT COUNT(*) FROM SNP_Coordinates WHERE Specie_idSpecie=%s AND Specie_Build=%s AND Chromosome=%s
              AND Coordinate BETWEEN %s AND %s""", (sid, build, chrom, start, end))[0][0]
    rows = _q("""SELECT SNP_SNPid, Coordinate FROM SNP_Coordinates WHERE Specie_idSpecie=%s AND Specie_Build=%s
                 AND Chromosome=%s AND Coordinate BETWEEN %s AND %s ORDER BY Coordinate LIMIT %s""",
              (sid, build, chrom, start, end, limit))
    return _json({'species': species, 'build': build, 'chrom': chrom, 'start': start, 'end': end, 'n': n,
                  'markers': [{'id': r[0], 'pos': r[1]} for r in rows]})


@app.route('/api/v1/genotypes', methods=['GET'])
def api_genotypes():
    try:
        species, _, build = _species()
        chrom, start, end = _chrom(), _int('start'), _int('end')
        names = [x.strip() for x in request.args.get('lines', '').split(',') if x.strip()][:500]
        if not names:
            raise ValueError("lines is required (comma-separated line names or accession IDs)")
        resolved = _resolve_lines(species, names)
        if not resolved:
            raise ValueError("none of the lines were found; see /api/v1/lines")
        markers, calls, line_of = _calls(species, resolved, chrom, start, end)
    except ValueError as e:
        return _err(e)
    wanted = set()
    for n in names:
        for line, line_accs in resolved.items():
            if n.lower() == line.lower():
                wanted.update(line_accs)
            elif n in line_accs:
                wanted.add(n)
    accs = [a for a in calls if a in wanted]
    order = sorted(markers, key=lambda m: markers[m][0])
    if request.args.get('format') == 'csv':
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(['marker', 'chrom', 'pos', 'alleles'] + [f"{line_of[a]} ({a})" for a in accs])
        for m in order:
            w.writerow([m, chrom, markers[m][0], markers[m][1]] + [calls[a].get(m, '') for a in accs])
        return Response(buf.getvalue(), mimetype='text/csv', headers={
            'Content-Disposition': f'attachment; filename=CropSNPdb_{chrom}_{start}-{end}.csv',
            'Access-Control-Allow-Origin': '*'})
    return _json({'species': species, 'build': build, 'chrom': chrom, 'start': start, 'end': end,
                  'not_found': [n for n in names if not any(n.lower() == l.lower() or n in a for l, a in resolved.items())],
                  'markers': [{'id': m, 'pos': markers[m][0], 'alleles': markers[m][1]} for m in order],
                  'accessions': [{'accession': a, 'line': line_of[a],
                                  'genotypes': [calls[a].get(m, '') for m in order]} for a in accs],
                  'csv': request.url + '&format=csv'})


def _segments(diff_positions, min_markers=3, max_gap=5_000_000):
    """Collapse differing marker positions into regions."""
    segs, cur = [], []
    for p in diff_positions:
        if cur and p - cur[-1] > max_gap:
            if len(cur) >= min_markers:
                segs.append({'start': cur[0], 'end': cur[-1], 'differing_markers': len(cur)})
            cur = []
        cur.append(p)
    if len(cur) >= min_markers:
        segs.append({'start': cur[0], 'end': cur[-1], 'differing_markers': len(cur)})
    return segs


@app.route('/api/v1/compare', methods=['GET'])
def api_compare():
    try:
        species, _, build = _species()
        chrom, start, end = _chrom(), _int('start', 1), _int('end', 1_000_000_000)
        a_name, b_name = request.args.get('line_a', '').strip(), request.args.get('line_b', '').strip()
        res = _resolve_lines(species, [a_name, b_name])
        acc = {}
        for side, name in (('a', a_name), ('b', b_name)):
            hits = [(l, x) for l, xs in res.items() for x in xs if name in (l, x) or name.lower() == l.lower()]
            if not hits:
                raise ValueError(f"line {name!r} not found; see /api/v1/lines")
            acc[side] = hits
        markers, calls, line_of = _calls(species, {acc['a'][0][0], acc['b'][0][0]}, chrom, start, end)
    except ValueError as e:
        return _err(e)
    a, b = acc['a'][0][1], acc['b'][0][1]
    same = diff = missing = 0
    diff_pos = []
    for m, (pos, _) in sorted(markers.items(), key=lambda kv: kv[1][0]):
        ga, gb = calls[a].get(m), calls[b].get(m)
        if not ga or not gb or ga == 'NC' or gb == 'NC':
            missing += 1
        elif ga == gb:
            same += 1
        else:
            diff += 1
            diff_pos.append(pos)
    compared = same + diff
    return _json({'species': species, 'build': build, 'chrom': chrom, 'start': start,
                  'end': end if end < 1_000_000_000 else None,
                  'line_a': {'line': acc['a'][0][0], 'accession': a, 'other_accessions': [x for _, x in acc['a'][1:]]},
                  'line_b': {'line': acc['b'][0][0], 'accession': b, 'other_accessions': [x for _, x in acc['b'][1:]]},
                  'markers': len(markers), 'compared': compared, 'identical': same, 'different': diff,
                  'missing_or_no_call': missing, 'identity': round(same / compared, 4) if compared else None,
                  'differing_regions': _segments(diff_pos)})


@app.route('/api/v1/haplotype', methods=['GET'])
def api_haplotype():
    """Lines whose genotypes in a region match a reference line (no-calls ignored)."""
    try:
        species, sid, build = _species()
        chrom, start, end = _chrom(), _int('start'), _int('end')
        if end - start > 5_000_000:
            raise ValueError("region must be at most 5 Mb")
        ref_name = request.args.get('line', '').strip()
        max_mm = int(request.args.get('max_mismatch', 0))
        ref = _resolve_lines(species, [ref_name])
        if not ref:
            raise ValueError(f"line {ref_name!r} not found; see /api/v1/lines")
        all_lines = [r[0] for r in _q("""SELECT DISTINCT c.CultivarName FROM Cultivar c JOIN Specie s
                                          ON s.idSpecie=c.Specie_idSpecie WHERE s.SpecieName=%s""", (species,))]
        markers, calls, line_of = _calls(species, all_lines, chrom, start, end)
    except ValueError as e:
        return _err(e)
    ref_line = next(iter(ref))
    ref_acc = next((x for x in ref[ref_line] if x in calls), None)
    if not ref_acc:
        return _json({'error': 'reference line has no genotypes in this region'}, 404)
    min_maf = float(request.args.get('min_maf', 0.05))
    min_called = float(request.args.get('min_called', 1.0))
    ok = lambda g: g not in (None, '', 'NC', '--', 'NN')
    # informative markers: polymorphic in the panel (minor allele frequency >= min_maf)
    informative = set()
    for m in markers:
        n = {}
        for gts in calls.values():
            g = gts.get(m)
            if ok(g):
                for a in g:
                    n[a] = n.get(a, 0) + 1
        tot = sum(n.values())
        if len(n) > 1 and tot and min(n.values()) / tot >= min_maf:
            informative.add(m)
    ref_gt = {m: g for m, g in calls[ref_acc].items() if ok(g) and m in informative}
    if len(ref_gt) < 3:
        return _json({'error': f'only {len(ref_gt)} informative called marker(s) (MAF >= {min_maf}) for the reference '
                               'line in this region; widen the region (max 5 Mb) or lower min_maf'}, 400)
    matches = []
    for acc, gts in calls.items():
        if acc == ref_acc:
            continue
        shared = [m for m in ref_gt if ok(gts.get(m))]
        mm = sum(gts[m] != ref_gt[m] for m in shared)
        if shared and mm <= max_mm and len(shared) >= min_called * len(ref_gt):
            matches.append({'accession': acc, 'line': line_of[acc], 'compared': len(shared), 'mismatches': mm})
    matches.sort(key=lambda x: (x['mismatches'], -x['compared'], x['line']))
    limit = min(int(request.args.get('limit', 200)), MAX_LIMIT)
    order = sorted(ref_gt, key=lambda m: markers[m][0])
    frac = len(matches) / max(1, len(calls) - 1)
    note = (f'common haplotype: shared by {frac:.0%} of accessions at {len(ref_gt)} informative markers, so it is not '
            'diagnostic for the reference line at this marker density' if frac > 0.2 else None)
    return _json({'note': note, 'species': species, 'build': build, 'chrom': chrom, 'start': start, 'end': end,
                  'reference': {'line': ref_line, 'accession': ref_acc},
                  'haplotype': [{'id': m, 'pos': markers[m][0], 'genotype': ref_gt[m]} for m in order],
                  'accessions_tested': len(calls), 'markers_in_region': len(markers),
                  'informative_markers': len(ref_gt), 'max_mismatch': max_mm, 'min_maf': min_maf,
                  'min_called': min_called, 'n_matching': len(matches),
                  'fraction_matching': round(frac, 4), 'matching': matches[:limit],
                  'method': f'markers polymorphic in the panel (MAF >= {min_maf}); a match has calls at >= '
                            f'{min_called:.0%} of them and at most {max_mm} mismatches'})


@app.route('/api/v1/phenotypes', methods=['GET'])
def api_phenotypes():
    line = request.args.get('line', '').strip()
    trait = request.args.get('trait', '').strip()
    if not line and not trait:
        traits = _q("SELECT Trait, COUNT(*), COUNT(DISTINCT Accession_idAccession) FROM AccessionPhenotype GROUP BY Trait ORDER BY Trait")
        return _json({'traits': [{'trait': t, 'records': n, 'accessions': k} for t, n, k in traits]})
    limit = min(int(request.args.get('limit', 200)), 5000)
    where, args = [], []
    if line:
        where.append("(c.CultivarName=%s OR a.Accession=%s)")
        args += [line, line]
    if trait:
        where.append("p.Trait=%s")
        args.append(trait)
    rows = _q(f"""SELECT a.Accession, c.CultivarName, s.SpecieName, p.Trial, p.Location, p.Trait, p.Value, p.NPlots, p.Source
                  FROM AccessionPhenotype p JOIN Accession a ON a.idAccession=p.Accession_idAccession
                  JOIN Cultivar c ON c.idCultivar=a.Cultivar_idCultivar JOIN Specie s ON s.idSpecie=c.Specie_idSpecie
                  WHERE {' AND '.join(where)} ORDER BY a.Accession, p.Trial, p.Trait LIMIT %s""", (*args, limit))
    cols = ['accession', 'line', 'species', 'trial', 'location', 'trait', 'value', 'n_plots', 'source']
    return _json({'n': len(rows), 'phenotypes': [dict(zip(cols, r)) for r in rows]})
