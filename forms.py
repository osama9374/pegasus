from tika import parser,detector
import time
from dicttoxml import dicttoxml
import sys
from xml.dom.minidom import parseString
import glob
import os
import pysolr
from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
solr = pysolr.Solr('http://localhost:8983/solr/', timeout=50) 
path = ""
# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'
 
class ReusableForm(Form):

    name = TextField('Name:', validators=[validators.required()])
 
 
@app.route("/", methods=['GET', 'POST'])
def hello():
	form = ReusableForm(request.form)
	#test = ['osama',21,'hello']
	#print form.errors
	if request.method == 'GET':
		return render_template('form.html', form=form)

		#name = request.form['name']
        #print name
 
        # if form.validate():
            # Save the comment here.
         #   flash('Hello ' + name)
        # else:
            # flash('Error: All the form fields are required. ')
 

@app.route("/start", methods=['GET', 'POST'])
def start():
	form = ReusableForm(request.form)
	#solr = pysolr.Solr('http://localhost:8983/solr/', timeout=10)

	reload(sys)
	#so that we don't get unicode encode error
	sys.setdefaultencoding('utf-8')
	#path = "C:\\Users\\HP\\Desktop\\test_data\\"
	global path
	path = request.form['folder']
	
	directory = os.listdir(path)
	start = time.time()
	print(directory)
	count = 0;
	type_dict = dict()
	for fpath in directory:
		#parsing through file to extract metadata and content
		file_path = path + fpath
		parsed = parser.from_file(file_path)

		#detecting file type
		file_type = detector.from_file(file_path)
		print(file_type)
		if(file_type) in type_dict:
			type_dict[file_type].append(directory[count])
		else:
			type_dict[file_type] = [directory[count]]	
		parsed['id'] = str(count)

		#converting output from python dict to xml
		#xml = dicttoxml(parsed)
		#dic = {'id':str(count),"content":parsed['content']}
		#dic.update(parsed['metadata']
		if(parsed['content'] is None):
			#print "working"
			parsed['content']="crime"

		solr.add([{"id":str(count),"content":parsed['content'],"payloads":parsed['metadata']}])
        #{"id":str(count),"content":parsed['content']}

		#formatting xml using xml.dom.minidom
		#dom = parseString(xml)
		#pretty_output = dom.toprettyxml()
		count = count + 1

		#creating, writing(xml), closing file
		#f = open(str(count)+ 'webpages','w+')
		#f.write(pretty_output)
		#f.close()

	#time elapsed
	#avg time between 0.5 and 0.7 seconds
	#specs: 3.8 GB RAM, i5-4200U, 1.6GHZ x 4
	end = time.time()
	#print(parsed['metadata'].keys())
	t_time  = end - start
	print(t_time)
	#result = solr.search("pegasus")
	#for r in result:
	#	id = r['id']
	#print directory[int(r['id'])]
	#print path+directory[int(r['id'])]
	print type_dict
	return render_template('form2.html', form=form, type=type_dict)

@app.route("/form2", methods=['GET', 'POST'])
def second():
    form = ReusableForm(request.form)

    if request.method == 'GET':
		return render_template('form2.html', form=form)

@app.route("/form3",methods=['GET', 'POST'])
def third():
	form = ReusableForm(request.form)
	directory = os.listdir(path)
	result = solr.search(request.form['nm'])
	files = []
	for r in result:
		id = r['id']
		files.append(directory[int(r['id'])])
	#ans = path+directory[int(r['id'])]
	return render_template('last.html',path = path, files = files)



 
if __name__ == "__main__":
    app.run()
