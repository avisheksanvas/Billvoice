import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog 
import math
import pdb
import googleData
import datetime
from scrollableFrame import ScrollableFrame

items = []
dfsPerBrand = googleData.loadData()

def getNepaliPrice( nepaliPrice ):
	try:
		float( nepaliPrice )
		return math.ceil( float( nepaliPrice ) )
	except ValueError:
		return 0

def _search():
	itemNo = searchText.get( "1.0", "end" ).replace( '\n', '' )
	itemNo = itemNo.upper()
	brandToSearch = brandText.get( "1.0", "end" ).replace( '\n', '' )
	brandToSearch = brandToSearch.upper()
	if brandToSearch not in dfsPerBrand.keys():
		brandToSearch = 'ALL'
	options = []
	for brand, dfInfos in dfsPerBrand.items():
		if not( brandToSearch == 'ALL' or brand == brandToSearch ):
			continue
		for dfInfo in dfInfos:
			orderNo = dfInfo[ 'ORDER' ]
			df = dfInfo[ 'DATA' ] 
			idxs = df.loc[ df['ItemNo'] == itemNo ].index.values.astype( int )
			# If nothing found by ItemNo, try to take it as a name
			if len( idxs ) <= 0:
				idxs = df.loc[ df['ItemDesc'].str.contains( itemNo ) ].index.values.astype( int )
			if( len( idxs ) > 0 ):
				for idx in idxs:
					qtyLeft = df.loc[ idx, 'QtyLeft' ]
					if qtyLeft != '0':
						option = {} 
						option[ 'Brand' ] = brand
						option[ 'Sheet' ] = 'ORDER%d!' % ( orderNo )
						option[ 'IdxInSheet' ] = idx + 2
						option[ 'ItemNo' ] = df.loc[ idx, 'ItemNo' ]
						option[ 'ItemDesc' ] = df.loc[ idx, 'ItemDesc' ]
						option[ 'Price' ] = df.loc[ idx, 'Price' ]
						option[ 'QtyLeft' ] = df.loc[ idx, 'QtyLeft' ]
						option[ 'CostPrice' ] = df.loc[ idx, 'CostPrice' ]
						option[ 'NepaliPrice' ] = df.loc[ idx, 'NepaliPrice' ]
						option[ 'LeastPrice' ] = df.loc[ idx, 'LeastPrice' ]
						setPrice = math.ceil( float( option[ 'Price' ] ) )
						nepaliPrice = getNepaliPrice( option[ 'NepaliPrice' ] )
						# Min price to sell is Indian MRP * 2. No need to multiply as stored in sheet
						# after multiplying by 2.
						minPriceToSell = math.ceil( float( option[ 'LeastPrice' ] ) )
						option[ 'Text' ] = '%s---%s---Brand:%s---Order:%s---Price:%d---NepaliPrice:%d---LeastPrice:%d' \
							 				% ( option[ 'ItemNo' ], option[ 'ItemDesc' ], option[ 'Brand' ],
								 			option[ 'Sheet' ], setPrice, nepaliPrice, minPriceToSell )
						option[ 'ReadableText' ] = '%s---%s' % ( option[ 'ItemNo' ], option[ 'ItemDesc' ] )
						options.append( option )
	return options

def search():
	options = _search()
	
	if( len( options ) == 0 ):
		notFoundDesc = ''
		while not notFoundDesc:
			# Entering empty string
			notFoundDesc = simpledialog.askstring( "Item not in stock", "Please enter brand name or description:",
											   	   initialvalue="Customer Request" )
			# Pressed cancel
			if notFoundDesc is None:
				return
		notFoundItem = []
		notFoundItem.append( searchText.get( "1.0", "end" ).replace( '\n', '' ).upper() )
		notFoundItem.append( getDate() )
		notFoundItem.append( notFoundDesc )
		googleData.writeNotFoundItem( notFoundItem )
		return

	if( len( options ) > 1 ):
		optionsText = ""
		for i, option in enumerate( options ):
			optionsText += "%d) %s\n" % ( i+1, option[ 'Text' ] )
		choice = 0
		while ( choice is not None ) and ( choice <= 0 or choice > len( options ) ):
			# Pressed wrong choice
			choice = simpledialog.askinteger( "Options", optionsText )
		
		if choice is None:
			return
		item = options[ choice-1 ]
	else:
		item = options[ 0 ]
	
	# Item Index in the Current Bill
	item[ 'Idx' ] = len( items )
	# Label to display
	item[ 'LabelEl' ] = tk.Label( listFrame, text=item[ 'Text' ] )
	item[ 'LabelEl' ].grid( row=item[ 'Idx' ] )
	# Item Quantity selection box
	item[ 'QtyBox' ] = tk.Spinbox( listFrame, from_=0, to=100 )
	item[ 'QtyBox' ].grid( row=item[ 'Idx' ], column=1 )
	item[ 'QtyBox' ].invoke( "buttonup" )
	# Item Price Box
	item[ 'SellingPriceBox' ] = tk.Entry( listFrame, width=20 )
	item[ 'SellingPriceBox' ].grid( row=item[ 'Idx' ], column=3 )
	items.append( item )

def getTotal( finalItems ):
	total = 0.0
	for item in finalItems:
		total += float( item[ 'SellingPrice' ] ) * item[ 'Qty' ]

	return total

def getDate():
	currentDate = datetime.datetime.now()
	return currentDate.strftime("%x")
	
def isItemsPriceCorrect( finalItems ):
	# Check if prices entered are appropriate
	for item in finalItems:
		try:
			float( item[ 'SellingPrice' ] )
		except ValueError:
			return False
	return True
	 
def bill():
	finalItems = []
	billText = ""
	for item in items:
		item[ 'Qty' ]  = min( int( item[ 'QtyBox' ].get() ), float( item[ 'QtyLeft' ] ) )
		item[ 'SellingPrice' ] = item[ 'SellingPriceBox' ].get()
		if item[ 'Qty' ] > 0:
			finalItems.append( item )
			billText = billText + ( item[ 'ReadableText' ] + '---Qty:%s---SellingPrice:%s' % ( str( item[ 'Qty' ] ), item[ 'SellingPrice' ] ) ) + "\n"

	if len( finalItems ) > 0:
		if not isItemsPriceCorrect( finalItems ):
			messagebox.showinfo( "Wrong Prices", "Please enter correct prices for items" )
			return
		confirm = messagebox.askokcancel( "Confirm Bill", billText )
		if confirm:
			customer = simpledialog.askstring( "Customer", "Enter customer name:" )
			if customer is None:
				return
			bill = { 
					'Id' : googleData.getMaxBillID() + 1,
					'Customer' : customer, 
					'Date' : getDate(),
					'Items' : finalItems,
					'Total' : getTotal( finalItems ),
				   }
			googleData.writeBill( bill )
			messagebox.showinfo( "Success", "Stock and billing successfully done" )	

			# Open a sheet with bill that can be printed ( See what TODO )
		else:
			# Don't do anything, might want to edit the order
			return
	else:
		messagebox.showinfo( "Not Available", "Please select some availabe items" )	

	# Load the data from the sheets again for safety
	global dfsPerBrand
	dfsPerBrand = googleData.loadData()
	# Clear local state
	clear()

def clear():
	global listFrameTop, listFrame
	listFrameTop.destroy()
	listFrameTop = ScrollableFrame( root )
	listFrameTop.place( rely=searchAreaHeight, relheight=listAreaHeight, relwidth=1 )
	listFrame = listFrameTop.scrollable_frame
	items.clear()

# Start of all the widgets
root = tk.Tk()
# Setup
searchAreaHeight = 0.05
listAreaHeight = 0.9
billAreaHeight = 0.05
# Canvas
canvas = tk.Canvas( root, height=700, width=1200, bg='#FFFFFF' )
canvas.pack() 
# Search Frame
searchFrame = tk.Frame( root, bg="#008000" )
searchFrame.place( relheight=searchAreaHeight, relwidth=1 )
searchTextWidth = 0.4
brandTextWidth = 0.4
searchButtonWidth = 1 - searchTextWidth - brandTextWidth 
searchText = tk.Text( searchFrame )
searchText.place( relheight=1, relwidth=searchTextWidth )
searchText.insert( tk.END, "ItemNo...")
brandText = tk.Text( searchFrame, bg="#b3ffff")
brandText.place( relx=searchTextWidth, relheight=1, relwidth=brandTextWidth )
brandText.insert( tk.END, "Brand...")
searchButton = ttk.Button( searchFrame, text="Search", command=search )
searchButton.place( relx=1-searchButtonWidth, relheight=1, relwidth=searchButtonWidth )
# List Frame
listFrameTop = ScrollableFrame( root )
listFrameTop.place( rely=searchAreaHeight, relheight=listAreaHeight, relwidth=1 )
listFrame = listFrameTop.scrollable_frame
# Bill Frame
billFrame = tk.Frame( root, bg="#B0B0B0" )
billFrame.place( rely=searchAreaHeight+listAreaHeight, relheight=billAreaHeight, relwidth=1 )
billButton = ttk.Button( billFrame, text="Bill", command=bill )
billButton.place( relheight=1, relwidth=0.5 )
clearButton = ttk.Button( billFrame, text="Clear", command=clear )
clearButton.place( relx=0.5, relheight=1, relwidth=0.5 )
# End of all the widgets

root.mainloop()
