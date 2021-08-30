#!/usr/bin/env python

import dropbox
import os


def uploadFile(access_token, file_path, dest_path):
	''' Carica il file su dropbox '''
	
	dbx = dropbox.Dropbox(access_token)
	
	try:
		with open(file_path, 'rb') as FILE:

			dbx.files_upload(FILE.read(), dest_path)
		
		print('\n\t{} caricato su Dropbox!!'.format(file_path))
	
	except FileNotFoundError:
		
		print('\n\t{} non trovato!!'.format(file_path))



		
if __name__ == '__main__':
	
	access_token = 'FggmdmsvYNAAAAAAAAAAEN0KNQUUYP_kdSLyRno77Jq9p_KC6T1NBRBKvIPcUzw4'
	file_path = 'dropbox_test.txt'
	dest_path = '/dropbox_test2.txt'    #/ prima del nome
	uploadFile(file_path, dest_path)
