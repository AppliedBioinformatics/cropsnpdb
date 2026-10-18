import sys
A = sys.argv[1]
p = A + "/views.py"; s = open(p).read()
old = '''				with open(emailtxtFilePath, "w") as text_file:
					print("Submission email: {}".format(email), file=text_file)'''
new = old + '''
				#Email alert to curators (settings in mail.cfg; skipped if not configured)
				try:
					from notify import notify_submission
					notify_submission("CropSNPdb: new data submission ({})".format(SNPArray),
						"A new genotype submission was uploaded to CropSNPdb.\\n\\nSubmitter email: {}\\nSNP array: {}\\nGenotype file: {}\\nCultivar file: {}\\nSaved in: {}\\n".format(email, SNPArray, SNPUploadFileName, cultivarUploadFileName, dirPath))
				except Exception:
					pass'''
if 'notify_submission' not in s:
    assert s.count(old) == 1
    s = s.replace(old, new)
open(p + ".new", "w").write(s)
print("wrote", p + ".new")
