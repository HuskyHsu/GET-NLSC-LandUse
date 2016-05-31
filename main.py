import requests
import json
import ast
import pyprind

#範圍與step以及資料年份
Xmin = 211000
Xmax = 211500
Ymin = 2673500
Ymax = 2674000
step = 100
LandUseDataYear = "LU102"

bar = pyprind.ProgBar(len(range(Xmin, Xmax, step))*len(range(Ymin, Ymax, step)), width=70, monitor=True, bar_char='█')

#API位置
url  ="http://whgis.nlsc.gov.tw/WS/MapDataProvider.asmx"
#API headers
headers = {'content-type': 'text/xml'}
#POST data
body = """<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:s="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <SOAP-ENV:Body>
    <tns:SearchLandUseAttribute xmlns:tns="http://gis.fcu.com.tw/">
      <tns:pointX>$pointX$</tns:pointX>
      <tns:pointY>$pointY$</tns:pointY>
      <tns:buffer>16</tns:buffer>
    </tns:SearchLandUseAttribute>
  </SOAP-ENV:Body>
</SOAP-ENV:Envelope>"""

#存放 ObjectID
ObjectID = []
#存放 geojsonData
geojsonData = []

for pointX in range(Xmin, Xmax, step):
    for pointY in range(Ymin, Ymax, step):

        response = requests.post(url,data=body.replace('$pointX$',str(pointX)).replace('$pointY$',str(pointY)),headers=headers)

        response.encoding = 'utf-8'

        data = response.text

        data = data.replace('<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"><soap:Body><SearchLandUseAttributeResponse xmlns="http://gis.fcu.com.tw/"><SearchLandUseAttributeResult>', '')
        data = data.replace('</SearchLandUseAttributeResult></SearchLandUseAttributeResponse></soap:Body></soap:Envelope>', '')
        data = data.replace('\\r\\n','')
        data = data.replace(' ','')
        data = json.loads(data)


        for item in data:
            if item["LandUseDataYear"] == LandUseDataYear and item["ObjectID"] not in ObjectID:
                geojsonData.append({"type" : "Feature","geometry" : {"type" : "Polygon","coordinates" : ast.literal_eval(item['Geometry'])},"properties" :{"ObjectID" : item["ObjectID"],"LandUseDataYear" : item["LandUseDataYear"],"ClassName1" : item["ClassName1"],"ClassName2" : item["ClassName2"],"ClassName3" : item["ClassName3"],"Description" : item["Description"],"DataCreateDate" : item["DataCreateDate"],"DataSurveyStartDate" : item["DataSurveyStartDate"],"DataSurveyEndDate" : item["DataSurveyEndDate"],"ProduceUnit" : item["ProduceUnit"]}})
                ObjectID.append(item["ObjectID"])
        
        bar.update()
        #print(pointX)
        
geojsonData = {"type" : "FeatureCollection","features" :geojsonData}

#, ensure_ascii=False
with open('data2.json', 'w') as outfile:
    json.dump(geojsonData, outfile)

