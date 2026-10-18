$(document).ready(function() {
	var queryResult = $('#queryResult')
	var speciesField = $('#Specie')
	var chipField = $('#Chip')
	var cultivarsField = $('#Cultivars')
	var chrList = $('#ChromDrop')
	var resultRow = $('#queryResult > tbody > tr');
	var downloadButton = $('#downloadSubmit')
	var informationBox = $('#informationBox');
	var dataList = $('#suggestionsSpecie')
	var messageBox = $('#message')
	var helpButton = $('#helpButton')
	informationBoxId = informationBox.attr('id')
	var informationBoxContent = '#'+informationBoxId+'> ul'
	var closeButton = $('#'+informationBoxId+' #Close')
	
	chipNameField = $('#'+informationBoxId+" #chipName")
	speciesbox = $('#'+informationBoxId+" #species")
	cultivarField = $('#'+informationBoxId+" #cultivar")
	accessionField = $('#'+informationBoxId+" #accession")
	snpIdField =  $('#'+informationBoxId+" #snpId")
	chromosomeField =  $('#'+informationBoxId+" #chromosome")
	coordinate = $('#'+informationBoxId+" #coordinate") 
	referenceSNPField = $('#'+informationBoxId+" #referenceSNP")
	referenceStrand = $('#'+informationBoxId+" #referenceStrand")
	genotypeAccession = $('#'+informationBoxId+" #genotypeAccession")
	sourceSeq = $('#'+informationBoxId+" #sourceSeq")
	/*Modal SNP information box */
	var modal = document.getElementById('myModal');
	var span = document.getElementsByClassName("close")[0];

	//Cultivars selected by user are stored in browser
	var stored_cultivars = JSON.parse(localStorage.getItem("QueryCultivars"));
	
	SpeciesCheck()

	if(speciesField.val() === ""){
		SpeciesCheck()
	}
	else{
		value = cultivarsField.val()
			cultivarsField.val(value)	
		value = chrList.val()
			chrList.val(value)
	}

	if (stored_cultivars !== null) {
		repop()
	}


	queryResult.on('init.dt',function(e,settings,json){queryResult.show(1000);})
	queryResult.dataTable( {
		"scrollCollapse": true,
		"paging":         true,
		"bFilter":        false,
		"bPaginate":      true,
		"bLengthChange":   true,
		"searching": true
	} );


	$('#addButton').click(
	function(){
		getSelectValues(document.getElementById("Cultivars"));
		sortQueryCultivars();	
	});
	
	$('#removeButton').click(
	function(){
		removeSelectValues(document.getElementById("QueryCultivars"));
	});

	$('#submitButton').click(
	function(){
	selectQueryCult()
	//Selected lines need to be retained in form after query submission
	var sel_cul = document.getElementById("QueryCultivars");
	
	sessionStorage.setItem('Species', speciesField.val());
	sessionStorage.setItem('Chromosome', chrList.val());

	culs = [];
	//Loop over cultivars and push to array
	for (var i = 0, n = sel_cul.options.length; i < n; i++) {
  		if (sel_cul.options[i].value) culs.push(sel_cul.options[i].value);
	}
	//JSONify array and store in browser
	localStorage.setItem('QueryCultivars', JSON.stringify(culs));
	}
	);

	//Select query species after page refresh

	function SelectElement(id, valueToSelect){    
    		var element = document.getElementById(id);
    		element.value = valueToSelect;
	}

	//Repopulate 'Selected Lines' form with queried lines

	function repop(){
	var selectedSpecies = sessionStorage.getItem('Species');
	if (selectedSpecies) {
		speciesField.value = selectedSpecies;
		SelectElement("Specie",selectedSpecies)
	}

	CultivarCheck() //necessary?

	for (x=0;x<stored_cultivars.length;x++) {
		var option = document.createElement("option");
		option.text=stored_cultivars[x];
		document.getElementById("QueryCultivars").add(option)
	}
	}

	$('#downloadSubmit').click(
	selectQueryCult()
	);

	function selectQueryCult(){
	for ( var i = 0, l = document.getElementById("QueryCultivars").options.length, o; i < l; i++ ) {
                        o = document.getElementById("QueryCultivars").options[i];
                        o.selected = true;
	}
	}

	chipField.change(function(){SpeciesCultivarCheckAndReset()});
	speciesField.change(function(){CultivarCheckAndReset()});

	function SpeciesCultivarCheckAndReset(){
		SpeciesCheck();
		resetlines();
		CultivarCheck();
	}

	function CultivarCheckAndReset(){
		resetlines();
		CultivarCheck();
	}
	//chipField.change(function(){resetlines()});

	function resetlines(){
		sessionStorage.removeItem('Species');
		sessionStorage.removeItem('Chromosome');
		localStorage.removeItem("QueryCultivars");
		for ( var i = 0, l = document.getElementById("QueryCultivars").options.length, o; i < l; i++ ) {
			o = document.getElementById("QueryCultivars").options[i];
			o.selected = true;
                }
		removeSelectValues(document.getElementById("QueryCultivars"));
		}
	
	function getSelectValues(select) {
		var myresult = new Array();
		var options = select && select.options;
		var opt;
		var content = document.getElementById("QueryCultivars");
		var conoptions = content && content.options;
		for (var i=0, iLen=options.length; i<iLen; i++) {
    			opt = options[i];
    			if (opt.selected) {
				if (content == null) {
					myresult.push(opt.value);
				} else {
					var flag = true;
					var inc = 0
					while (conoptions.length > inc) {
						conopt = conoptions[inc];
						if (conopt.text == opt.text) {
							flag = false
						}
						inc = inc + 1
					}
					if (flag == true) {
					 myresult.push(opt.value);
					}
    				}	
  			}
		}
		for (x=0;x<myresult.length;x++) {
			var option = document.createElement("option");
			option.text=myresult[x];
			document.getElementById("QueryCultivars").add(option);
		}
	}

	function sortQueryCultivars() {
		var list = document.getElementById("QueryCultivars");
		var tmpAry = new Array();
		for (var i=0;i<list.options.length;i++) {
			tmpAry[i] = new Array();
			tmpAry[i][0] = list.options[i].text;
			tmpAry[i][1] = list.options[i].value;
		}
		tmpAry.sort(); //alphabetic sort
		while (list.options.length > 0) {
			list.options[0] = null;
		}
		for (var i=0;i<tmpAry.length;i++) {
			var op = new Option(tmpAry[i][0], tmpAry[i][1]);
			list.options[i] = op;
		}
		return;

	}

	function removeSelectValues(select) {
		var options = select.options;
		var opt;
		//start loop from last index
		//this avoids accidental modifications of index positions when removing items
		for (var i=options.length - 1; i>=0; i--) {
    			opt = options[i];
    			if (opt.selected) {
				document.getElementById("QueryCultivars").remove(i)
			}
		}
	}
	//Adds species to form based on value in chip field
	function setSelectedIndex(s, i) {

		s.options[i-1].selected = true;
		return;

	}

	function SpeciesCheck() {
		speciesField.empty();
		var chip = chipField.val();
		var speciesToUse = chipsWithSpecies[chip];
		var speciesToUse = speciesToUse.sort();
		for(var i=0;i < speciesToUse.length;i++){
			var species = speciesToUse[i]
				speciesField.append(new Option(species,species));
		}
		setSelectedIndex(document.getElementById("Specie"),1);
		CultivarCheck();

	}

	function CultivarCheck(){
		var species = speciesField.val()
		var newCultivars = []
		var newChromosomes = [] 
		var chromsToUse = chromosomesWithSpecies[species]
		var chromsToUse = chromsToUse.sort()
		var cultivarsToUse = speciesWithCultivars[species]
//		var chromosomes = []
		chrList.empty()	
		cultivarsField.empty()
//		var matchingChr = []
//		pattern = new RegExp(inputChr)
		var i = 0
/*		var brassica_pfx = "Brassica"
		var wheat_pfx = "Triticum"

		if(species.substring(0, wheat_pfx.length) === wheat_pfx){
			var chromosomes = wheatchr;
			var chromsToUse = chromosomes;
		} else if(species.substring(0, brassica_pfx.length) === brassica_pfx){  
			var chromosomes = canolachr;
			var chromsToUse = chromosomes;
		}*/
		if(cultivarsToUse)
		{
			for(var i in cultivarsToUse){
				newCultivars.push(cultivarsToUse[i])
			}
		}

		var newCultivars = newCultivars.sort();

		for(var i=0;i < newCultivars.length;i++){
			var cultivar = newCultivars[i]
				cultivarsField.append(new Option(cultivar,cultivar));
		}

		if(chromsToUse)
		{
			for(var i in chromsToUse){
				newChromosomes.push(chromsToUse[i])
			}
		}

		for(var i=0;i < newChromosomes.length;i++){
			var chr = newChromosomes[i]
				chrList.append(new Option(chr,chr));
		}
		
		var selectedChromosome = sessionStorage.getItem('Chromosome');

		if (selectedChromosome) {
		chrList.value = selectedChromosome;
		SelectElement("ChromDrop",selectedChromosome)
		}


	}

	resultRow.click(function(e){
		modal.style.display = "block";
			chipNameField.text(results[$(this).attr('id')][0])
			speciesbox.text(results[$(this).attr('id')][1])
			cultivarField.text(results[$(this).attr('id')][2])
			accessionField.text(results[$(this).attr('id')][3])
			snpIdField.text(results[$(this).attr('id')][4])
			chromosomeField.text(results[$(this).attr('id')][7])
			referenceSNPField.text(results[$(this).attr('id')][5])
			referenceStrand.text(results[$(this).attr('id')][6])
			coordinate.text(results[$(this).attr('id')][8])
			genotypeAccession.text(results[$(this).attr('id')][9])
			sourceSeq.text(results[$(this).attr('id')][10]) 
			var current_species = results[$(this).attr('id')][1]
			var coordinateInt=parseInt(results[$(this).attr('id')][8])
			var start=coordinateInt-200
			var end=coordinateInt+200


			if(results[$(this).attr('id')][1] !== "Triticum aestivum RefSeq v1 and Pan"){

				document.getElementById("snpref").href="http://dx.doi.org/"+results[$(this).attr('id')][11];
				document.getElementById("snpref").innerHTML=results[$(this).attr('id')][11];

			} else {
				snpref = $('#'+informationBoxId+" #snpref")
				snpref.text(results[$(this).attr('id')][11])
			}

			if(results[$(this).attr('id')][1] === "Triticum aestivum RefSeq v1 and Pan"){
				if(results[$(this).attr('id')][7] === "Pan_BP_CH"){
					document.getElementById("gbrowseLink").href="NA";
					document.getElementById("gbrowseLink").innerHTML="NA";
				} else {
					document.getElementById("gbrowseLink").href=gbrowseLink+results[$(this).attr('id')][7]+"%3A"+start+".."+end+"&tracks=DNA%2CHighConfidenceGenesv1.1%2CINFINIUM90K_SUMMARY%2CAll%20Accessions%20with%20SNP%20Eff&highlight=";
					document.getElementById("gbrowseLink").innerHTML=results[$(this).attr('id')][7]+":"+results[$(this).attr('id')][8];
					}

			} else if(results[$(this).attr('id')][1] === "Brassica napus Darmor v81"){ //handle Brassica chr naming scheme 
				if(results[$(this).attr('id')][7] === "Unplaced"){
					document.getElementById("gbrowseLink").href=gbrowseLink+"?name="+results[$(this).attr('id')][7]+"_contigs_v81"+":"+start+".."+end;
					document.getElementById("gbrowseLink").innerHTML=results[$(this).attr('id')][7]+":"+results[$(this).attr('id')][8];
				} else {
					document.getElementById("gbrowseLink").href=gbrowseLink+"?name="+"chr"+results[$(this).attr('id')][7]+"_contigs_placed_v81"+":"+start+".."+end;
					document.getElementById("gbrowseLink").innerHTML=results[$(this).attr('id')][7]+":"+results[$(this).attr('id')][8];
					}  

			} else if(results[$(this).attr('id')][1] === "Brassica napus Darmor v41"){  
					if(typeof gbrowseLink === "undefined" || gbrowseLink === "NA" || gbrowseLink === "XXX"){
						document.getElementById("gbrowseLink").href="NA";
						document.getElementById("gbrowseLink").innerHTML="NA";
					} else {
						document.getElementById("gbrowseLink").href=gbrowseLink+"?name="+results[$(this).attr('id')][7];
						document.getElementById("gbrowseLink").innerHTML=results[$(this).attr('id')][7];
					}
					}

			 else if(results[$(this).attr('id')][1] === "Brassica oleracea v2.1"){
				if(results[$(this).attr('id')][7] === "Unplaced"){
					document.getElementById("gbrowseLink").href="NA";
					document.getElementById("gbrowseLink").innerHTML="NA";
				} else {
					document.getElementById("gbrowseLink").href=gbrowseLink+"?name="+results[$(this).attr('id')][7]+":"+start+".."+end;
					document.getElementById("gbrowseLink").innerHTML=results[$(this).attr('id')][7]+":"+results[$(this).attr('id')][8];
					}
			} else if(results[$(this).attr('id')][1] === "Brassica rapa v3"){
				if(results[$(this).attr('id')][7] === "Unplaced" || typeof gbrowseLink === "undefined" || gbrowseLink === "NA" || gbrowseLink === "XXX"){
					document.getElementById("gbrowseLink").href="NA";
					document.getElementById("gbrowseLink").innerHTML="NA";
				} else {
					document.getElementById("gbrowseLink").href=gbrowseLink+"?name="+"X"+results[$(this).attr('id')][7]+"_v3.0%3A"+start+".."+end;
					document.getElementById("gbrowseLink").innerHTML=results[$(this).attr('id')][7]+":"+results[$(this).attr('id')][8];
					}
			} else if(results[$(this).attr('id')][1] === "Brassica juncea v1.5"){
				document.getElementById("gbrowseLink").href=gbrowseLink;
				document.getElementById("gbrowseLink").innerHTML="BRAD Genome Browser";
			}
			
	}) 
	span.onclick = function() {
		modal.style.display = "none";
	}
	window.onclick = function(event) {
		if (event.target == modal) {
        		modal.style.display = "none";
    		}
	}
}  );
