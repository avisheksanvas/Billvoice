import googleData
import pdb
import xlsxwriter
import datetime
import operator

dfsPerBrand = googleData.loadData( allOrders=True )
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
				stock[ brand ][ row[ 'ItemNo' ] ] = [ row[ 'ItemDesc' ], qtyLeft ]
			else:
				stock[ brand ][ row[ 'ItemNo' ] ][1] += qtyLeft

# sort stock
sortedStock = {}
for brand in stock.keys():
	sortedStock[ brand ] = sorted( stock[ brand ].items(), key=operator.itemgetter(0) )

googleData.writeStock( sortedStock )
