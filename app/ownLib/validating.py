import re
#Looks if file is not empty and if it has allowed extension
def fileIsLegit(filename):
        if filename == "" or not allowed_file(filename):
                return False
        else:
                return True
#Checks if a given file has an allowed extension 
#Allowed extensions in config file
def allowed_file(filename,Allowed_Extensions=["csv"]):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Allowed_Extensions                       
