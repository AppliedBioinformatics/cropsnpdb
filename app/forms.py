from flask_wtf import FlaskForm
from dataHandeler import getAllCultivarsAsChoice, getAllChipsAsChoice,getAllSpeciesAsChoice,getAllSNPArraysAsChoice
from wtforms import SelectMultipleField,SelectField,StringField,FileField,HiddenField,validators
from wtforms.validators import InputRequired
from wtforms.fields.html5 import EmailField

#Generates input field to upload file
#Generates select field to select if the input is csv or raw
class SNPSubmit(FlaskForm):
	Email = EmailField('Email', [validators.DataRequired(), validators.Email()])
	SNPArray = SelectField('SNPArray',choices=getAllSNPArraysAsChoice())
	SNPFile = FileField('SNPFile')
	CultivarFile = FileField('CultivarFile')		
	qualityFile = FileField('qualityFile')
     
	@classmethod
	def new(self):
		form = self()
		form.SNPArray.choices = getAllSNPArraysAsChoice()
		return form

#Generates string field to give search query
#Generates select field to select if the query is a accession or a snpid
class SNPSearch(FlaskForm):
	Chip = SelectField('Chip',choices=getAllChipsAsChoice())
	Specie = SelectField('Specie',choices=[])
#	Specie = SelectField('Specie',choices=getAllSpeciesAsChoice())
	Cultivars = SelectMultipleField('Cultivars',choices=[])
	QueryCultivars = SelectMultipleField('QueryCultivars',choices=[])
	ChromDrop = SelectField('ChromDrop', choices=[])
	CoordinationFrom = StringField('CoordinationFrom')
	CoordinationTo = StringField('CoordinationTo')
