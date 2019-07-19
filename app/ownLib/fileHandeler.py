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
	pathAndFileExtension = path.split('.')
	path = pathAndFileExtension[0]
	fileExtension = '.'+pathAndFileExtension[1]
	i = 0
	tempPath = path
	while(os.path.isfile(tempPath+fileExtension)):
		i = i + 1
		tempPath = path+"("+str(i)+")"
	tempPath = tempPath + fileExtension
	return tempPath
