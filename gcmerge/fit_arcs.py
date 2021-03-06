##############################
# Fit arcs to sharp features #
##############################

import numpy as np
from scipy import optimize
import gc
from points_above_gradient import find_points_above

def calc_R(x,y, xc, yc):
    """ calculate the distance of each 2D points from the center (xc, yc) """
    return np.sqrt((x-xc)**2 + (y-yc)**2)

def f(c, x, y):
    """ calculate the algebraic distance between the data points and the mean circle centered at c=(xc, yc) """
    Ri = calc_R(x, y, *c)
    return Ri - Ri.mean()

def leastsq_circle(x,y):
    # coordinates of the barycenter
    x_m = np.mean(x)
    y_m = np.mean(y)
    center_estimate = x_m, y_m
    center, ier = optimize.leastsq(f, center_estimate, args=(x,y))
    xc, yc = center
    Ri       = calc_R(x, y, *center)
    R        = Ri.mean()
    residu   = np.sum((Ri - R)**2)
    return xc, yc, R, residu

def fit_arc(img, islandlist, island, verbose=False):
	i = -1
	arcfit = np.empty((18,6))
	for mincontrast in np.arange(.9,0,-.05):
		i += 1
		arcfit[i,0] = mincontrast
		try:
			#select n points on either side of the central point
			feature = find_points_above(img, islandlist, island, mincontrast)[:,0]
			#this function is in islands.py
			xdata = feature[:,1]
			ydata = feature[:,0]
			arcfit[i, 1] = len(feature)
			fit = leastsq_circle(xdata, ydata)
			arcfit[i, 2:] = fit
			del(fit, xdata, ydata, feature)
			gc.collect()
			if verbose:
				print(mincontrast, " done")
		
		except (TypeError,IndexError):
			print(mincontrast, " not enough pts")
			continue
		except (RuntimeError):
			print(mincontrast, "no good fit")
			continue
	return arcfit
