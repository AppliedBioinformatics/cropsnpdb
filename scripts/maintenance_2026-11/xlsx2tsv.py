import zipfile, re, sys, csv, xml.etree.ElementTree as ET
z = zipfile.ZipFile(sys.argv[1]); ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
ss = [("".join(t.text or "" for t in si.iter("{%s}t" % ns["m"]))) for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", ns)] if "xl/sharedStrings.xml" in z.namelist() else []
rows = []
for r in ET.fromstring(z.read("xl/worksheets/sheet1.xml")).iter("{%s}row" % ns["m"]):
    out = {}
    for c in r.findall("m:c", ns):
        col = re.match(r"[A-Z]+", c.get("r")).group(); v = c.find("m:v", ns); t = c.get("t")
        val = ss[int(v.text)] if t == "s" and v is not None else (v.text if v is not None else "".join(x.text or "" for x in c.iter("{%s}t" % ns["m"])))
        out[ord(col) - 65] = val
    rows.append([out.get(i, "") for i in range(max(out) + 1)] if out else [])
csv.writer(open(sys.argv[2], "w"), delimiter="\t").writerows(rows)
