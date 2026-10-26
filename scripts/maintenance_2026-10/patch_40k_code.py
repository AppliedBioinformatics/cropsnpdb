import sys
A = sys.argv[1]
def edit(path, pairs, out=None):
    s = open(path).read()
    for a, b in pairs:
        assert s.count(a) == 1, (path, a[:70])
        s = s.replace(a, b)
    open(out or path + ".new", "w").write(s); print("ok", path)
# views.py: probe lookup tolerant of markers without probe sequences; default genome-browser link
edit(A + "/views.py", [
 ("			snpsource = probedf.loc[result[4],'probeseq']",
  "			try:\n				snpsource = probedf.loc[result[4],'probeseq']\n			except KeyError:\n				snpsource = 'NA'"),
 ("		# decide what gbrowse URL to be used\n",
  "		# decide what gbrowse URL to be used (NA unless a browser is configured)\n		gbrowseLink = 'NA'\n"),
])
# SNPSearch.js: NA link for species without a browser branch; line-name filter box
js_old = '''			} else if(results[$(this).attr('id')][1] === "Brassica juncea v1.5"){
				document.getElementById("gbrowseLink").href=gbrowseLink;
				document.getElementById("gbrowseLink").innerHTML="BRAD Genome Browser";
			}'''
js_new = '''			} else if(results[$(this).attr('id')][1] === "Brassica juncea v1.5"){
				document.getElementById("gbrowseLink").href=gbrowseLink;
				document.getElementById("gbrowseLink").innerHTML="BRAD Genome Browser";
			} else {
				document.getElementById("gbrowseLink").href="NA";
				document.getElementById("gbrowseLink").innerHTML="NA";
			}'''
s = open(A + "/static/SNPSearch.js").read()
assert s.count(js_old) == 1
s = s.replace(js_old, js_new)
s += '''

// Filter box for the Lines list (added 2026-10-26)
$(document).ready(function(){
	function applyLineFilter(){
		var q = ($('#lineFilter').val() || '').toLowerCase();
		$('#Cultivars option').each(function(){
			this.hidden = q !== '' && this.text.toLowerCase().indexOf(q) === -1;
		});
	}
	$('#lineFilter').on('input', applyLineFilter);
	$('#Specie, #Chip').on('change', function(){ $('#lineFilter').val(''); setTimeout(applyLineFilter, 0); });
});
'''
open(A + "/static/SNPSearch.js.new", "w").write(s); print("ok js")
# template: filter input above the Lines list, cache-buster bump
edit(A + "/templates/SNPSearch.html", [
 ('''								{{ form.Cultivars(style="max-width:100%") }}''',
  '''								<input type="text" id="lineFilter" placeholder="Type to filter lines..." style="width:100%;margin-bottom:4px" autocomplete="off">
								{{ form.Cultivars(style="max-width:100%") }}'''),
 ("SNPSearch.js?v=20261017b", "SNPSearch.js?v=20261026"),
])
