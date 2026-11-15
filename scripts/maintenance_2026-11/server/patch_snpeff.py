import os
os.chdir('/var/www/html/cropsnpdb/snpdb/app')
def rep(p,old,new,dest=None):
    s=open(p).read(); assert s.count(old)==1,(p,old[:60]); open(dest or p,"w").write(s.replace(old,new))
rep("ownLib/vcfBackend.py","""			ref = '[{}/{}]'.format(rec.ref, ','.join(rec.alts or ()))
""","""			ref = '[{}/{}]'.format(rec.ref, ','.join(rec.alts or ()))
			ann = ''
			if 'GENE' in rec.header.info and 'GENE' in rec.info:
				ann = '{}: {} ({})'.format(rec.info['GENE'], rec.info.get('EFFECT', ''), rec.info.get('IMPACT', ''))
""")
rep("ownLib/vcfBackend.py","out.append((r[5], species, r[0], r[1], rec.id, ref, 'NA', chrom, rec.pos, g, r[4]))","out.append((r[5], species, r[0], r[1], rec.id, ref, 'NA', chrom, rec.pos, g, r[4], ann))")
rep("genoapi.py","    for arr, sp, line, acc, snp, ref, strand, ch, pos, gt, doi in rows:","    for arr, sp, line, acc, snp, ref, strand, ch, pos, gt, doi, *extra in rows:",dest="/tmp/genoapi.py")
rep("views.py","""			result = list(result)
			result.insert(10,snpsource)
""","""			result = list(result)
			result.insert(10,snpsource)
			if len(result) < 13:
				result.append('')   # gene effect (VCF INFO, e.g. OzBarley RNA-seq SnpEff)
""")
rep("views.py","""                snpsource = probedf.loc[SNP[4],'probeseq']
                SNP = list(SNP)
                SNP.insert(10,snpsource)
""","""                try:
                    snpsource = probedf.loc[SNP[4],'probeseq']
                except KeyError:
                    snpsource = 'NA'
                SNP = list(SNP)
                SNP.insert(10,snpsource)
                effect = SNP[12] if len(SNP) > 12 and SNP[12] else 'NA'
""")
rep("views.py","snpinfodict[SNPid] = [(probeseq,pos,strand,ref_snp,chrom,chip,species)]","snpinfodict[SNPid] = [(effect.replace(',',';'),probeseq,pos,strand,ref_snp,chrom,chip,species)]")
rep("views.py","columnlist = ['SNPid','Species','Array','Chr','Ref_SNP','Strand','SNP_Position_On_Chr','Probe_Sequence']","columnlist = ['SNPid','Species','Array','Chr','Ref_SNP','Strand','SNP_Position_On_Chr','Probe_Sequence','Gene_effect']")
rep("static/SNPSearch.js","""			sourceSeq.text(results[$(this).attr('id')][10]) ""","""			sourceSeq.text(results[$(this).attr('id')][10]) 
			var geneEffect = results[$(this).attr('id')][12]
			$('#geneEffectRow').toggle(!!geneEffect)
			$('#geneEffect').text(geneEffect || '')""")
rep("templates/SNPSearch.html","""				<div class="row">
					<div class="col-md-2">
						<b>Source sequence</b>""","""				<div class="row" id="geneEffectRow" style="display:none">
					<div class="col-md-2">
						<b>Gene effect</b>
					</div>
					<div class="col-md-10">
						<p id="geneEffect"></p>
					</div>
				</div>
				<div class="row">
					<div class="col-md-2">
						<b>Source sequence</b>""")
print("patched")
