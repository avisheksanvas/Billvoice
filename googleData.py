import sheetData
import datetime
import os
import pdb
import pandas as pd
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow,Flow
from google.auth.transport.requests import Request
from tkinter import messagebox

billSheetID = sheetData.billSheetID
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

def search( partNo ):
	options = []
	# Brand level
	for sheetInfo in sheets:
		# Different orders placed for different brands level
		for order in range( sheetInfo[ 'orders' ] ):
			# Search for PartNo for a particular order of a particular brand and add to options
			sheetRange = 'ORDER%d!A1:G50000' % ( order + 1 )
			sheet = service.spreadsheets()
			result_input = sheet.values().get( spreadsheetId=sheetInfo[ 'id' ], range=sheetRange ).execute()
			values_input = result_input.get( 'values', [])
			if not values_input:
				print( 'No data found.' )
			df = pd.DataFrame( values_input[1:], columns=values_input[0] )
			idxs = df.loc[ df['PartNo'] == partNo ].index.values.astype( int )
			if( len( idxs ) > 0 ):
				for idx in idxs:
					idx = df.loc[ df['PartNo'] == partNo ].index.values.astype( int )[ 0 ]
					qtyLeft = df.loc[ idx, 'QtyLeft' ]
					if qtyLeft != '0':
						option = {} 
						option[ 'Brand' ] = sheetInfo[ 'brand' ]
						option[ 'Sheet' ] = 'ORDER%d!' % ( order + 1 )
						option[ 'Idx' ] = idx
						option[ 'PartDesc' ] = df.loc[ idx, 'PartDesc' ]
						option[ 'Price' ] = df.loc[ idx, 'Price' ]
						option[ 'QtyLeft' ] = df.loc[ idx, 'QtyLeft' ]
						option[ 'CostPrice' ] = df.loc[ idx, 'CostPrice' ]
						options.append( option )
	return options
	
def getMaxBillID():
	sheetRange = 'BROAD!A2:D89100'
	sheet = service.spreadsheets()
	result_input = sheet.values().get( spreadsheetId=billSheetID, range=sheetRange ).execute()
	values_input = result_input.get( 'values', [])

	if not values_input:
		print( 'No data found.' )
	if len( values_input ) > 0:
		return int( values_input[-1][0] )
	else:
		return 0

def createBillText( items ):
	bill = ""
	for item in items:
		billRow = "Part: " + item[ 'PartNo' ] + "---Qty: " + str( item[ 'FinalQty' ] ) + "---Discount: " + item[ 'Discount' ].get()
		bill += "\n" + billRow
	return bill
		
def writeBill( bill, customer ):
	sheet = service.spreadsheets()
	billID = getMaxBillID() + 1
	billDate = datetime.datetime.now()
	billDate = billDate.strftime("%x")
	total = 0
	detailValues = []
	finalBill = []
	for item in bill:
		item[ 'FinalQty' ] = min( int( item[ 'Qty' ].get() ), int( item[ 'QtyLeft' ] ) )
		if item[ 'FinalQty' ] <= 0:
			continue
		finalBill.append( item )
		
	# If no items in bill, return
	if len( finalBill ) < 1:
		messagebox.showinfo( "Not Available", "Please select some availabe items" )
		return
	
	billText = createBillText( finalBill )
	confirm = messagebox.askokcancel( "Confirm Bill", billText )
	if not confirm:
		return
	
	for item in finalBill:
		# Create detailed row to add in the bill sheet
		detailValueRow = [ str( billID ),
					 	   item[ 'PartNo' ],
					 	   item[ 'FinalQty' ],
						   item[ 'Brand' ],
						   item[ 'Sheet' ],
					 	   item[ 'Price' ],
					 	   item[ 'Discount' ].get(),
						   item[ 'CostPrice' ] ]
		detailValues.append( detailValueRow )

		# Update the stock in the stock sheet
		qtyLeft = int( item[ 'QtyLeft' ] ) - item[ 'FinalQty' ]
		sheetRange = item[ 'Sheet' ] + qtyLeftCol + '%d' % item[ 'IdxInSheet' ]
		for sheetInfo in sheets:
			if sheetInfo[ 'brand' ] == item[ 'Brand' ]:
				sheetId = sheetInfo[ 'id' ]
				break
		body = { 'values' : [[ qtyLeft ]] }
		sheet.values().update( spreadsheetId=sheetId, valueInputOption='RAW', range=sheetRange, body=body ).execute()
		
		# Add the item price to the total bill
		price = float( item[ 'Price' ] )
		discount = price * ( int( item[ 'Discount' ].get() ) / 100 )
		total += ( price - discount ) * item[ 'FinalQty' ]

	# Add detailed rows to the bill sheet	
	body = { 'values' : detailValues }
	sheetRange = 'DETAIL!A1:G89100'
	result_output = sheet.values().append( spreadsheetId=billSheetID, valueInputOption='RAW', range=sheetRange, body=body ).execute()

	# Create a per bill row to add to the bill sheet	
	broadValues = []
	broadValueRow = [ str( billID ),
					  customer, 
					  billDate,
					  total ]
	broadValues.append( broadValueRow )
	body = { 'values' : broadValues }
	sheetRange = 'BROAD!A1:D89100'
	result_output = sheet.values().append( spreadsheetId=billSheetID, valueInputOption='RAW', range=sheetRange, body=body ).execute()
		
authenticate()
