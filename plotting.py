""" plotting.py
"""

# Author: Nick Kridler
from sklearn.metrics import roc_curve, auc
from scipy.stats import gaussian_kde
import pylab as pl
import numpy as np
def binaryHistogram(df,x,y,xlim=[],params={},labels={}):
	""" Plots a histogram of series

		Plots the histogram of a DataFrame column 
		conditioned on a binary labeled column.

		Args:
			df: pandas DataFrame
			x: column to histogram
			y: column containing binary condition
			xlim: x-bounds of plot
			params: dictionary containing pylab.hist parameters
			labels: dictionary containing axes labels

	"""
	#pl.figure()
	df[x].ix[df[y] == 0].hist(color='black',**params)
	df[x].ix[df[y] == 1].hist(color='red',**params)
	pl.xlim(xlim)
	pl.title(labels['title'])
	pl.xlabel(labels['xlabel'])
	pl.ylabel(labels['ylabel'])
	#pl.show()


def PlotROC(truth, prediction, printAuc=False):
	"""Plot a roc curve"""
	fpr, tpr, thresholds = roc_curve(truth, prediction)

	params = {'lw':3}
	if printAuc:
		roc_auc = auc(fpr,tpr)
		print "Area under the curve: %f" % roc_auc
		params['label'] = 'ROC curve (area = %0.2f)' % roc_auc
	pl.plot(fpr, tpr, **params)
	pl.ylim([0.0, 1.0])
	pl.xlim([0.0, 1.0])
	pl.xlabel('PFA')
	pl.ylabel('PD')
	if printAuc:
		pl.legend(loc="lower right")
	return			

def PlotDensity(prediction, labelStr, minval=None, maxval=None):
	"""Density plot"""
	if minval != None and maxval != None:
		prediction = (prediction - minval)/(maxval - minval)

	density = gaussian_kde(prediction)
	xs = np.linspace(0,1,200)
	density.covariance_factor = lambda : .1
	density._compute_covariance()
	pl.plot(xs, density(xs), lw=3, label=labelStr)
	pl.legend(loc="upper right")