# run with
#  ~/Workspaces/BGG statistics$ pipenv run python main.py
#
# install new modules with
#  ~/Workspaces/BGG statistics$ pipenv install matplotlib

import requests
import xml.etree.ElementTree as ET
import datetime
import os.path
import matplotlib.pyplot as plt

def getXMLPage( pageNumber ):
	url = 'https://boardgamegeek.com/xmlapi2/plays?username=prisonmonkeys&page='
	url = url + str(pageNumber)
	response = requests.get( url )
	return response.text

def writeToFile( strContent, fileName ):
	localFile = open(fileName, "w")
	localFile.write( strContent )
	localFile.close()

def createFileName( index ):
	return 'Plays_{}.xml'.format( index )

def getAndWriteXML( index ):
	fileContent = getXMLPage( index )
	if fileContent.count( '<play id' ) > 0:
		fileName = createFileName( index )
		writeToFile( fileContent, fileName )
		print( fileName + " was written" )
		return True
	else:
		return False

def updateXMLFilesFromWeb():
	for i in range(1,100):
		success = getAndWriteXML(i)
		if not success:
			return

def doesXMLExist( index ):
	fileName = createFileName( index )
	return os.path.exists( fileName ) and os.path.isfile( fileName )

def readXMLFiles():
	for i in range(1,100):
		success = doesXMLExist(i)
		if not success:
			return i
	return 99

def dateFromStr( date ):
	y,m,d = [int(x) for x in date.split('-')]
	return datetime.datetime(y, m, d)

def getDateListSince( start ):
	end = datetime.datetime.today()
	delta = end - start
	dateList = []
	for x in range( delta.days ):
		dateList.append( start + datetime.timedelta( days = x ) )
	return dateList

class Play:
	def __init__(self, date, name):
		self.date = date
		self.name = name

def addXMLToPlays( index, plays ):
	fileName = 'Plays_{}.xml'.format( index )
	tree = ET.parse( fileName )
	root = tree.getroot()

	for child in root:
		for i in range( int(child.attrib['quantity']) ):
			name = child[0].attrib['name']
			date = child.attrib['date']
			plays.append( Play( date, name ) )

def countPerGameFromPlays( plays ):
	countPerGame = dict()
	for play in plays:
		countPerGame.update( { play.name: countPerGame.get(play.name, 0) + 1 } )
	return countPerGame

def readPlays():
	numberOfXmlFiles = readXMLFiles()
	plays = list()
	for i in range( 1, numberOfXmlFiles ):
		addXMLToPlays( i, plays )
	print( 'found {} plays.'.format( len(plays) ) )
	return plays

def getFirstPlayDate( plays ):
	firstDate = datetime.datetime.today();
	for play in plays:
		if dateFromStr( play.date ) < firstDate:
			firstDate = dateFromStr( play.date )
	return firstDate

def countPerGameFromPlaysSince( plays, date ):
	countPerGame = dict()
	for play in plays:
		if ( dateFromStr( play.date ) <= date ):
			countPerGame.update( { play.name: countPerGame.get(play.name, 0) + 1 } )
	return countPerGame

def printCounts( countPerGame, amount ):
	countPerGameList = list( countPerGame.items() )
	countPerGameList.sort( key = lambda x : (x[0]) )
	countPerGameList.sort( key = lambda x : (x[1]), reverse = True )
	printAmount = amount
	if printAmount == 0:
		printAmount = len(countPerGameList)
	else:
		printAmount = min(printAmount, len(countPerGameList))
	for index in range( printAmount ):
		entry = countPerGameList[index]
		print('{}\t{}\t'.format( index + 1, entry[1] ) + entry[0] )

def calcTotalPlays( countPerGame ):
	totalPlays = 0
	for game in countPerGame:
		totalPlays += countPerGame[game]
	return totalPlays

def calcHIndex( countPerGame ):
	counts = list(countPerGame.values())
	counts.sort( reverse=True )
	h = 0
	for count in counts:
		if count <= h:
			return h
		h += 1
	return h

def calcCountMoreThan( countPerGame, threshold ):
	totalCount = 0
	for count in countPerGame.values():
		if count >= threshold:
			totalCount += 1
	return totalCount

def makePlot( xValues, yValues, title = '' ):
	# x axis values 
	x = xValues
	# corresponding y axis values 
	y = yValues
	  
	# plotting the points  
	plt.plot(x, y) 
	  
	# naming the x axis 
	plt.xlabel('x - axis') 
	# naming the y axis 
	plt.ylabel('y - axis') 
	  
	# giving a title to my graph 
	plt.title( title ) 
	  
	# function to show the plot 
	plt.show()

def plotCountsAndGamesAndH():
	plays = readPlays()
	datesForPlot = getDateListSince( getFirstPlayDate( plays ) )
	totalPlaysForPlot = []
	distinctGamesForPlot = []
	hIndicesForPlot = []
	for date in datesForPlot:
		# Calculate counts per game for this date.
		# Could be done incrementally instead of from scratch every time.
		countPerGame = countPerGameFromPlaysSince( plays, date )
		# Calculate total plays for this date.
		totalPlaysForPlot.append( calcTotalPlays( countPerGame ) )
		# Calculate distinct games played for this date.
		distinctGamesForPlot.append( len( countPerGame ) )
		# Calculate h index for this date.
		hIndicesForPlot.append( calcHIndex( countPerGame ) )

	# addPlotLine( thePlot, datesForPlot, totalPlaysForPlot, 'total plays history' )
	# addPlotLine( thePlot, datesForPlot, distinctGamesForPlot, 'games played history' )
	# addPlotLine( thePlot, datesForPlot, hIndicesForPlot, 'h index history' )

	fig, ax1 = plt.subplots()

	color = 'tab:blue'
	ax1.set_xlabel( 'time' )
	ax1.set_ylabel( 'games/plays played', color=color )
	ax1.plot( datesForPlot, totalPlaysForPlot, color=color )
	ax1.plot( datesForPlot, distinctGamesForPlot, color='tab:green' )
	ax1.tick_params( axis='y', labelcolor=color )

	ax2 = ax1.twinx()
	color = 'tab:red'
	ax2.set_ylabel( 'h index', color=color )
	ax2.plot( datesForPlot, hIndicesForPlot, color=color )
	ax2.tick_params( axis='y', labelcolor=color )

	fig.tight_layout()
	# plt.plot( datesForPlot, totalPlaysForPlot, 'b' )
	# plt.plot( datesForPlot, distinctGamesForPlot, 'r' )
	# plt.plot( datesForPlot, hIndicesForPlot, 'g' )
	plt.title( 'BGG history' )
	plt.show()

def getHGames( countPerGame, h ):
	hGames = []
	for game in countPerGame:
		if ( countPerGame[game] >= h ):
			hGames.append( game )
	return hGames

def printHIndexHistory():
	plays = readPlays()
	maxH = 0
	for date in getDateListSince( getFirstPlayDate( plays ) ):
		# Calculate counts per game for this date.
		# Could be done incrementally instead of from scratch every time.
		countPerGame = countPerGameFromPlaysSince( plays, date )
		# Calculate h index for this date.
		h = calcHIndex( countPerGame )
		# if ( dateFromStr( '2015-11-08' ) <= date and date <= dateFromStr( '2015-11-15' ) ):
		# 	print( '{}, h: {}'.format( date, h ) )
		# 	print( countPerGame )
		if ( h > maxH ):
			maxH = h
			# print( countPerGame )
			hGames = getHGames( countPerGame, h )
			hGames.sort()
			print( '{}, H: {}, {} games: {}'.format( date.strftime('%Y-%m-%d'), h, len(hGames), hGames ) )

def printStats():
	plays = readPlays()
	countPerGame = countPerGameFromPlays( plays )
	print( 'Current H index: {}'.format( calcHIndex( countPerGame ) ) )
	dimeCount = calcCountMoreThan( countPerGame, 10 )
	print( 'Current # dimes: {}'.format( dimeCount ) )
	print( 'Current # fives: {}'.format( calcCountMoreThan( countPerGame, 5 ) ) )
	printCounts( countPerGame, dimeCount )

def getInput( question ):
	inputText = question + ' (Y/y) for yes. --> '
	answer = input( inputText )
	return answer.lower() == 'y'

def main():
	if getInput( 'Update play history?' ):
		updateXMLFilesFromWeb()

	if getInput( 'Plot graphs?' ):
		plotCountsAndGamesAndH()

	if getInput( 'Print H-index history?' ):
		printHIndexHistory()

	if getInput( 'Print stats?' ):
		printStats()
		

if __name__ == "__main__":
	main()