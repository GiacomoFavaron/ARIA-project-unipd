#!/usr/bin/env python3

from datetime 		import datetime
from time 			import time
from SaveFile 		import SaveFile
from data_upload 	import uploadFile
import matplotlib.pyplot 	as plt
import serial 				as ser 
import argparse
import RPi.GPIO 			as io






class SDS011:
	
	__access_token = 'FggmdmsvYNAAAAAAAAAAEN0KNQUUYP_kdSLyRno77Jq9p_KC6T1NBRBKvIPcUzw4'
	__SDS011_folder = '/home/pi/data/SDS011/'
	
	
	def __init__(self, serial_port = '/dev/ttyUSB0'):
		
		self.sensor = ser.Serial(serial_port, 9600, timeout = 1.5)        # baudrate 9600
		self.print_data = True
		self.live_plot = False
		self.dropbox_upload = False
		
		self.saver = SaveFile(SDS011.__SDS011_folder)
	
	
	
	
	
	def get_data(self):
		''' Legge il sensore e ritorna nell'ordine:
			pm 2.5, pm 10, data e ora '''
		
		if not self.sensor.isOpen():
			
			self.sensor.open()
		
		data = self.sensor.read(10)                            # legge 10 byte dal sensore
		
		
		if data[0] == ord('\xaa') and data[1] == ord('\xc0') and data[9] == ord('\xab'):
			
			pm25 = (data[3] * 256 + data[2]) / 10              # dal datasheet del SDS011
			pm10 = (data[5] * 256 + data[4]) / 10
                        
			if data[8] == (sum(data[2:8]) % 256):              # verifica checksum

				strtime = datetime.now().strftime('%d-%m-%Y--%H:%M:%S')

				return pm25, pm10, strtime
	
	
	
	
	
	def PlotAndSave(self, delta = False):
		''' Scrive i dati su file, plotta le concentrazioni e le stampa
			a video.
			delta:		tempo di rilevazione
			intervallo:		frequenza lettura sensore '''
			
		pm25, pm10, labels = [], [], []
		
		addr = self.saver.generateName('SDS011')
		with open(addr, 'w') as FILE:
			
			FILE.write('pm2.5,pm10,data\n')
			
		if self.print_data:
			print('\npm2.5\tpm10\tDATA')
		
		
		flag = False
		if not delta:	flag = True
		stime = time()
			
		while (time() - stime) < delta or flag:
			
			tempo_residuo = delta - (time() - stime)
			
			data = self.readSensor()
			if data:
				
				with open(addr, 'a') as FILE:
					FILE.write('{0},{1},{2}\n'.format(data[0], data[1], data[2]))
				
				if self.print_data:
					print('\n{0}\t{1}\t{2}'.format(data[0], data[1], data[2]))

				pm25.append(data[0])
				pm10.append(data[1])
				labels.append(data[2])
				
				self.plotParticulates(pm25, pm10, labels, tempo_residuo)
						
			

		self.uploadDropbox(addr)





	def plotParticulates(self, pm25, pm10, labels, tempo_residuo = '...'):
		''' Plotta in real time le concentrazioni '''
		
		pm25avg = average(pm25)
		pm10avg = average(pm10)
		letture = len(pm25)
		
		width = 70
		if len(pm25) > width:
			
			pm25 = pm25[-width::]
			pm10 = pm10[-width::]
			labels = labels[-width::]

		
		with plt.style.context('ggplot'):
			
			plt.cla()                                   # pulisce assi e figura
			plt.clf()
			
			ax = plt.gca()
			fig = plt.gcf()
			fig.set_facecolor((.95, .95, .95))
			ax.set(title = 'Concentrazioni pm 10 e pm 2.5 ({})'
				   .format(datetime.now().strftime('%H:%M:%S')), ylabel = 'μg / m³')
			
			ax.plot(pm25, 'g', linewidth = 1.1, label = 'pm 2.5')
			ax.plot(pm10, 'b', linewidth = 1.1, label = 'pm 10')
			ax.legend()
			
			fig.text(.05, .95, 'Numero letture: {0:4d}\nMedia PM 2.5: {1:3.2f}\n'
					 'Media PM 10: {2:3.2f}\nTempo residuo: {3:3.2f}'.format(letture,
					 pm25avg, pm10avg, tempo_residuo), fontsize = 8)
			
			plt.xticks(list(range(len(labels))), labels, rotation = 60)
			
		plt.pause(.01)

	
	
	
	
	
	def saveData(self, delta = False):
		''' Scrive i dati su file, plotta le concentrazioni e le stampa
			a video.
			delta:		tempo di rilevazione
			intervallo:		frequenza lettura sensore '''
		
		addr = self.saver.generateName('SDS011')
		with open(addr, 'w') as FILE:
			
			FILE.write('pm2.5,pm10,data\n')
			
		stime = time()
		
		flag = False
		if not delta:	flag = True
		stime = time()
		
		while (time() - stime) < delta or flag:
			
			data = self.readSensor()
			
			if data:
				
				with open(addr, 'a') as FILE:
					FILE.write('{0},{1},{2}\n'.format(data[0], data[1], data[2]))

	
		self.uploadDropbox(addr)
				
		
		
		
		
		
	def printRaw(self, intervallo = 1):
		
		add = self.saver,generateName('SDS011')
		with open(addr, 'w') as FILE:
			
			FILE.write('pm2.5,pm10,data\n')
		
		while True:
			data = self.readSensor()
			if data:

				print('\n{0}\t{1}\t{2}'.format(data[0], data[1], data[2]))
				with open(addr, 'a') as FILE:
					FILE.write('{0},{1},{2}\n'.format(data[0], data[1], data[2]))

				
	
	
	
	def uploadDropbox(self, file_path):
		''' Carica su dropbox il file appena salvato '''
		
		if self.dropbox_upload:
			
			fileName = '/SDS011_' + datetime.now().strftime('%d_%m_%Y_%H_%M_%S') + '.csv'
			uploadFile(SDS011.__access_token, file_path, fileName)		
	
	
	
	
def average(arr):
	return sum(arr) / len(arr)
	
	
	
	
if __name__ == '__main__':
	
	
	sensor = SDS011()
	sensor.saveData()
