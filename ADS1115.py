#!/usr/bin/env python3

import Adafruit_ADS1x15
from time 			import time
from data_upload	import uploadFile
from SaveFile 		import SaveFile


# Choose a gain of 1 for reading voltages from 0 to 4.09V.
# Or pick a different gain to change the range of voltages that are read:
#  - 2/3 = +/-6.144V
#  -   1 = +/-4.096V
#  -   2 = +/-2.048V
#  -   4 = +/-1.024V
#  -   8 = +/-0.512V
#  -  16 = +/-0.256V

# Valore di gain consigliato per i nostri sensori gain = 8


class ADS1115:
	
	__access_token = 'FggmdmsvYNAAAAAAAAAAEN0KNQUUYP_kdSLyRno77Jq9p_KC6T1NBRBKvIPcUzw4'
	__dict_gain = {2/3: .1875, 1: .125, 2: .0625, 4: .03125, 8: .015625, 16: .0078125}		# valori in mV
	__ADS1115_folder = '/home/pi/data/ADS1115/'
	
	def __init__(self):
		
		self.GAIN = 4
		
		try:	self.mult = ADS1115.__dict_gain[self.GAIN]
		
		except NameError:
			
			self.mult = ADS1115.__dict_gain[1]
			print("\n\tGain settato al valore di default {} μV".format(myADS1115.__dict_gain[1]))
		
		self.sensor = Adafruit_ADS1x15.ADS1115()
		self.print_data = True
		self.dropbox_upload = False
		self.saver = SaveFile(ADS1115.__ADS1115_folder)






	def get_data(self):
		''' Ritorna una lista di valori letti dal convertitore '''
		
		data = []
		for i in range(4):
			
			data.append(self.sensor.read_adc(i, self.GAIN) * self.mult)        # i = canale del convertiore letto
		
		return data
		




	def continuous_mode(self, interval = False):
		''' Letture continue per un intervallo interval '''
		
		
		data = []
		st = time()
		
		addr = self.saver.generateName('ADS1115')
		with open(addr, 'w') as FILE:
			
			FILE.write("A0,A1,A2,A3\n")
		
		if self.print_data:
			
			print("\n\t{0: ^10}{1: ^10}{2: ^10}{3: ^10}\t"
				  .format('DATA 1', 'DATA 2', 'DATA 3', 'DATA 4'))		
		
		flag = False
		if not interval:	flag = True
		
		while (time() - st) < interval or flag:
			
			temp = self.get_data()
			
			with open(addr, 'a') as FILE:
				
				FILE.write("{0},{1},{2},{3}\n".format(temp[0], temp[1], temp[2], temp[3]))
			
			if self.print_data:
				print("\t{0}\t{1}\t{2}\t{3}"
					  .format(temp[0], temp[1], temp[2], temp[3]))
			
			data.append(temp)
			

		
		if self.dropbox_upload:	self.uploadDropbox(addr)
				
		return data
		
		
		
		
		
		
		
			
	def uploadDropbox(self, file_path):
                ''' Carica su dropbox il file appena salvato '''
                
                if self.dropbox_upload:
                        
                        fileName = '\ADS1115' + datetime.now().strftime('%d_%m_%Y_%H_%M_%S') + '.csv'
                        uploadFile(ADS1115.__access_token, file_path, fileName)		
			




if __name__ == '__main__':
	
	converter = ADS1115()
	converter.continuous_mode()
		
