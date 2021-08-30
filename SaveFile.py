#!/usr/bin/env python3

import os


class SaveFile:
	
	
	def __init__(self, folder):
		
		self.folder = folder
	
	
	
	
	def searchFile(self, file_addr):
		''' Ritorna true se trova il file '''
		
		if file_addr in os.listdir(self.folder):		return True
		
		return False
	
	
	
	
	def getCounter(self):
		''' Trova il valore del counter e lo aggiorna '''
		
		if self.searchFile('counter.txt'):
			
			with open((self.folder + 'counter.txt'), 'r') as COUNTER_FILE:
				
				
				try:		val =  int(COUNTER_FILE.readline())
				except:		val = -1
				
			with open((self.folder + 'counter.txt'), 'w') as COUNTER_FILE:
				
				COUNTER_FILE.write(str(val + 1))
				
			return val + 1
		
		else:
			
			with open((self.folder + 'counter.txt'), 'w') as COUNTER_FILE:
				
				COUNTER_FILE.write(str(0))
				
			return 0
		
	
	
	def generateName(self, string):
		''' Genera il nome per il salvataggio '''
		
		return self.folder + string + '_' + str(self.getCounter()) + '.csv'
		







if __name__ == '__main__':
	
	fold = 'tuo indirizzo'
	sf = SaveFile(fold)
	
	for i in range(10):
		
		print(sf.generateName('misure'))
