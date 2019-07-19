#Takes SNPid and parses it to usable informarion
def ParseSNPid(SNPid):
	dicSNPid={}
	splitSNPid = SNPid.split('-')
	dicSNPid['chromosome'] = splitSNPid[1]
	dicSNPid['coordination'] = splitSNPid[2]
	return dicSNPid

