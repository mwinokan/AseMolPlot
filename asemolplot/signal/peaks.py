
import mout

import statistics

from .modify import differentiate

from scipy.optimize import curve_fit
from scipy import asarray as ar,exp


def peakFinder(xdata,ydata,min_width,min_height,baseline=None,threshold=1.0e-2,search_coeff=0.1):

	many = any(isinstance(el,list) for el in ydata)

	xdata,dydx = differentiate(xdata,ydata)

	if many:

		peaklist = []

		# mout.errorOut("peakFinder. Unsupported",fatal=True)

		for data in ydata:
			peaklist.append(peakFinder(xdata,data,
									   min_width,min_height,
									   baseline=baseline,
									   threshold=threshold,
									   search_coeff=search_coeff))

		all_peaks = peaklist

	else:

		if baseline is None:
			y_avg = statistics.mean(ydata)
		else:
			y_avg = baseline

		# print(y_avg)

		found = False

		all_peaks = []

		for i,y in enumerate(ydata):

			this_height = y - y_avg

			if this_height > min_height and abs(dydx[i]) < threshold:

				# print(xdata[i],y,this_height,abs(dydx[i]))

				skip = False
				for peak in all_peaks:
					if peak.in_range(xdata[i]):
						skip = True
						break

				if skip: continue

				# backwards search for the start of the peak
				backsearch_i = i
				backsearch_height = this_height

				while backsearch_height > min_height*search_coeff:

					backsearch_i -= 1
					if backsearch_i <= 0:
						break
					# print(backsearch_i)
					backsearch_height = ydata[backsearch_i] - y_avg

				mout.varOut("Peak start estimated at",xdata[backsearch_i])

				# forwards search for the start of the peak
				foresearch_i = i
				foresearch_height = this_height

				while foresearch_height > min_height*search_coeff:

					foresearch_i += 1
					if foresearch_i >= len(ydata)-1:
						break
					foresearch_height = ydata[foresearch_i] - y_avg

				mout.varOut("Peak end estimated at",xdata[foresearch_i])

				all_peaks.append(Peak(xdata[backsearch_i],xdata[foresearch_i]))

	return all_peaks

class Peak:

	def __init__(self,start_x,end_x):

		self.start_x = start_x
		self.end_x = end_x

	def __str__(self):
		return "Peak["+str(self.start_x)+":"+str(self.end_x)+"]"

	def __repr__(self):
		return "Peak["+str(self.start_x)+":"+str(self.end_x)+"]"

	def in_range(self,x):
		if x >= self.start_x and x <= self.end_x:
			return True
		else:
			return False

	def gauss_fit(self,xdata,ydata,return_data=False,baseline=0.0,filename=None):
		return gaussian_fit(xdata,ydata,[self.start_x,self.end_x],return_data=return_data,baseline=baseline,filename=filename)

def gaussian_fit(xdata,ydata,window,return_data=False,index_window=False,baseline=0.0,filename=None):

	many = any(isinstance(el,list) for el in ydata)

	if many:
		mout.errorOut("gaussian_fit. Unsupported.",fatal=True)

	if index_window:
		x = ar(xdata[window[0]:window[1]])
		y = ar(ydata[window[0]:window[1]])
	else:
		index1=closest_index(window[0],xdata)
		index2=closest_index(window[1],xdata)
		x = ar(xdata[index1:index2])
		y = ar(ydata[index1:index2])

	n = len(x)                          #the number of data
	mean = sum(x*y)/n           
	sigma = sum(y*(x-mean)**2)/n
	
	mean = x[len(x)//2]
	sigma = (x[-1]-x[0])/4

	import mplot

	
	# print(1.0,mean,sigma)

	global ___BASELINE
	___BASELINE = baseline

	try:
		popt,pcov = curve_fit(gaus,x,y,p0=[1,mean,sigma])
	except:
		mplot.graph2D(x,y,filename=filename,show=False)
		return False

	a,mean,sigma = popt

	# print(a,mean,sigma)

	if return_data:
		gaus_y = []
		for this_x in xdata:
			gaus_y.append(gaus(this_x,*popt))
		if filename is not None:
			mplot.graph2D(x,[y,gaus_y[index1:index2]],filename=filename,show=False)
		return a,mean,sigma,xdata,gaus_y
	else:
		return a,mean,sigma

def gaus(x,a,x0,sigma):
    return a*exp(-(x-x0)**2/(2*sigma**2))+___BASELINE

def closest_index(value,xdata):

	for i,x in enumerate(xdata):

		if x > value:

			if abs(xdata[i-1]-value) < abs(xdata[i]-value):
				return i
			else:
				return i-1

