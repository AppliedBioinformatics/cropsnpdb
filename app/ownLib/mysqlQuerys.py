from app import app
from flaskext.mysql import MySQL
#from flask_mysqldb import MySQL

#Database connection
#The mySQL query joins columns in database based on the condition WHERE, which takes input from the data_handler.py eg., cultivars,chromosomes,coordinationFrom etc.
mysql = MySQL(app)
#def getSNPData(cultivars,chromosomes,coordinationFrom,coordinationTo):
#	curCon = getCursor()
#	con=curCon[1]
#	cur=curCon[0]
#	cur.execute("SELECT SNPArray.SNPArrayName,Specie.SpecieName,Cultivar.CultivarName,Accession.Accession,SNP.SNPid,SNP.Chromosome,SNP.Reference,SNP.Strand,SNP.Coordination,Accession_has_SNP.Genotype,SNP.SourceSeq FROM mydb.SNP INNER JOIN mydb.SNPArray ON SNP.SNPArray_idSNPArray=SNPArray.idSNPArray INNER JOIN mydb.Accession_has_SNP ON SNP.SNPTableid = Accession_has_SNP.SNP_SNPTableid INNER JOIN mydb.Accession ON Accession_has_SNP.Accession_idAccession = Accession.idAccession INNER JOIN mydb.Cultivar ON Accession.Cultivar_idCultivar = Cultivar.idCultivar left join mydb.Specie on Cultivar.Specie_idSpecie = Specie.idSpecie WHERE Cultivar.CultivarName in %s AND %s <= SNP.Coordination AND %s >= SNP.Coordination AND SNP.Chromosome = %s",(cultivars,coordinationFrom,coordinationTo,chromosomes))
#	return getResult(cur,con)

def getSNPData(speciesName,speciesID,speciesBuild,cultivars,chromosomes,coordinationFrom,coordinationTo):
	curCon = getCursor()
	con=curCon[1]
	cur=curCon[0]
	#cur.execute("SELECT SNPArray.SNPArrayName,Specie.SpecieName,Cultivar.CultivarName,Accession.Accession,SNP.SNPid,SNP.Reference,SNP.Strand,SNP_Coordinates.Chromosome,SNP_Coordinates.Coordinate,Accession_has_SNP.Genotype,Reference.DOI FROM mydb.SNP INNER JOIN mydb.SNPArray ON SNP.SNPArray_idSNPArray=SNPArray.idSNPArray INNER JOIN mydb.SNP_Coordinates ON SNP.SNPid = SNP_Coordinates.SNP_SNPid INNER JOIN mydb.Accession_has_SNP ON SNP.SNPTableid = Accession_has_SNP.SNP_SNPTableid INNER JOIN mydb.Accession ON Accession_has_SNP.Accession_idAccession = Accession.idAccession INNER JOIN mydb.Cultivar ON Accession.Cultivar_idCultivar = Cultivar.idCultivar INNER JOIN mydb.Reference ON Accession.Accession_RefID = Reference.RefID left join mydb.Specie on Cultivar.Specie_idSpecie = Specie.idSpecie WHERE Cultivar.CultivarName in %s AND %s <= SNP_Coordinates.Coordinate AND %s >= SNP_Coordinates.Coordinate AND SNP_Coordinates.Chromosome = %s AND SNP_Coordinates.Specie_idSpecie = %s AND SNP_Coordinates.Specie_Build = %s AND Specie.SpecieName = %s",(cultivars,coordinationFrom,coordinationTo,chromosomes,speciesID,speciesBuild, speciesName))
	cur.execute("SELECT SNPArray.SNPArrayName,Specie.SpecieName,Cultivar.CultivarName,Accession.Accession,SNP.SNPid,SNP.Reference,SNP.Strand,SNP_Coordinates.Chromosome,SNP_Coordinates.Coordinate,Accession_has_SNP.Genotype,Reference.DOI FROM snpdb.SNP INNER JOIN snpdb.SNPArray ON SNP.SNPArray_idSNPArray=SNPArray.idSNPArray INNER JOIN snpdb.SNP_Coordinates ON SNP.SNPid = SNP_Coordinates.SNP_SNPid INNER JOIN snpdb.Accession_has_SNP ON SNP.SNPTableid = Accession_has_SNP.SNP_SNPTableid INNER JOIN snpdb.Accession ON Accession_has_SNP.Accession_idAccession = Accession.idAccession INNER JOIN snpdb.Cultivar ON Accession.Cultivar_idCultivar = Cultivar.idCultivar INNER JOIN snpdb.Reference ON Accession.Accession_RefID = Reference.RefID left join snpdb.Specie on Cultivar.Specie_idSpecie = Specie.idSpecie WHERE Cultivar.CultivarName in %s AND %s <= SNP_Coordinates.Coordinate AND %s >= SNP_Coordinates.Coordinate AND SNP_Coordinates.Chromosome = %s AND SNP_Coordinates.Specie_idSpecie = %s AND SNP_Coordinates.Specie_Build = %s AND Specie.SpecieName = %s",(cultivars,coordinationFrom,coordinationTo,chromosomes,speciesID,speciesBuild, speciesName))
	return getResult(cur,con)

#Opens connection and makes cursor 
def getCursor():
	connection = mysql.connect()
	cursor = connection.cursor()
	return [cursor,connection]

#Closes connection
def getResult(cursor,connection):
	result = cursor.fetchall()
	cursor.close()
	connection.close()
	return result

def CultivarWithId(idCultivar):
	curCon = getCursor()
	cur = curCon[0]
	con = curCon[1]
	cur.execute("SELECT * FROM Cultivar WHERE idCultivar=%s",(idCultivar,))
	return getResult(cur,con)

def CultivarIdWithCultivar(cultivar):
	curCon = getCursor()
	cur = curCon[0]
	con = curCon[1]
	cur.execute("SELECT idCultivar FROM Cultivar WHERE CultivarName=%s",(cultivar,))
	return getResult(cur,con)

def CultivarsWithSpecieId(idSpecie):
	curCon = getCursor()
	cur = curCon[0]
	con = curCon[1]
	cur.execute("SELECT * FROM Cultivar WHERE Specie_idSpecie=%s",(idSpecie,))
	return getResult(cur,con)

def SpeciesWithChipId(chipID):
	curCon = getCursor()
	cur = curCon[0]
	con = curCon[1]
	cur.execute("SELECT * FROM Specie WHERE Specie_idSNPArray=%s",(chipID,))
	return getResult(cur,con)


def getCultivarWithCultivarName(cultivarName):
	curCon = getCursor()
	cur=curCon[0]
	con=curCon[1]
	cur.execute("SELECT * FROM Cultivar WHERE CultivarName=%s",(cultivarName,))
	return getResult(cur,con)

def addCultivars(listOfCultivar):
	curCon = getCursor()
	cur=curCon[0]
	con=curCon[1]
	cur.executemany("INSERT INTO Cultivar VALUES (NULL,%s,%s)",listOfCultivar)
	con.commit()
	cur.close()
	con.close()

def SpecieWithId(idSpecie):
	curCon = getCursor()
	cur=curCon[0]
	con=curCon[1]
	cur.execute("SELECT * FROM Specie WHERE idSpecie=%s",(idSpecie,))
	return getResult(cur,con)

def SpecieIdWithSpecie(specieName):
	curCon = getCursor()
	cur=curCon[0]
	con=curCon[1]
	cur.execute("SELECT idSpecie FROM Specie WHERE SpecieName=%s",(specieName))
	return getResult(cur,con)

def BuildWithSpecie(specieName):
	curCon = getCursor()
	cur=curCon[0]
	con=curCon[1]
	cur.execute("SELECT Build FROM Specie WHERE SpecieName=%s",(specieName))
	return getResult(cur,con)

def getAllSpecies():
	curCon = getCursor()
	cur=curCon[0]
	con=curCon[1]
	cur.execute("SELECT * FROM Specie")
	return getResult(cur,con)

def getAllChips():
	curCon = getCursor()
	cur=curCon[0]
	con=curCon[1]
	cur.execute("SELECT * FROM SNPArray")
	return getResult(cur,con)

def AccessionWithId(idAccession):
	curCon = getCursor()
	cur=curCon[0]
	con=curCon[1]
	cur.execute("SELECT * FROM Accession WHERE idAccession=%s",(idAccession,))
	return getResult(cur,con)

def AccessionWithAccession(accession):
	curCon = getCursor()
	cur=curCon[0]
	con=curCon[1]
	cur.execute("SELECT * FROM Accession WHERE Accession=%s",(accession))
	return getResult(cur,con)

def AccessionsWithCultivarId(cultivarId):
	curCon = getCursor()
	cur=curCon[0]
	con=curCon[1]
	cur.execute("SELECT * FROM Accession WHERE Cultivar_idCultivar=%s",(cultivarId,))
	return getResult(cur,con)

def addAccession(listWithAccession):
	curCon = getCursor()
	cur=curCon[0]
	con=curCon[1]
	cur.executemany("INSERT INTO Accession VALUES(NULL,%s,%s,%s)",listWithAccession)
	con.commit()
	cur.close()
	con.close()	

def addCultivar(Accession,specieId):
	curCon = getCursor()
	cur=curCon[0]
	con=curCon[1]
	cur.execute("INSERT INTO Cultivar VALUES(NULL,%s,%s)",(Accession,specieId,))
	con.commit()
	cur.close()
	con.close()

def AccessionSNPRelationWithIdAccession(idAccession):
	curCon = getCursor()	
	cur=curCon[0]
	con=curCon[1]
	cur.execute("SELECT * FROM Accession_has_SNP WHERE Accession_idAccession=%s",(idAccession,))
	return getResult(cur,con)

def AccessionSNPRelationWithIdSNP(idSNPTable):
	curCon = getCursor()
	cur=curCon[0]
	con=curCon[1]
	cur.execute("SELECT * FROM Accession_has_SNP WHERE SNP_SNPTableId=%s",(idSNPTable,))
	return getResult(cur,con)

def getAllAccessions():
	curCon = getCursor()
	cur=curCon[0]
	con=curCon[1]
	cur.execute("SELECT * FROM Accession")
	return getResult(cur,con)

def addAccessionSNPRelation(SNPRelations):
	curCon = getCursor()
	cur=curCon[0]
	con=curCon[1]
	cur.executemany("INSERT IGNORE INTO Accession_has_SNP VALUES (%s,%s,%s)",SNPRelations)
	con.commit()
	cur.close()
	con.close()

def SNPWithSNPTableId(idSNPTable):
	curCon = getCursor()
	cur=curCon[0]
	con=curCon[1]
	cur.execute("SELECT * FROM SNP WHERE SNPTableid=%s",(idSNPTable,))
	return getResult(cur,con)

def SNPTableIdWithSNPId(SNPId):
	curCon = getCursor()
	cur=curCon[0]
	con=curCon[1]
	cur.execute("SELECT * FROM SNP WHERE SNPid=%s",(SNPId,))
	return getResult(cur,con)

def SNPArrayWithIdSNP(idSNP):
	curCon = getCursor()
	cur=curCon[0]
	con=curCon[1]
	cur.execute("SELECT * FROM SNPArray WHERE idSNP=%s",(idSNP))
	return getResult(cur,con)

def SNPArrayIdWithName(SNPArrayName):
	curCon = getCursor()
	cur=curCon[0]
	con=curCon[1]
	cur.execute("SELECT idSNPArray FROM SNPArray WHERE SNPArrayName=%s",(SNPArrayName))
	return getResult(cur,con)

def getAllSNPArrays():
	curCon = getCursor()
	cur=curCon[0]
	con=curCon[1]
	cur.execute("SELECT SNPArrayName FROM SNPArray")
	return getResult(cur,con)

def getChromosomeWithSNPTableId(SNPTableId):
	curCon = getCursor()
	cur=curCon[0]
	con=curCon[1]
	cur.execute("SELECT Chromosome  FROM SNP WHERE SNPTableid=%s",(SNPTableId,))
	return getResult(cur,con)

def getAllSNPsWithSNPArrayId(SNPArrayId):
	curCon = getCursor()
	cur=curCon[0]
	con=curCon[1]
	cur.execute("SELECT * FROM SNP WHERE SNPArray_idSNPArray=%s",(SNPArrayId,))
	return getResult(cur,con)

def getAllCultivars():
	curCon = getCursor()
	cur=curCon[0]
	con=curCon[1]
	cur.execute("SELECT CultivarName FROM Cultivar")
	return getResult(cur,con)

def getChromWithSpeciesID(SpeciesID,SpeciesBuild):
	curCon = getCursor()
	cur=curCon[0]
	con=curCon[1]
	cur.execute("SELECT DISTINCT(Chromosome) FROM SNP_Coordinates WHERE Specie_idSpecie=%s AND Specie_Build=%s",(SpeciesID,SpeciesBuild,))
	return getResult(cur,con)
