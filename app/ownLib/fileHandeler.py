import os

#Takes filepath and creates a file
#Writes filebody into file
def putToFile(path,fileBody):
	path = checkPath(path)
	fileToWrite = open(path,'w')
	fileToWrite.write(str(fileBody))
	fileToWrite.close()

#Checks if a file already excists at given filepath and renames it with path(x).fileExtension
def checkPath(path):
	#splitext keeps the full name and real extension even when folders or file names contain dots
	path, fileExtension = os.path.splitext(path)
	i = 0
	tempPath = path
	while(os.path.isfile(tempPath+fileExtension)):
		i = i + 1
		tempPath = path+"("+str(i)+")"
	tempPath = tempPath + fileExtension
	return tempPath
