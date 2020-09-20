# Add a script to make orders.
# Also use extra info sheet to check which items need to be ordered.

# Checks all distinct part numbers in the current year per brand and forms
# an order template with total quantity ordered and total quantity sold.
# This can also be used to move to form the order 0 ( old stock ) for the next year

import googleData
import pdb
import xlsxwriter
import datetime

dfsPerBrand = googleData.loadData()
toOrder = {}
stock = {}
for brand, dfInfos in dfsPerBrand.items():
	stock[ brand ] = {}
	for dfInfo in dfInfos:
		for _, row in dfInfo[ 'DATA' ].iterrows():	
			try:
				float( row[ 'QtyLeft' ] )
				qtyLeft = float( row[ 'QtyLeft' ] )
			except ValueError:
				qtyLeft = 0
			if row[ 'ItemNo' ] not in stock[ brand ]:
				stock[ brand ][ row[ 'ItemNo' ] ] = qtyLeft
			else:
				stock[ brand ][ row[ 'ItemNo' ] ] += qtyLeft


for brand in stock.keys():
	toOrder[ brand ] = {}
	for itemNo in stock[ brand ].keys():
		if stock[ brand ][ itemNo ] <= 1:
			toOrder[ brand ][ itemNo ] = stock[ brand ][ itemNo ]

currentDate = datetime.datetime.now()
workbook = xlsxwriter.Workbook( 'Order.xlsx' )
for brand in toOrder.keys():
	worksheet = workbook.add_worksheet( brand )
	worksheet.write('A1', 'ItemNo')
	worksheet.write('B1', 'QtyLeft')
	rowNo = 2
	for itemNo in toOrder[ brand ].keys():
		worksheet.write('A%d' % rowNo, itemNo )
		worksheet.write('B%d' % rowNo, toOrder[ brand ][ itemNo ] )
		rowNo += 1

workbook.close()
