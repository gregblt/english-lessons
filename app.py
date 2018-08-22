#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 17 12:25:50 2018

@author: gregory
"""
import os.path
import json
from flask import Flask, send_from_directory, request
app = Flask(__name__)
db=[]
with open('./test.json','r') as f:
	content=f.read()
	print(content)
	db=json.loads(content)

configuration={}
with open('./config.json','r') as f:
	content=f.read()
	print(content)
	configuration=json.loads(content)

import pdfkit

from bs4 import BeautifulSoup

style="""
.TFtableCol{
	border-collapse:collapse; 
    margin: 20px;
    width:90%;
}
.TFtableCol th{ 
	text-align: center
	padding:7px; border:black 1px solid;
    background-color :#4e95f4;
}

.TFtableCol td{ 
	padding:7px; border:black 1px solid;
	word-wrap: keep-all;        
    text-overflow:clip;
}

"""


@app.route('/')
def root():
    print("hello")
    return app.send_static_file('index.html')

@app.route('/db')
def get_db():
    print("hello")
    response = send_from_directory(directory="./", filename='test.json')
    return response

    
@app.route('/update_student', methods=['POST'])
def update_student():
    print(request.get_json()['id'])
    sid=request.get_json()['id']
    sname=request.get_json()['name']
    sdata=request.get_json()['data']
    print(str(sdata))
    file="./static/docs/html/Summary/"+sname.replace(" ","_")+".html"
    filepdf="./static/docs//pdf/Summary/"+sname.replace(" ","_")+".pdf"
    file_pronunciation="./static/docs//html/Pronunciation/"+sname.replace(" ","_")+"_pronunciation"
    file_feedback="./static/docs/html/Feedback/"+sname.replace(" ","_")+"_feedback"
    file_voc="./static/docs/html/Vocabulary/"+sname.replace(" ","_")+"_voc"
    file_pronunciation_pdf="./static/docs/pdf/Pronunciation/"+sname.replace(" ","_")+"_pronunciation"
    file_feedback_pdf="./static/docs/pdf/Feedback/"+sname.replace(" ","_")+"_feedback"
    file_voc_pdf="./static/docs/pdf/Vocabulary/"+sname.replace(" ","_")+"_voc"
    

#        html="<h1>"+sname+"</h1>"
#        with open(file,'w') as f:
#            f.write(html)
    
    header="""<head><style>
    """+style+"""
    </style></head>"""

    body_open="""<body style="margin: 10px;font-family: 'Montserrat', sans-serif;"><h1>"""+sname+"</h1>"
    body_close="""</body>"""

    body=""
    body_feedback=""
    pronunciation=""
    row_voc=""

    ## Init body
    table_pronunciation="""<table class="TFtableCol">
        <tr style="background-color:#4e95f4;" >
            <th>Word</th><th>Pronunciation</th>
        </tr>"""
    table_voc="""<table class="TFtableCol">
            <tr style="background-color:#4e95f4;">
                <th>Vocabulary</th><th>P. of S.</th><th>Meaning</th>
            </tr>"""


    for lesson in sdata:
        # Summary
        title="""<table class="TFtableCol">
        <tr style="background-color:#4e95f4;" >
            <th>Lesson date</th><th>Focus</th><th>Material used</th>
        </tr>
        <tr> 
            <td>%s</td><td>%s</td><td>%s</td> 
        </tr></table>""" % (lesson['date'],lesson['data'][0]['focus'],lesson['data'][0]['materials'])

        voc="""<table class="TFtableCol">
            <tr style="background-color:#4e95f4;" >
                <th>Vocabulary</th><th>P. of S.</th><th>Meaning</th>
            </tr>"""

        mistake="""<table class="TFtableCol">
            <tr style="background-color:#4e95f4;">
                <th>Mistake</th><th>Correction</th>
            </tr>"""

        sound="""<table class="TFtableCol">
            <tr style="background-color:#4e95f4;" >
                <th>Pronunciation</th><th>Sound</th>
            </tr>"""

        for val in lesson['data']:
            # Summary
            voc+="""
            <tr> 
                <td>%s</td><td>%s</td><td>%s</td> 
            </tr>""" % (val['voc'],val['pos'],val['def'])
            row_voc+="""
            <tr> 
                <td>%s</td><td>%s</td><td>%s</td> 
            </tr>""" % (val['voc'],val['pos'],val['def'])
            mistake+="""        
            <tr>
                <td>%s</td><td>%s</td> 
            </tr>""" % (val['mistake'],val['correction'])
            sound+="""<tr><td>%s</td><td>%s</td> 
            </tr>""" % (val['pronunciation'],val['sound'])
            # Pronunciation
            pronunciation+="""<tr><td>%s</td><td>%s</td> 
            </tr>""" % (val['voc'],val['pronunciation'])

        # Close tables
        voc+="""</table>"""
        mistake+="""</table>"""
        sound+="""</table>"""

        # Add feedback table
        feedback="""<table class="TFtableCol">           
        <tr style="background-color:#4e95f4;">
            <th >Feedback</th>
        </tr>        <td>%s</td>
        </tr></table>""" % (lesson['data'][0]['feedback'])

        body+='<div style="border-bottom: 5px solid black">'+title+mistake+voc+sound+feedback+"</div>"

        body_feedback+='<div style="border-bottom: 5px solid black">'+title+feedback+"</div>"

    pronunciation+="""</table>"""
    row_voc+="""</table>"""
    
    
    if(os.path.isfile(file_pronunciation+".html")):
        with open(file_pronunciation+".html",'r') as f:
            html=f.read()
            new_html=header+body_open+table_pronunciation+pronunciation+body_close
            new_soup=BeautifulSoup(new_html,"lxml")
            soup = BeautifulSoup(html,"lxml")
            table = soup.findChildren('table')
            rows = table[0].findChildren(['tr'])
            rows.pop(0)
            for val in rows:
                new_soup.table.append(val)
            html=new_soup.prettify()
                
    else:
        html=header+body_open+table_pronunciation+pronunciation+body_close
    
    with open(file_pronunciation+".html",'w') as f:
        f.write(html)
        
    if(os.path.isfile(file_voc+".html")):
        with open(file_voc+".html",'r') as f:
            html=f.read()
            new_html=header+body_open+table_voc+row_voc+body_close
            new_soup=BeautifulSoup(new_html,"lxml")
            soup = BeautifulSoup(html,"lxml")
            table = soup.findChildren('table')
            rows = table[0].findChildren(['tr'])
            rows.pop(0)
            for val in rows:
                new_soup.table.append(val)
            html=new_soup.prettify()
                
    else:
        html=header+body_open+table_voc+row_voc+body_close
    
    with open(file_voc+".html",'w') as f:
        f.write(html)
        
    if(os.path.isfile(file)):
        with open(file,'r') as f:
            html=f.read()
            new_html=header+body_open+body+body_close
            new_soup=BeautifulSoup(new_html,"lxml")
            soup = BeautifulSoup(html,"lxml")
            body = new_soup.findChildren('body')[0]      
            title = body.find('h1')
            title.extract()
            toAdd=BeautifulSoup(body.decode_contents(),"lxml")
            soup.find('h1').insert_after(toAdd)
            html=soup.prettify()
                
    else:
        html=header+body_open+body+body_close
    
    with open(file,'w') as f:
        f.write(html)

    if(os.path.isfile(file_feedback+".html")):
        with open(file_feedback+".html",'r') as f:
            html=f.read()
            new_html=header+body_open+body_feedback+body_close
            new_soup=BeautifulSoup(new_html,"lxml")
            soup = BeautifulSoup(html,"lxml")
            body = new_soup.findChildren('body')[0]      
            title = body.find('h1')
            title.extract()
            toAdd=BeautifulSoup(body.decode_contents(),"lxml")
            soup.find('h1').insert_after(toAdd)
            html=soup.prettify()
                
    else:
        html=header+body_open+body_feedback+body_close

    with open(file_feedback+".html",'w') as f:
        f.write(html) 
        
    options = {
    'margin-top': '0.75in',
    'margin-right': '0.75in',
    'margin-bottom': '0.75in',
    'margin-left': '0.75in',
    'encoding': "UTF-8",
    'no-outline': None
    }   
	
    config = pdfkit.configuration(wkhtmltopdf=configuration["wkhtmltopdf"])

    pdfkit.from_file(file, filepdf,options=options,configuration=config)
    pdfkit.from_file(file_pronunciation+".html", file_pronunciation_pdf+".pdf",options=options,configuration=config)
    pdfkit.from_file(file_voc+".html", file_voc_pdf+".pdf",options=options,configuration=config)
    pdfkit.from_file(file_feedback+".html",file_feedback_pdf+".pdf",options=options,configuration=config)


    
    def find(lst, key, value):
        for i, dic in enumerate(lst):
            if dic[key] == value:
                return i
        return -1  

    idx=find(db,'id',sid)
    print(idx)
    if idx==-1:
        db.append({'id':sid,'row':request.get_json()['new_entries']+1})
        idx=len(db)-1
    else:
        db[idx]['row']=db[idx]['row']+request.get_json()['new_entries']
            
    with open('./test.json','w') as f:
        f.write(json.dumps(db))    
		
    response = app.response_class(
    response=json.dumps(db[idx]),
    status=200,
    mimetype='application/json'
    )
    return response

if __name__ == "__main__":

    app.run(port=8000)

