import tkinter as tk
from tkinter import messagebox
import pdb
import googleData

items = []

def search():
	partNo = searchText.get( "1.0", "end" ).replace( '\n', '' )
	options = googleData.search( partNo )
	if( len( options ) == 1 ):
		option = options[ 0 ]
		item = {	'PartNo' : partNo,
					'Desc' : option[ 'PartDesc' ],
					'Brand' : option[ 'Brand' ],
					'Sheet' : option[ 'Sheet' ],
					'IdxInSheet' : option[ 'Idx' ] + 2, 
					'Price' : option[ 'Price' ],
					'QtyLeft' : option[ 'QtyLeft' ] }
		item[ 'Idx' ] = len( items )
		item[ 'LabelEl' ] = tk.Label( listFrame, text=item[ 'Desc' ] )
		item[ 'LabelEl' ].grid( row=item[ 'Idx' ] )
		item[ 'Qty' ] = tk.Spinbox( listFrame, from_=0, to=100 )
		item[ 'Qty' ].grid( row=item[ 'Idx' ], column=1 )
		item[ 'Qty' ].invoke( "buttonup" )
		item[ 'Discount' ] = tk.Spinbox( listFrame, from_=0, to=100 )
		item[ 'Discount' ].grid( row=item[ 'Idx' ], column=2 )
		items.append( item )
	elif ( len( options ) > 1 ):
		#TODO give option to choose items.
		pass
	else:
		display = 'Part Not Found'
		result = 'Failure'
		messagebox.showinfo( result, display )

def bill():
	
	# Write online to google sheets
	customer = customerText.get( "1.0", "end" ).replace( '\n', '' )
	googleData.writeBill( items, customer )

	# Open a sheet with bill that can be printed ( See what TODO )
	# ????


	# Clear local state
	clear()	

def clear():
	global listFrame
	listFrame.destroy()
	listFrame = tk.Frame( root, bg="#C0C0C0" )
	listFrame.place( rely=searchAreaHeight, relheight=listAreaHeight, relwidth=1 )
	items.clear()

# Start of all the widgets
root = tk.Tk()
# Setup
searchAreaHeight = 0.05
listAreaHeight = 0.9
billAreaHeight = 0.05
# Canvas
canvas = tk.Canvas( root, height=700, width=500, bg='#FFFFFF' )
canvas.pack() 
# Search Frame
searchFrame = tk.Frame( root, bg="#008000" )
searchFrame.place( relheight=searchAreaHeight, relwidth=1 )
searchTextWidth = 0.4
customerTextWidth = 0.4
searchButtonWidth = 1 - searchTextWidth - customerTextWidth 
searchText = tk.Text( searchFrame )
searchText.place( relheight=1, relwidth=searchTextWidth )
customerText = tk.Text( searchFrame )
customerText.place( relx=searchTextWidth, relheight=1, relwidth=customerTextWidth )
searchButton = tk.Button( searchFrame, text="Search", command=search )
searchButton.place( relx=1-searchButtonWidth, relheight=1, relwidth=searchButtonWidth )
# List Frame - TODO: Add a scrollbar when the items exceed
listFrame = tk.Frame( root, bg="#C0C0C0" )
listFrame.place( rely=searchAreaHeight, relheight=listAreaHeight, relwidth=1 )
# Bill Frame
billFrame = tk.Frame( root, bg="#B0B0B0" )
billFrame.place( rely=searchAreaHeight+listAreaHeight, relheight=billAreaHeight, relwidth=1 )
billButton = tk.Button( billFrame, text="Bill", command=bill )
billButton.place( relheight=1, relwidth=0.5 )
clearButton = tk.Button( billFrame, text="Clear", command=clear, fg='red' )
clearButton.place( relx=0.5, relheight=1, relwidth=0.5 )
# End of all the widgets

# TODO: Button names not visible
root.mainloop()
