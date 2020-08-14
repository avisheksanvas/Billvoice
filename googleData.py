import sheetData
import os
import pdb
import pandas as pd
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow,Flow
from google.auth.transport.requests import Request
import matplotlib.pyplot as plt

billSheetID = sheetData.billSheetID
extraSheetID = sheetData.extraSheetID
sheets = sheetData.sheets
qtyLeftCol = 'F'

def authenticate():
	SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
	global service
	creds = None
	if os.path.exists( 'token.pickle' ):
		with open( 'token.pickle', 'rb' ) as token:
			creds = pickle.load( token )
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh( Request() )
		else:
			flow = InstalledAppFlow.from_client_secrets_file( 'credentials.json', SCOPES )
			creds = flow.run_local_server( port=0 )
		with open( 'token.pickle', 'wb' ) as token:
			pickle.dump( creds, token )

	service = build( 'sheets', 'v4', credentials=creds )

def loadData():
	dfsPerBrand = {}
	# Brand level
	for sheetInfo in sheets:
		# Different orders placed for different brands level
		dfsPerBrand[ sheetInfo[ 'brand' ] ] = []
		for order in range( sheetInfo[ 'orders' ] ):
			sheetRange = 'ORDER%d!A1:G50000' % ( order + 1 )
			sheet = service.spreadsheets()
			result_input = sheet.values().get( spreadsheetId=sheetInfo[ 'id' ], range=sheetRange ).execute()
			values_input = result_input.get( 'values', [])
			if not values_input:
				print( 'No stock data found for %s-%s' % ( sheetInfo[ 'brand' ], sheetRange ) )
			df = pd.DataFrame( values_input[1:], columns=values_input[0] )
			dfsPerBrand[ sheetInfo[ 'brand' ] ].append( df )
	
	return dfsPerBrand
	
def getMaxBillID():
	sheetRange = 'BROAD!A2:D89100'
	sheet = service.spreadsheets()
	result_input = sheet.values().get( spreadsheetId=billSheetID, range=sheetRange ).execute()
	values_input = result_input.get( 'values', [])

	if not values_input:
		print( 'No broad bill data found.' )
	if len( values_input ) > 0:
		return int( values_input[-1][0] )
	else:
		return 0

def writeNotFoundItem( notFoundItem ):
	sheet = service.spreadsheets()
	body = { 'values' : [ notFoundItem ] }
	sheetRange = 'NOTFOUND!A1:B89100'
	sheet.values().append( spreadsheetId=extraSheetID, valueInputOption='RAW', range=sheetRange, body=body ).execute()
	 
def writeBill( bill ):
	sheet = service.spreadsheets()
	detailValues = []
	
	for item in bill[ 'Items' ]:
		# Create detailed row to add in the bill sheet
		detailValueRow = [ str( bill[ 'Id' ] ),
					 	   item[ 'PartNo' ],
					 	   item[ 'Qty' ],
						   item[ 'Brand' ],
						   item[ 'Sheet' ],
					 	   item[ 'Price' ],
					 	   item[ 'Discount' ],
						   item[ 'CostPrice' ] ]
		detailValues.append( detailValueRow )

		# Update the stock in the stock sheet
		qtyLeft = int( item[ 'QtyLeft' ] ) - item[ 'Qty' ]
		sheetRange = item[ 'Sheet' ] + qtyLeftCol + '%d' % item[ 'IdxInSheet' ]
		for sheetInfo in sheets:
			if sheetInfo[ 'brand' ] == item[ 'Brand' ]:
				sheetId = sheetInfo[ 'id' ]
				break
		body = { 'values' : [[ qtyLeft ]] }
		sheet.values().update( spreadsheetId=sheetId, valueInputOption='RAW', range=sheetRange, body=body ).execute()
		
	# Add detailed rows to the bill sheet	
	body = { 'values' : detailValues }
	sheetRange = 'DETAIL!A1:G89100'
	result_output = sheet.values().append( spreadsheetId=billSheetID, valueInputOption='RAW', range=sheetRange, body=body ).execute()

	# Create a per bill row to add to the bill sheet	
	broadValues = []
	broadValueRow = [ str( bill[ 'Id' ] ),
					  bill[ 'Customer' ], 
					  bill[ 'Date' ],
					  bill[ 'Total' ] ]
	broadValues.append( broadValueRow )
	body = { 'values' : broadValues }
	sheetRange = 'BROAD!A1:D89100'
	result_output = sheet.values().append( spreadsheetId=billSheetID, valueInputOption='RAW', range=sheetRange, body=body ).execute()
		
def getFrequentProducts():
	# Get products to plot
	sheetRange = 'DETAIL!B1:C89100'
	sheet = service.spreadsheets()
	result_input = sheet.values().get( spreadsheetId=billSheetID, range=sheetRange ).execute()
	values_input = result_input.get( 'values', [])
	df = pd.DataFrame( values_input[1:], columns=values_input[0] )
	df[ 'Qty' ] = df[ 'Qty' ].astype( int )
	df1 = df.groupby('PartNo')[ 'Qty' ].sum()
	df1 = df1.sort_values( ascending=False )
	partNos = []
	qtys = []
	i = 0
	for partNo, qty in df1.items():
		partNos.append( partNo )
		qtys.append( qty )
		i += 1
		if i == 10:
			break
	
	# Plot a bar graph
	fig = plt.figure()
	ax = fig.add_axes([0.2,0.2,0.7,0.7])
	ax.bar(partNos,qtys)
	plt.xlabel("Part Number")
	plt.ylabel("Quantity")
	plt.show()
	pdb.set_trace()
		
authenticate()
