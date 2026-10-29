import os
import sys
import ast
import time
import json
import pandas as pd
from flask import render_template, flash, redirect,request,send_from_directory, make_response
from app import app
#from .forms import SNPSubmit, SNPSearch
from forms import SNPSubmit, SNPSearch
from dataHandeler import useInputToSearchv2, getDicChrWithSpecies as ChrWS, getDicChipsWithSpecies as CWS, getDicSpeciesWithCultivar as SWC
from fileHandeler import checkPath
from validating import fileIsLegit
from werkzeug.utils import secure_filename
from collections import defaultdict

#Checks what python version is used and imports the thread library for the right python version
if(sys.version_info > (3,0)):
	import _thread as thread
else:
	import thread

#SNPSearch contains the input fields
#When the forms are filled in the results are taken from the database
#Makes a new page but with a list of SNP results
@app.route('/search',methods=["GET","POST"])
def search():	
	message=getMessage('search')
	chipsWithSpecies = CWS()
	speciesWithCultivar = SWC()
	chromosomesWithSpecies = ChrWS()
	form=SNPSearch()	
	if form.is_submitted():
		#Checks if fields are empty or not
		#If one field is empty returs error
		for item in form:
			if item.id != "Cultivars" and item.data == "" or item.id != "Cultivars" and item.data == []:
				return render_template('SNPSearch.html',title="Error",form=form,chromosomesWithSpecies=chromosomesWithSpecies,chipsWithSpecies=chipsWithSpecies,speciesWithCultivar=speciesWithCultivar,message=message,error="Field(s) empty. Ensure at least one cultivar is selected and genomic coordinates are provided.")
		
		#Takes data from form
		specie = form.Specie.data
		QueryCultivars = form.QueryCultivars.data
		chromosomes = form.ChromDrop.data
		coordinationFrom = form.CoordinationFrom.data
		coordinationTo = form.CoordinationTo.data

		try:
			int(coordinationTo)
			int(coordinationFrom)
		except:
			return render_template('SNPSearch.html',title="Warning",form=form,chromosomesWithSpecies=chromosomesWithSpecies,chipsWithSpecies=chipsWithSpecies,speciesWithCultivar=speciesWithCultivar,message=message,error="Genomic coordinate error. Values must be integers.")		
		if int(coordinationTo) <= int(coordinationFrom):
			return render_template('SNPSearch.html',title="Warning",form=form,chromosomesWithSpecies=chromosomesWithSpecies,chipsWithSpecies=chipsWithSpecies,speciesWithCultivar=speciesWithCultivar,message=message,error="Genomic coordinate error. Integer value for 'Coordinates from' must be less than value for 'Coordinates to'.")		
		if int(coordinationTo) - int(coordinationFrom) > 1000000 and len(QueryCultivars) > 500:
			return render_template('SNPSearch.html',title="Warning",form=form,chromosomesWithSpecies=chromosomesWithSpecies,chipsWithSpecies=chipsWithSpecies,speciesWithCultivar=speciesWithCultivar,message=message,error="Search parameters too broad. Try reducing the number of cultivars, narrowing the coordinate range, or downloading all genotypes for the chromosome on the 'Download' page.")			
		#Uses data to search database
		try:
			databaseOutput = useInputToSearchv2(specie,QueryCultivars,chromosomes,coordinationFrom,coordinationTo)
		except ValueError as e:
			return render_template('SNPSearch.html',title="Warning",form=form,chromosomesWithSpecies=chromosomesWithSpecies,chipsWithSpecies=chipsWithSpecies,speciesWithCultivar=speciesWithCultivar,message=message,error=str(e))
		results = {}
		#Adds database output into a dic
		#Key = snp_id + accession from one snp
		#Entry = all data from one snp

		probedf = pd.read_csv(app.config['PROBES'], index_col='idx', names=['idx','probeseq'])

		for result in databaseOutput:
			#load into pandas df
			#drop Source column
			#SNPid as index for static Source list
			#add source to result 
			try:
				snpsource = probedf.loc[result[4],'probeseq']
			except KeyError:
				snpsource = 'NA'
			result = list(result)
			result.insert(10,snpsource)
			result = tuple(result)
			results[result[3]+result[4]] = result
		if results:
			hasResult = True;
		else:
			hasResult = False;
		# decide what gbrowse URL to be used (NA unless a browser is configured)
		gbrowseLink = 'NA'
		if specie=='Triticum aestivum RefSeq v1 and Pan':
			gbrowseLink=app.config['GBROWSE_WHEAT_URL']
		elif specie=='Brassica napus Darmor v81':
			gbrowseLink=app.config['GBROWSE_BRASSICA_NAPUS_V81_URL']
		elif specie=='Brassica napus Darmor v41':
			gbrowseLink=app.config['GBROWSE_BRASSICA_NAPUS_V41_URL']
		elif specie=='Brassica oleracea v2.1':
			gbrowseLink=app.config['GBROWSE_BRASSICA_OLERACEA_URL']
		elif specie=='Brassica rapa v3':
			gbrowseLink=app.config['GBROWSE_BRASSICA_RAPA_URL']
		elif  specie=='Brassica juncea v1.5':
			gbrowseLink=app.config['GBROWSE_BRASSICA_JUNCEA_URL']
		return render_template('SNPSearch.html',
					title="Result",
					form=form,
					results=results,
					message=message,
					specie=specie,
					QueryCultivars=QueryCultivars,
					chromosomes=chromosomes,
					coordinationFrom=coordinationFrom,
					coordinationTo=coordinationTo,
					chromosomesWithSpecies=chromosomesWithSpecies,
					chipsWithSpecies=chipsWithSpecies,
					speciesWithCultivar=speciesWithCultivar,
					hasResult=hasResult,
					gbrowseLink=gbrowseLink,
					success="Search successfully submitted! Scroll down for search results. Depending on your query, it may take several seconds before results appear.")
	else:
		print(form.errors)
	return render_template('SNPSearch.html',
				title ="Search",
				form=form,
				chromosomesWithSpecies=chromosomesWithSpecies,
				chipsWithSpecies=chipsWithSpecies,
				speciesWithCultivar=speciesWithCultivar,
				message=message)

#After a person searched for information they get the option to download found information as a csv file
#When they search their input gets saved with a hiddenfield
#That hiddenfield is used to get the information from the database and return it as a csv file
@app.route('/downloadSearch',methods=["POST"])
def download():
        form = request.form
        #Looks if every field is empty or not
        if form:
            for item in form:
                if item == "":
                   return render_template('SNPSearch.html',title="Error",form=form,speciesWithCultivar=speciesWithCultivar,message=message,error="Field(s) empty")
                #Gathers data users filled in
            specie = form['specie']
            print(specie)
            cultivars = ast.literal_eval(form['cultivars'])
            print(cultivars)
            chromosome = form['chromosomes']
            coordinationFrom = form['coordinationFrom']
            coordinationTo = form['coordinationTo']
            #Gets data from database
            listOfSNPs = useInputToSearchv2(specie,cultivars,chromosome,coordinationFrom,coordinationTo)
            #CSV output as genotype table with accessions in header
            print(listOfSNPs)
            probedf = pd.read_csv(app.config['PROBES'], index_col='idx', names=['idx','probeseq'])
        
            cultivars = set()
            snpdict = defaultdict(list)
            snpinfodict = defaultdict(list)

            for SNP in listOfSNPs:    
                snpsource = probedf.loc[SNP[4],'probeseq']
                SNP = list(SNP)
                SNP.insert(10,snpsource)
                unid = SNP[2].replace(" ","_") + "__" + SNP[3]
                cultivars.add(unid)
                SNPid = SNP[4]
                probeseq = SNP[10]
                pos = SNP[8]
                strand = SNP[6]
                ref_snp = SNP[5]
                chrom = SNP[7]
                chip = SNP[0]
                doi = SNP[11]
                species = SNP[1]		
             
                #snpdict holds list of cults with genos for each snp
                if SNPid in snpdict:
                    snpdict[SNPid].append((unid,SNP[9]))
                else:
                    snpdict[SNPid] = [(unid,SNP[9])]
                if SNPid in snpinfodict:
                    pass
                else: #add to snpinfodict which holds SNP meta information
                    snpinfodict[SNPid] = [(probeseq,pos,strand,ref_snp,chrom,chip,species)]
            all_cult_of_SNP = set()
            sorted_cult = sorted(list(cultivars))
            #print(sorted_cult)
            for SNPID in snpdict: #for each key in dict
                for SNPcultivars in snpdict[SNPID]:
                    all_cult_of_SNP.add(SNPcultivars[0])
                missing_cult = list(cultivars - all_cult_of_SNP)
                all_cult_of_SNP = set()
                for cultivar in missing_cult:
                    snpdict[SNPID].append((cultivar,"?"))
            header = [] #header row for CSV output
            for cultivar in sorted_cult:
                header.append(cultivar)
            columnlist = ['SNPid','Species','Array','Chr','Ref_SNP','Strand','SNP_Position_On_Chr','Probe_Sequence']
            columnlist.reverse()
            for column in columnlist:
                header.insert(0,column)
            #print(header)
            toFile = ','.join(map(str, header)) + "\n" 
            for SNPID in snpdict: # loops through SNPids
	
                genolist = list() # holds row for each SNP to be printed to outfile
                for cult in sorted_cult: #loop through unique ids (Cultivar_Accession)
                    for SNPcultivars in snpdict[SNPID]: # for each unique id and genotype associated with a particular SNP
                        if cult == SNPcultivars[0]: # if the unique id is the same as the column we are trying to fill
                            genolist.append(SNPcultivars[1]) #append the genotype of the unique id to the SNP row
                for value in snpinfodict[SNPID][0][0:]:
                    genolist.insert(0,value)
                genolist.insert(0,SNPID)
                print(genolist)
                toFile = toFile + ','.join(map(str, genolist)) + "\n" 
            #Makes csv file and returns it
            response = make_response(toFile)
            exportfilename = specie.replace(" ", "_") + "_" + chromosome + "_" + coordinationFrom + "-" + coordinationTo + "_genotypes.csv"
            response.headers["Content-Disposition"] = "attachment; filename="+exportfilename+""
            #Content-Type must be specified for Firefox to correctly handle the .csv extension
            response.headers["Content-Type"] = "text/csv; charset=utf-8" 
            return response

#When users go to ip/submit this will run
#SNPSubmit contains the input fields
#If the input fields are filled uploads the given file and stores it into the database
#Writing the file to the database is threaded and happens after the file is uploaded
#Renders a new page but with a upload succeed message (or an error if something failed)
#Writes into command line if lines of data got removed from an file
@app.route('/submit',methods=["POST","GET"])
def submit():
	message = getMessage('submit')
	form = SNPSubmit.new()
	if form.validate_on_submit():
		#Gets data from form
		email = form.Email.data
		SNPArray = form.SNPArray.data
		SNPFile = form.SNPFile.data
		cultivarFile = form.CultivarFile.data
		#Gets uploaded files
		if SNPFile != "" and cultivarFile != "":
			SNPUploadFile = request.files["SNPFile"]
			cultivarUploadFile = request.files["CultivarFile"]
			#Gets uploaded file names
			SNPUploadFileName = SNPUploadFile.filename
			#First5lettersofSpecies-YYMMDD-hhmmss                
			cultivarUploadFileName = cultivarUploadFile.filename
			timestring = time.strftime("%Y%m%d-%H%M%S")
			uniq_fname = SNPArray + "_" + timestring
			snpname = uniq_fname + "_" + SNPUploadFileName[:50]
			cultname = uniq_fname + "_" + cultivarUploadFileName[:50]
			#Looks if uploaded files have the right file extension 
			if fileIsLegit(SNPUploadFileName) and fileIsLegit(cultivarUploadFileName):
				#Uses SNPUploadFileName to make a path to create a dir for that specific upload
				tempDirPath = os.path.join(app.config['UPLOAD_FOLDER'],timestring)
				i = 0
				dirPath = tempDirPath
				#Checks if dir already exists and changes path until it doesn't
				while(os.path.exists(dirPath)):
					i=i+1
					dirPath = tempDirPath + "("+str(i)+")"
				os.makedirs(dirPath)
				dirPath = dirPath + "/"
				
				#Checks if path isn't a hack
				#Creates path for the files to save to
				SNPUploadFilePath = checkPath(dirPath + snpname)
				cultivarUploadFilePath = checkPath(dirPath + cultname)		
				emailtxtFilePath = dirPath + "email.txt"

				try:
					qualityFile = form.qualityFile.data
					qualityUploadFile = request.files["qualityFile"]
					qualityUploadFileName = qualityUploadFile.filename
					qualname = uniq_fname + "_" + qualityUploadFileName[:50]
					if fileIsLegit(qualityUploadFileName):
						qualityUploadFilePath = checkPath(dirPath + qualname)
						qualityUploadFile.save(qualityUploadFilePath)
				except:
					pass
				#Save files
				SNPUploadFile.save(SNPUploadFilePath)
				cultivarUploadFile.save(cultivarUploadFilePath)
				with open(emailtxtFilePath, "w") as text_file:
					print("Submission email: {}".format(email), file=text_file)
				#Email alert to curators (settings in mail.cfg; skipped if not configured)
				try:
					from notify import notify_submission
					notify_submission("CropSNPdb: new data submission ({})".format(SNPArray),
						"A new genotype submission was uploaded to CropSNPdb.\n\nSubmitter email: {}\nSNP array: {}\nGenotype file: {}\nCultivar file: {}\nSaved in: {}\n".format(email, SNPArray, SNPUploadFileName, cultivarUploadFileName, dirPath))
				except Exception:
					pass
			else:
				return render_template('SNPSubmit.html',title="Error",form=form,message=message,error="csv")
			return render_template('SNPSubmit.html',
						title="Uploaded "+SNPUploadFileName,
						fileSubmit=SNPUploadFileName,
						form=form,
						message=message)
	
		return render_template('SNPSubmit.html',title="Error",form=form,message=message,error="Error")

	return render_template('SNPSubmit.html',
				title ="Upload",
				form=form,
				message=message)

@app.route('/download',methods=["GET"])
def downloadchr():
        return render_template('Download.html',
                                title="Download")

#Shows the home page
@app.route('/',methods=["GET","POST"])
@app.route('/home',methods=['GET'])
def home():
	filename = os.path.join(app.config['STATIC_FOLDER'], 'logo.png')
	return render_template('Home.html',
				user_image = filename,
				title="Home")

#Renders the submit page with an error
def getErrorSubmit(form,expectedFileType,message):
	return render_template('SNPSubmit.html',
                                                title="Error",
                                                form=form,
                                                error=expectedFileType,
						message=message)

#Gets the bottom message page specific
def getMessage(pageType):
	if pageType == 'search':
		with open(os.path.join(app.config['STATIC_FOLDER'],'searchText.html'),'r', encoding='utf-8', errors='ignore') as searchTextFile:
			message = searchTextFile.read()
		return message
	elif pageType == 'download':
		with open(os.path.join(app.config['STATIC_FOLDER'],'searchText.html'),'r', encoding='utf-8', errors='ignore') as downloadTextFile:
			message = downloadTextFile.read()

#Lines page: all accessions with their metadata (added 2026-10-18)
LINES_SQL = """SELECT a.Accession, c.CultivarName, GROUP_CONCAT(DISTINCT s.SpecieName ORDER BY s.SpecieName SEPARATOR '; '),
 m.Country, m.Ecotype, m.BiologicalStatus, m.CropType, m.BreedingOrganization, m.Pedigree, m.Subpopulation,
 m.GrainHardness, m.GrainColour, m.AGG_ID, m.SuppliedSpecies, m.SNPConfirmedSpecies, m.Donor, m.ExternalURL,
 CONCAT(r.Authors,' (',r.Date,') ',r.Journal), r.DOI, m.MetadataSource
 FROM Accession a JOIN Cultivar c ON a.Cultivar_idCultivar=c.idCultivar JOIN Specie s ON s.idSpecie=c.Specie_idSpecie
 JOIN Reference r ON r.RefID=a.Accession_RefID LEFT JOIN AccessionMetadata m ON m.Accession_idAccession=a.idAccession
 GROUP BY a.idAccession ORDER BY a.idAccession"""
LINES_COLS = ['Accession','Line','Species','Country','Ecotype','Status','Crop type','Breeding organisation','Pedigree','Subpopulation',
 'Grain hardness','Grain colour','AGG ID','Genebank species','SNP-confirmed species','Donor','External link','Genotype source','Source DOI/URL','Metadata source']

def getLines():
	from mysqlQuerys import getCursor, getResult
	cur, con = getCursor()
	cur.execute(LINES_SQL)
	rows = getResult(cur, con)
	return [[("" if v is None else str(v)).replace("Brassica napus Darmor v41; Brassica napus Darmor v81","Brassica napus") for v in r] for r in rows]

@app.route('/lines', methods=["GET"])
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
	like = q.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
	cur, con = getCursor()
	cur.execute("SELECT DISTINCT c.CultivarName FROM Cultivar c JOIN Specie s ON s.idSpecie=c.Specie_idSpecie WHERE s.SpecieName=%s AND c.CultivarName LIKE %s ORDER BY (c.CultivarName LIKE %s) DESC, c.CultivarName LIMIT 300", (species, '%' + like + '%', like + '%'))
	return jsonify([r[0] for r in getResult(cur, con)])

@app.route('/lines.csv', methods=["GET"])
def lines_csv():
	import csv, io
	buf = io.StringIO()
	w = csv.writer(buf)
	w.writerow(LINES_COLS)
	w.writerows(getLines())
	resp = make_response(buf.getvalue())
	resp.headers["Content-Type"] = "text/csv; charset=utf-8"
	resp.headers["Content-Disposition"] = "attachment; filename=CropSNPdb_lines_metadata.csv"
	return resp

#Phenotype CSV (AGG field data, added 2026-10-18)
@app.route('/phenotypes.csv', methods=["GET"])
def phenotypes_csv():
	import csv, io
	from mysqlQuerys import getCursor, getResult
	cur, con = getCursor()
	cur.execute("SELECT a.Accession, c.CultivarName, p.Trial, p.Location, p.Trait, p.Value, p.NPlots, p.Source FROM AccessionPhenotype p JOIN Accession a ON a.idAccession=p.Accession_idAccession JOIN Cultivar c ON c.idCultivar=a.Cultivar_idCultivar ORDER BY a.idAccession, p.Trial, p.Trait")
	rows = getResult(cur, con)
	buf = io.StringIO(); w = csv.writer(buf)
	w.writerow(['Accession','Line','Trial','Location','Trait','Value','NPlots','Source']); w.writerows(rows)
	resp = make_response(buf.getvalue())
	resp.headers["Content-Type"] = "text/csv; charset=utf-8"
	resp.headers["Content-Disposition"] = "attachment; filename=CropSNPdb_field_phenotypes.csv"
	return resp
