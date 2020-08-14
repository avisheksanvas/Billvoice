import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog 
import pdb
import googleData
import datetime
from scrollableFrame import ScrollableFrame

items = []
dfsPerBrand = googleData.loadData()

def _search():
	itemNo = searchText.get( "1.0", "end" ).replace( '\n', '' )
	options = []
	for brand, dfs in dfsPerBrand.items():
		for orderNo, df in enumerate( dfs ):
			idxs = df.loc[ df['ItemNo'] == itemNo ].index.values.astype( int )
			if( len( idxs ) > 0 ):
				for idx in idxs:
					idx = df.loc[ df['ItemNo'] == itemNo ].index.values.astype( int )[ 0 ]
					qtyLeft = df.loc[ idx, 'QtyLeft' ]
					if qtyLeft != '0':
						option = {} 
						option[ 'Brand' ] = brand
						option[ 'Sheet' ] = 'ORDER%d!' % ( orderNo + 1 )
						option[ 'IdxInSheet' ] = idx + 2
						option[ 'ItemNo' ] = itemNo
						option[ 'ItemDesc' ] = df.loc[ idx, 'ItemDesc' ]
						option[ 'Price' ] = df.loc[ idx, 'Price' ]
						option[ 'QtyLeft' ] = df.loc[ idx, 'QtyLeft' ]
						option[ 'CostPrice' ] = df.loc[ idx, 'CostPrice' ]
						option[ 'Text' ] = '%s---%s---Brand:%s---Order:%s---Price:%s---Cost:%s' \
							 				% ( option[ 'ItemNo' ], option[ 'ItemDesc' ], option[ 'Brand' ],
								 			option[ 'Sheet' ], option[ 'Price' ], option[ 'CostPrice' ] )
						options.append( option )
	return options

def search():
	options = _search()
	
	if( len( options ) == 0 ):
		notFoundItem = []
		notFoundItem.append( searchText.get( "1.0", "end" ).replace( '\n', '' ) )
		notFoundItem.append( getDate() )
		googleData.writeNotFoundItem( notFoundItem )
		display = 'Item Not In Stock'
		result = 'Failure'
		messagebox.showinfo( result, display )
		return

	if( len( options ) > 1 ):
		optionsText = ""
		for i, option in enumerate( options ):
			optionsText += "%d) %s\n" % ( i, option[ 'Text' ] )
		choice = simpledialog.askinteger( "Options", optionsText )
		item = options[ choice ]
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
	# Item Discount selection box
	item[ 'DiscountBox' ] = tk.Spinbox( listFrame, from_=0, to=100 )
	item[ 'DiscountBox' ].grid( row=item[ 'Idx' ], column=2 )
	items.append( item )

def getTotal( finalItems ):
	total = 0.0
	for item in finalItems:
		price = float( item[ 'Price' ] )
		discount = price * ( int( item[ 'Discount' ] ) / 100 )
		total += ( price - discount ) * item[ 'Qty' ]

	return total

def getDate():
	currentDate = datetime.datetime.now()
	return currentDate.strftime("%x")
	 
def bill():
	finalItems = []
	billText = ""
	for item in items:
		item[ 'Qty' ]  = min( int( item[ 'QtyBox' ].get() ), int( item[ 'QtyLeft' ] ) )
		item[ 'Discount' ] = item[ 'DiscountBox' ].get()
		if item[ 'Qty' ] > 0:
			item[ 'Text' ] = item[ 'Text' ] + '---Qty:%s---Dis:%s' % ( str( item[ 'Qty' ] ), item[ 'Discount' ] )
			finalItems.append( item )
			billText = billText + item[ 'Text' ] + "\n"
	
	if len( finalItems ) > 0:
		confirm = messagebox.askokcancel( "Confirm Bill", billText )
		if confirm:
			bill = { 
					'Id' : googleData.getMaxBillID() + 1,
					'Customer' : customerText.get( "1.0", "end" ).replace( '\n', '' ),
					'Date' : getDate(),
					'Items' : finalItems,
					'Total' : getTotal( finalItems ),
				   }
			googleData.writeBill( bill )

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
customerTextWidth = 0.4
searchButtonWidth = 1 - searchTextWidth - customerTextWidth 
searchText = tk.Text( searchFrame )
searchText.place( relheight=1, relwidth=searchTextWidth )
searchText.insert( tk.END, "ItemNo...")
customerText = tk.Text( searchFrame, bg="#b3ffff")
customerText.place( relx=searchTextWidth, relheight=1, relwidth=customerTextWidth )
customerText.insert( tk.END, "Customer...")
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
