import re
import time
import os
import sys
from app import app
from fileHandeler import putToFile, checkPath
from mysqlQuerys import SNPArrayIdWithName,BuildWithSpecie,getChromWithSpeciesID,getAllSNPsWithSNPArrayId,getAllAccessions,getSNPData,addAccessionSNPRelation,AccessionWithAccession,CultivarIdWithCultivar,SpeciesWithChipId,SpecieIdWithSpecie,SNPTableIdWithSNPId,addAccession,addCultivar,getChromosomeWithSNPTableId,CultivarsWithSpecieId,getAllSNPArrays,getAllChips as Chips,getAllSpecies as Species,getAllCultivars as Cult,AccessionWithAccession as AWA,getCultivarWithCultivarName,AccessionsWithCultivarId,AccessionSNPRelationWithIdAccession,SNPWithSNPTableId

#Looks if input has data
#If the input has data uses sql script to retrieve data
def useInputToSearchv2(species,cultivars,chromosoms,coordinationFrom,coordinationTo):
	if cultivars == [] or chromosoms == [] or coordinationFrom == "" or coordinationTo == "":
		return "" 
	speciesID = SpecieIdWithSpecie(species)[0][0] 
	speciesBuild = BuildWithSpecie(species)[0][0]
	speciesName = species
	import vcfBackend
	if vcfBackend.handles(species):
		return vcfBackend.search(species,cultivars,chromosoms,coordinationFrom,coordinationTo)
	return getSNPData(speciesName,speciesID,speciesBuild,cultivars,chromosoms,coordinationFrom,coordinationTo)

def CapSearchv2(cultivars,chromosoms,coordinationFrom,coordinationTo,cap):
        if cultivars == [] or chromosoms == [] or coordinationFrom == "" or coordinationTo == "":
                return ""
        return getSNPData(cultivars,chromosoms,coordinationFrom,coordinationTo)[:cap]
		 	
#Retrieves cultivars and makes it a choice
def getAllCultivarsAsChoice():
	listOfCultivars = []
	cultivars = Cult()
	for cultivar in cultivars:
		listOfCultivars.append(cultivar[0])
	cultivarsAsChoices = listToChoices(listOfCultivars)
	return cultivarsAsChoices

def getAllSNPArraysAsChoice():
	listOfSNPArrays = []
	SNPArrays = getAllSNPArrays()
	for SNPArray in SNPArrays:
		listOfSNPArrays.append(SNPArray[0])
	SNPArraysAsChoices = listToChoices(listOfSNPArrays)
	return SNPArraysAsChoices
	

def getAllSpeciesAsChoice():
	species = Species()
	listOfSpecies = []
	for specie in species:
		listOfSpecies.append(specie[1])
	speciesAsChoices = listToChoices(listOfSpecies)
	return speciesAsChoices

def getAllChipsAsChoice():
	chips  = Chips()
	listOfChips = []
	for chip in chips:
		listOfChips.append(chip[1])
	chipsAsChoices = listToChoices(listOfChips)
	return chipsAsChoices

def getDicChipsWithSpecies():
	chipsWithSpecies={}
	chips = Chips()
	for chip in chips:
		speciesOfChip = []
		species = SpeciesWithChipId(chip[0])
		for sp in species:
			speciesOfChip.append(sp[1])
		chipsWithSpecies[chip[1]]=speciesOfChip
	return chipsWithSpecies

def getDicChrWithSpecies():
	species = Species()
	chromWithSpecies = {}
	for sp in species:
		chrlist = []
		speciesBuild = BuildWithSpecie(sp[1])
		chroms = getChromWithSpeciesID(sp[0],speciesBuild)
		for chrom in chroms:
			chrlist.append(chrom[0])
		chromWithSpecies[sp[1]]=chrlist
	return chromWithSpecies

#Retrieves all species and cultivars and puts them in a dic
#{specie:[cultivar,cultivar]}
def getDicSpeciesWithCultivar():
	speciesWithCultivars={}
	species = Species()
	for specie in species:
		cultivarsOfSpecie = []
		cultivars = CultivarsWithSpecieId(specie[0])
		if len(cultivars) > 5000:
			#too many to embed in the page: the Search page looks these up as the user types
			speciesWithCultivars[specie[1]]=['__REMOTE__']
			continue
		for cultivar in cultivars:	
			cultivarsOfSpecie.append(cultivar[1])
		speciesWithCultivars[specie[1]]=cultivarsOfSpecie
	return speciesWithCultivars

def listToChoices(listToUse):
	choices = []
	for item in listToUse:
		choice =(item,item)
		choices.append(choice)
	return choices

def sorted_nicely(list): 
	""" Sort the given iterable in the way that humans expect.""" 
	convert = lambda text: int(text) if text.isdigit() else text 
	alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
	return sorted(list, key = alphanum_key)
