import sys, re
A = sys.argv[1]
def edit(path, pairs):
    s = open(path).read()
    for a, b in pairs:
        assert s.count(a) == 1, (path, a[:80]); s = s.replace(a, b)
    open(path + ".new", "w").write(s); print("ok", path)
# dataHandeler: route VCF-backed species; large species load lines on demand
edit(A + "/ownLib/dataHandeler.py", [
 ("	speciesName = species\n	return getSNPData(",
  "	speciesName = species\n	import vcfBackend\n	if vcfBackend.handles(species):\n		return vcfBackend.search(species,cultivars,chromosoms,coordinationFrom,coordinationTo)\n	return getSNPData("),
 ("		cultivars = CultivarsWithSpecieId(specie[0])\n		for cultivar in cultivars:",
  "		cultivars = CultivarsWithSpecieId(specie[0])\n		if len(cultivars) > 5000:\n			#too many to embed in the page: the Search page looks these up as the user types\n			speciesWithCultivars[specie[1]]=['__REMOTE__']\n			continue\n		for cultivar in cultivars:"),
])
# views: friendly error for oversized searches; /api/lines; /lines.json; /lines without embedded rows
v = open(A + "/views.py").read()
old = "		databaseOutput = useInputToSearchv2(specie,QueryCultivars,chromosomes,coordinationFrom,coordinationTo)\n"
new = ("		try:\n			databaseOutput = useInputToSearchv2(specie,QueryCultivars,chromosomes,coordinationFrom,coordinationTo)\n"
       "		except ValueError as e:\n"
       "			return render_template('SNPSearch.html',title=\"Warning\",form=form,chromosomesWithSpecies=chromosomesWithSpecies,chipsWithSpecies=chipsWithSpecies,speciesWithCultivar=speciesWithCultivar,message=message,error=str(e))\n")
assert v.count(old) == 1; v = v.replace(old, new)
old = "@app.route('/lines', methods=[\"GET\"])\ndef lines():\n	return render_template('Lines.html', title=\"Lines\", cols=LINES_COLS, rows=getLines())\n"
new = ('''@app.route('/lines', methods=["GET"])
def lines():
	from mysqlQuerys import getCursor, getResult
	cur, con = getCursor()
	cur.execute("SELECT COUNT(*) FROM Accession")
	n = getResult(cur, con)[0][0]
	return render_template('Lines.html', title="Lines", cols=LINES_COLS, nrows=n)

@app.route('/lines.json', methods=["GET"])
def lines_json():
	import json, gzip
	body = json.dumps({"data": getLines()}).encode()
	resp = make_response(body)
	resp.headers["Content-Type"] = "application/json"
	if 'gzip' in request.headers.get('Accept-Encoding', ''):
		resp.set_data(gzip.compress(body))
		resp.headers["Content-Encoding"] = "gzip"
		resp.headers["Vary"] = "Accept-Encoding"
	return resp

@app.route('/api/lines', methods=["GET"])
def api_lines():
	#type-ahead line search for species with too many lines to embed in the Search page
	from flask import jsonify
	from mysqlQuerys import getCursor, getResult
	species = request.args.get('species', '')
	q = request.args.get('q', '').strip()
	if len(q) < 2:
		return jsonify([])
	like = q.replace('\\\\', '\\\\\\\\').replace('%', '\\\\%').replace('_', '\\\\_')
	cur, con = getCursor()
	cur.execute("SELECT DISTINCT c.CultivarName FROM Cultivar c JOIN Specie s ON s.idSpecie=c.Specie_idSpecie WHERE s.SpecieName=%s AND c.CultivarName LIKE %s ORDER BY (c.CultivarName LIKE %s) DESC, c.CultivarName LIMIT 300", (species, '%' + like + '%', like + '%'))
	return jsonify([r[0] for r in getResult(cur, con)])
''')
assert v.count(old) == 1; v = v.replace(old, new)
open(A + "/views.py.new", "w").write(v); print("ok views")
# JS: replace the simple filter block with local filter + remote type-ahead
js = open(A + "/static/SNPSearch.js").read()
i = js.index("// Filter box for the Lines list (added 2026-10-26)")
js = js[:i] + '''// Line filter / type-ahead search (added 2026-10-26, type-ahead 2026-10-29)
$(document).ready(function(){
	var REMOTE = '__REMOTE__', timer = null;
	function isRemote(){
		var l = speciesWithCultivars[$('#Specie').val()];
		return l && l.length === 1 && l[0] === REMOTE;
	}
	function fixRemote(){
		$('#Cultivars option').filter(function(){ return this.value === REMOTE; }).remove();
		$('#lineFilter').attr('placeholder', isRemote() ? 'Type 2+ letters to search lines...' : 'Type to filter lines...');
	}
	function localFilter(){
		var q = ($('#lineFilter').val() || '').toLowerCase();
		$('#Cultivars option').each(function(){ this.hidden = q !== '' && this.text.toLowerCase().indexOf(q) === -1; });
	}
	function remoteSearch(){
		var q = ($('#lineFilter').val() || '').trim(), sel = $('#Cultivars');
		if(q.length < 2){ sel.empty(); return; }
		$.getJSON('/api/lines', {species: $('#Specie').val(), q: q}, function(names){
			sel.empty();
			names.forEach(function(n){ sel.append(new Option(n, n)); });
		});
	}
	$('#lineFilter').on('input', function(){
		if(isRemote()){ clearTimeout(timer); timer = setTimeout(remoteSearch, 250); } else { localFilter(); }
	});
	$('#Specie, #Chip').on('change', function(){ $('#lineFilter').val(''); setTimeout(function(){ fixRemote(); localFilter(); }, 0); });
	fixRemote();
});
'''
open(A + "/static/SNPSearch.js.new", "w").write(js); print("ok js")
edit(A + "/templates/SNPSearch.html", [("SNPSearch.js?v=20261026", "SNPSearch.js?v=20261029")])
# Lines page: load rows via ajax
t = open(A + "/templates/Lines.html").read()
t = t.replace("All {{rows|length}} genotyped accessions", "All {{nrows}} genotyped accessions")
t = re.sub(r"\t\t<tbody>.*?</tbody>\n", "", t, flags=re.S)
old = "$(document).ready(function(){ $('#linesTable').DataTable({pageLength:25, order:[], columnDefs:[{targets:[8,12,13,15,16,17,18,19], visible:false}]}); });"
new = ("$(document).ready(function(){ $('#linesTable').DataTable({ajax:'/lines.json', deferRender:true, pageLength:25, order:[], "
       "language:{loadingRecords:'Loading lines...'}, "
       "columnDefs:[{targets:[8,12,13,15,16,17,18,19], visible:false},"
       "{targets:'_all', render:function(d,type){ if(type==='display' && typeof d==='string' && d.indexOf('http')===0){ return '<a href=\"'+d+'\" target=\"_blank\" rel=\"noopener\">link</a>'; } return d; }}]}); });")
assert t.count(old) == 1 and "{{nrows}}" in t and "<tbody>" not in t
t = t.replace(old, new)
open(A + "/templates/Lines.html.new", "w").write(t); print("ok lines template")
