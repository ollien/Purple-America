import cherrypy
import os
import os.path
from glob import glob
import json
from math import floor
from configReader import ConfigReader
staticRoot = os.path.dirname(os.path.abspath(os.getcwd()))
staticPath = os.path.join(os.path.dirname(os.path.abspath(os.getcwd())),'static/')

class PurpleAmericaWeb(object):
	@cherrypy.expose
	def index(self,**kwargs):
		return file(staticPath+'index.html')
class PurpleAmerica(object):
	exposed = True
	@cherrypy.tools.accept(media='text/plain')
	def GET(self,**kwargs):
		configReader = ConfigReader()
		configReader.readKeys()
		keys = configReader.getKeys()
		region = 'USA-county'
		year = '2012'
		if 'region' in kwargs:
			if self.validRegion(kwargs['region']):
				region = kwargs['region']
		elif 'region' in keys:
			if self.validRegion(keys['region']):
				region=keys['region']
		if 'year' in kwargs:
			if self.validYear(int(kwargs['year'])):
				year = kwargs['year']
		elif 'year' in keys:
			if self.validYear(int(keys['year'])):
				year = keys['year']
		areas = {}
		#Read election data
		if 'county' in region:
			files = glob(staticPath+'purple/*'+year+'.txt')
			for fileName in files:
				f = open(fileName,'r')
				areas.update(self.readReigion(f))
				f.close()
		else:
			f = open(staticPath+'purple/'+region+'2012.txt')
			areas.update(self.readReigion(f))
		f = open(staticPath+'purple/'+region+'.txt')
		coords = [{'name':'','color':None,'coords':[]}]
		reading = False
		#Read the region file
		for line in f:
			if not reading:
				#A fix for some file inconsitencies in LA
				line = line.rstrip().lower().replace(' parish','')
				if line in areas:
					coords[-1]['name']=line
					l = areas[line]
					# Baisc Red Green Blue Map
					# if (max(l)==l[0]):
					# 	coords[-1]['color']='blue'
					# elif (max(l)==l[1]):
					# 	coords[-1]['color']='red'
					# elif (max(l)==l[2]):
					# 	coords[-1]['color']='green'
					r = float(l[0])/sum(l)*255
					g = float(l[2])/sum(l)*255
					b = float(l[1])/sum(l)*255
					
					coords[-1]['color'] = '#%02X%02X%02X' % (r,g,b)					
					reading = True
			else:
				if line[0]!='\n':
					coords[-1]['coords'].append([float(item) for item in line.split() if len(line.split())==2])
				else:
					reading = False
					coords.append({'name':'','color':None,'coords':[]})
		f.close()
		#Fix there being elements that are len == 0. String parsing can be a pain.
		c = []
		for dictionary in coords:
			l = []
			for item in dictionary['coords']:
				if len(item)==2:
					l.append(item)
			if len(l)!=0:
				dictionary['coords']=l
				c.append(dictionary)
		coords = list(c)
		lowest = min([item for dictionary in coords for c in dictionary['coords'] for item in c])*-1
		#Convert them to values above 0, round them, and multiply to make it bigger
		for dictionary in coords:
			dictionary['coords'] = [[(item+lowest)*20 for item in c]for c in dictionary['coords']]
		#get the highest y coordinate
		highestY = min([c[1] for dictionary in coords for c in dictionary['coords']])
		#We need to reflect it, since we're drawing in quadrant IV
		for dictionary in coords:
			dictionary['coords'] = [[c[0], highestY-(c[1]-highestY)] for c in dictionary['coords']]
		
		#Now we're gonna move it up so you can actually see it
		#Find the newest highest y coordinate
		highestY = min([c[1] for dictionary in coords for c in dictionary['coords']])
		for dictionary in coords:
			dictionary['coords'] = [[c[0],c[1]-highestY]for c in dictionary['coords']]
		print 'sending to client'
		return json.dumps({'coords':coords})
	def readReigion(self,regionFile):
		next(regionFile) #Skip the first line
		result = {}
		for line in regionFile:
			l = line.split(',')
			areaName = l[0].lower()
			result[areaName] = [int(item) for item in l[1:] if self.isInt(item)]
		
		return result
	def isInt(self,s):
		try:
			int(s)
			return True
		except ValueError:
			return False
	def validRegion(self,region):
		if len(glob(staticPath+'purple/'+region+".txt"))==1:
			return True
		return False
	def validYear(self,year):
		if year>=1960 and year%4==0:
			return True
		return False
			
			
		
if __name__=='__main__':
	conf = {
		'/':{
			'tools.sessions.on':True,
			'tools.staticdir.root':staticRoot,
		},
		'/purpleAmerica':{
			'request.dispatch':cherrypy.dispatch.MethodDispatcher(),
			'tools.response_headers.on': True,
			'tools.response_headers.headers': [('Content-Type', 'text/plain')],
		},
		'/static':{
			'tools.staticdir.on':True,
			'tools.staticdir.dir':'./static/',
		}
		
	}
	web = PurpleAmericaWeb()
	web.purpleAmerica = PurpleAmerica()
	cherrypy.tree.mount(web,'/',config=conf)
	cherrypy.engine.start()
	cherrypy.engine.block()