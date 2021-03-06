import numpy as np
import pylab as pl
import pandas as pd
import scipy.sparse as sp
from sklearn.preprocessing import OneHotEncoder

NUMTRAIN = 32769
NUMTEST = 58921

def addIDColumn(df):
	"""Add an id column for joining later"""
	df['ID'] = map(lambda x: "%s.%06i"%(x[0],x[1]),
		zip(['train']*NUMTRAIN + ['test']*NUMTEST, range(NUMTRAIN) + range(NUMTEST)))
	return df

def buildPairs(x):
	"""Category Pairs"""
	pairs = []
	for i in xrange(len(x)):
		for j in xrange(i+1,len(x)): 
			pairs.append([x[i],x[j]])	
	return pairs

def buildTrips(x):
	"""Category Triplets"""
	pairs = []
	for i in xrange(len(x)):
		for j in xrange(i+1,len(x)): 
			for k in xrange(j+1,len(x)):
				pairs.append([x[i],x[j],x[k]])	
	return pairs

def buildQuads(x):
	"""Category Triplets"""
	pairs = []
	for i in xrange(len(x)):
		for j in xrange(i+1,len(x)): 
			for k in xrange(j+1,len(x)):
				for l in xrange(k+1,len(x)):
					pairs.append([x[i],x[j],x[k],x[l]])	
	return pairs

def sortAndMerge(df,key,fraction=0.42):
	""" Sort by column counts and merge to data frame"""
	# Sort the unique values by counts
	y = df[key].value_counts().order()[::-1]
	index = np.arange(y.size,dtype='int32')

	# Take the top N percent
	if fraction < 1.0:
		counts = int(y.size*fraction)
		while counts > 1:
			if y.values[counts-1] == y.values[counts]:
				counts -= 1
			else:
				break
		index[counts:] = counts

	suffix = 'Ids%03i'%(int(fraction*100))
	#suffix = 'Ids'
	df = pd.merge(df,
		pd.DataFrame({key:y.index,key+suffix:index}),
		how='inner',on=key,sort=False)
	return df

def add4grams(df,pairs,fraction=0.42):
	""" Turn trigrams into unique columns """
	keys = [ col for col in df.columns]
	df = addIDColumn(df)
	for pair in pairs:
		# Make a key using the column names
		key = '%s.%s.%s.%s'%(pair[0],pair[1],pair[2],pair[3])
		keys.append(key)

		# Create a new column containing the combo
		df[key] = map(lambda x: '%i.%i.%i.%i'%(x[0],x[1],x[2],x[3]),
			zip(df[pair[0]],df[pair[1]],df[pair[2]],df[pair[3]]))

		df = sortAndMerge(df,key,fraction=fraction)

	return df.ix[:,[c for c in df.columns if c not in keys]]

def addTrigrams(df,pairs,fraction=0.42):
	""" Turn trigrams into unique columns """
	keys = [ col for col in df.columns]
	df = addIDColumn(df)
	for pair in pairs:
		# Make a key using the column names
		key = '%s.%s.%s'%(pair[0],pair[1],pair[2])
		keys.append(key)

		# Create a new column containing the combo
		df[key] = map(lambda x: '%i.%i.%i'%(x[0],x[1],x[2]),
			zip(df[pair[0]],df[pair[1]],df[pair[2]]))

		df = sortAndMerge(df,key,fraction=fraction)

	return df.ix[:,[c for c in df.columns if c not in keys]]


def addBigrams(df,pairs,fraction=0.5):
	""" Turn bigrams into unique columns """
	keys = [ col for col in df.columns]
	df = addIDColumn(df)
	for pair in pairs:
		# Make a key using the column names
		key = '%s.%s'%(pair[0],pair[1])
		keys.append(key)

		# Create a new column containing the combo
		df[key] = map(lambda x: '%i.%i'%(x[0],x[1]),
			zip(df[pair[0]],df[pair[1]]))

		df = sortAndMerge(df,key,fraction=fraction)

	return df.ix[:,[c for c in df.columns if c not in keys]]

def threshold(df, fraction=1.0):
	""" Add the ability to threshold """
	h = df.columns
	col = dict([(y+'Ids',y) for y in df.columns])
	df = addIDColumn(df)
	if fraction == 1.0:
		return df 
	
	for c in h:
		df = sortAndMerge(df,c,fraction=fraction)

	df = df.ix[:,[c for c in df.columns if c not in h]]
	return df

class Fileio(object):
	""" Fileio helper """
	def __init__(self, train='../data/train.csv', test='../data/test.csv'):
		# Create a OneHotEncoder
		self.encoder = OneHotEncoder()
		self.trainDF = pd.read_csv(train,usecols=[0])
		self.trainDF['ID'] = map(lambda x: "%s.%06i"%(x[0],x[1]), zip(['train']*NUMTRAIN, range(NUMTRAIN)))

		self.testDF = pd.read_csv(test)
		self.testDF['ID'] = map(lambda x: "%s.%06i"%(x[0],x[1]), zip(['test']*NUMTEST, range(NUMTEST)))

	def encode(self,usecols):
		self.encoder.fit(np.array(self.df.ix[:,usecols],dtype='float'))

	def transformTrain(self,cols,idCol=8):
		""" Transform the training set"""
	
		x = pd.merge(self.trainDF,self.df.ix[:,[idCol]+cols],how='left',on='ID',sort=False)
		ignore = ['ID','ACTION']
		usecols = [c for c in x.columns if c not in ignore]
		return self.encoder.transform(np.array(x.ix[:,usecols],dtype='float')), np.array(x.ACTION)

	def transformTest(self,cols,idCol=8):
		""" Transform the testing set"""

		x = pd.merge(self.testDF.ix[:,['ID','ROLL_CODE']],self.df.ix[:,[idCol]+cols]
			,how='left',on='ID',sort=False)
		ignore = ['ID','ROLL_CODE']
		usecols = [c for c in x.columns if c not in ignore]
		return self.encoder.transform(np.array(x.ix[:,usecols],dtype='float'))

class RawInput(Fileio):
	""" Raw data """
	def __init__(self,filename='',usePairs=False,useTrips=False,useQuads=False,train='../data/train.csv',test='../data/test.csv'):
		Fileio.__init__(self,train,test)
		df = pd.read_csv(filename)

		x = [0.25,0.5,0.75,1.]
		for xx in x:
			self.df = threshold(df.copy(),fraction=xx)

		if usePairs:
			pairs = buildPairs(df.columns)
			for xx in x:
				self.df = pd.merge(self.df,addBigrams(df.copy(),pairs,fraction=xx),how='inner',on='ID')

		if useTrips:
			trips = buildTrips(df.columns)
			for xx in x:
				self.df = pd.merge(self.df,addTrigrams(df.copy(),trips,fraction=xx),how='inner',on='ID')

		if useQuads:
			quads = buildQuads(df.columns)
			for xx in x:
				self.df = pd.merge(self.df,add4grams(df.copy(),quads,fraction=xx),how='inner',on='ID')

class Preprocessed(Fileio):
	""" Preprocessed data """
	def __init__(self,filename='',train='../data/train.csv',test='../data/test.csv', cols=[]):
		Fileio.__init__(self,train,test)
		if len(cols) == 0:
			self.df = pd.read_csv(filename)
		else:
			self.df = pd.read_csv(filename,usecols=cols)
