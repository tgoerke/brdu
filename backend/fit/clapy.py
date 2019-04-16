import numpy as np
import scipy as sp
import scipy.stats

import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox, TransformedBbox, blended_transform_factory
from mpl_toolkits.axes_grid1.inset_locator import BboxConnector
import matplotlib.lines as pltlines
import matplotlib.transforms as plttransformsimport 
import json
from iminuit import Minuit
import warnings


def calc_statistic(dataframe,parameter):
    tmp = dataframe.copy()
    try:
        tmp.rename({'GF_error' : 'GFf_error'}, axis="columns",inplace=True)
    except:
        pass
    for i in ['Tc','r','ss','sc','GFf']:
        try:
            tmp[i+'_2std'] = tmp[i+'_error'].mul(2)
            tmp[i+'_mse'] = tmp[i].sub(1).pow(2)
            tmp[i+'_d'] = tmp[i].sub(parameter[i])
            tmp[i+'_p'] = tmp[i+'_d'].abs() < tmp[i+'_2std']
            tmp[i+'_p2'] = np.logical_and( tmp[i+'_hpd46_l'] < parameter[i] ,parameter[i] < tmp[i+'_hpd46_u']    )
        except:
            print(i+' not found')
    sdata = tmp.mean(level=['model','sPopulation','sSample','M','GF'])
    for i in ['Tc','r','ss','sc','GFf']:
        try:
            sdata[i+'_mse'] = sdata[i+'_mse'].pow(0.5)
        except:
            print(i+' not found')
    return tmp,sdata

def ecdf(x):
    ''' calc emerical cdf '''
    xs = np.sort(x)
    ys = np.arange(1, len(xs)+1)/float(len(xs))
    return xs, ys


class asym_lh:
    ''' class with the likelihood for the asymetric cell labelling assays 
        usable for minuit
    '''

    def __init__(self,data,times,ncell):
        ''' data = number of labeld cells
            times = time for labeling fraction
            ncell = number of cells 
        '''
        self.data = np.round(data)
        self.datalen = np.size(data)
        self.times = times
        if np.size(ncell) !=  self.datalen:
            self.ncell = np.ones_like(data,dtype=np.int32)*ncell
        else:
            self.ncell = ncell

    def compute(self, Tc,r,GF,sigma_cell,sigma_sample):
        ''' compute log liklyhood for parameters given
        '''
        pmf = self.pmf_f(Tc,r,GF,sigma_cell,sigma_sample) 
        pmf[np.abs(pmf) < 1e-300] = 1e-300 #fix nan in log
        return np.sum(-np.log( pmf) )
        #return np.sum(-np.log( self.pmf_f(Tc,r,GF,sigma_cell,sigma_sample) ) )


    def log_params(self, mu, sigma):
        """ A transformation of paramteres such that mu and sigma are the
            mean and variance of the log-normal distribution and not of
            the underlying normal distribution.
        """
        s2 = np.log(1.0 + sigma**2/mu**2)
        m = np.log(mu) - 0.5 * s2
        s = np.sqrt(s2)
        return m, s

    def pdf_LN(self, X, mu, sigma):
        ''' lognormal pdf with actual miu and sigma
        '''
        mu_tmp, sigma_tmp = self.log_params(mu, sigma)
        return sp.stats.lognorm.pdf(X, s=sigma_tmp, scale = np.exp(mu_tmp))

    def logn(self, sigma_cell,Tc,r,n):
        '''  def logn(t,sigma_cell,Tc,r):
             analytic solution for cell only noise
        '''
        mean,sigma = self.log_params(Tc,sigma_cell)
        la = np.log(self.times[n]/(1-r))
        idf = 0.5 * ( 1 + sp.special.erf(  (mean - la) / (np.sqrt(2) * sigma) )  )
        int2 = 0.5 * np.exp( -mean + 0.5 * sigma * sigma ) * sp.special.erfc(  ( -mean + sigma*sigma + la ) / (np.sqrt(2)*sigma) )
        return 1-1*idf+r*idf+self.times[n]*int2



    def pmf_f(self, Tc,r, GF, sigma_cell,sigma_sample):
        """ pmf for the number of labelled cells
            to test: using epsabs=0.1 and epsrel=0.1 in quad might significantly
            speed up the computation without loosing too much precision
        """
        self.Tc = Tc
        self.r = r
        self.GF = GF
        self.sigma_cell = sigma_cell
        self.sigma_sample = sigma_sample

        #P =[sp.integrate.quadrature(self.f, 0.0001, Tc+(sigma_sample*10),args=([i]),tol=1.48e-08, rtol=1.48e-08)[0] for i in range(self.datalen)]
        #P = [sp.integrate.fixed_quad(self.f, 0.0001, Tc+(sigma_sample*10),n=100,args=([i]))[0] for i in range(self.datalen)]
        P = [sp.integrate.fixed_quad(self.f, max(0.0001,Tc-(sigma_sample*5)), Tc+(sigma_sample*10),n=200,args=([i]))[0] for i in range(self.datalen)]
        return np.array(P)

    def f(self, TC_,n):
        return sp.stats.binom.pmf(self.data[n], self.ncell[n], self.GF*self.logn(self.sigma_cell,TC_,self.r,n) ) * self.pdf_LN(TC_, self.Tc, self.sigma_sample)
    
    
class dist:
    ''' distribution for the asymetric labelling assay   '''

    def __init__(self):
        pass

    def log_params(self, mu, sigma):
        """ A transformation of paramteres such that mu and sigma are the 
            mean and variance of the log-normal distribution and not of
            the underlying normal distribution.
        """
        s2 = np.log(1.0 + sigma**2/mu**2)
        m = np.log(mu) - 0.5 * s2
        s = np.sqrt(s2)
        return m, s

    def pdf_LN(self, X, mu, sigma):
        ''' lognormal pdf with actual miu and sigma
        '''
        mu_tmp, sigma_tmp = self.log_params(mu, sigma)
        return sp.stats.lognorm.pdf(X, s=sigma_tmp, scale = np.exp(mu_tmp))

    def logn(self, sigma_cell,Tc,r):
        '''  def logn(t,sigma_cell,Tc,r):
             analytic solution for cell only noise
        '''
        mean,sigma = self.log_params(Tc,sigma_cell)
        la = np.log(self.t/(1-r))
        idf = 0.5 * ( 1 + sp.special.erf(  (mean - la) / (np.sqrt(2) * sigma) )  )
        int2 = 0.5 * np.exp( -mean + 0.5 * sigma * sigma ) * sp.special.erfc(  ( -mean + sigma*sigma + la ) / (np.sqrt(2)*sigma) )
        return 1-1*idf+r*idf+self.t*int2



    def pmf_f(self,ncell,Tc,r, GF, sigma_cell,sigma_sample, t, x):
        """ pmf for the number of labelled cells
        """
        self.ncell = ncell
        self.Tc = Tc
        self.r = r
        self.GF = GF
        self.sigma_cell = sigma_cell
        self.sigma_sample = sigma_sample
        self.t = t
        
        #P =  sp.integrate.quadrature(self.f, 0.01, 11,args=([x]))[0] 
        P = sp.integrate.fixed_quad(self.f, max(0.0001,Tc-(sigma_sample*5)), Tc+(sigma_sample*10),n=200,args=([x]))[0]
        return P

    def f(self, TC_,x):
        return sp.stats.binom.pmf(x, self.ncell, self.GF*self.logn(self.sigma_cell,TC_,self.r) ) * self.pdf_LN(TC_, self.Tc, self.sigma_sample)

    def pmf_mean(self,ncell,Tc,r, GF, sigma_cell,sigma_sample, t):
        """ mean number of labelled cells
        """
        self.ncell = ncell
        self.Tc = Tc
        self.r = r
        self.GF = GF
        self.sigma_cell = sigma_cell
        self.sigma_sample = sigma_sample
        self.t = t
        
        #P =  sp.integrate.quadrature(self.fm, max(0.0001,Tc-(sigma_sample*5)), Tc+(sigma_sample*10))[0] 
        P = sp.integrate.fixed_quad(self.fm, max(0.0001,Tc-(sigma_sample*5)), Tc+(sigma_sample*10),n=200)[0]
        return ncell*P


    def fm(self, TC_):
        return  self.GF*self.logn(self.sigma_cell,TC_,self.r) * self.pdf_LN(TC_, self.Tc, self.sigma_sample)
    

@np.vectorize
def cla_det_model(t, G1=0.2, S=0.3, G2M=0.5, GF=1, mode=1, **kwargs):
    """ Model for labeling assays in vivo.
        Based on Lefevre et al., 2013 and extended with an initial
        growth fraction.
        
        t    ... time after start of labeling
        S    ... absolute length of S-Phase
        G1   ... absolute length of G1-Phase
        G2M  ... absolute length of G2-Phase and M-Phase
        rmode    ... mean number of daughter cells after cell division remaining
                 in the population
        GF   ... initial growth fraction
        
        Lefevre, J., Marshall, D. J., Combes, A. N., Ju, A. L., Little, M. H.
        & Hamilton, N. A. (2013). Modelling cell turnover in a complex tissue
        during development. Journal of Theoretical Biology, 338, 66-79.
    """
    r = mode
    TC = S + G1 + G2M
    if G2M < 0:
        return sp.nan
    if S + G2M > TC:
        return sp.nan
    else:
        if r==1:
            if t < TC - S:
                return GF * (t + S) / TC
            else:
                return GF
        else:
            # calculate the growth fraction at time t
            g = ( ( GF * r ** (t / TC) ) / ( GF * r ** (t / TC) + (1 - GF) ) )
            if t < G2M:
                return  g * ((r ** ( ( G2M + S ) / TC ) - r ** (( G2M - t ) / TC) ) / (r - 1.0) )
            elif t < TC - S:
                return g * (1.0 - ( r ** ( ( TC + G2M - t ) / TC ) - r ** ( ( G2M  + S) / TC ) ) / (r - 1.0) )
            else:
                return g


def web_fit(ncells,times,datas,opath,name):
    dat = np.array(datas)
    tim = np.array(times)
    ncell = np.array(ncells)

    Tc_init = np.max(tim)*0.5
    r_init = 0.5
    GF_init = np.mean(np.sort(dat)[-len(dat)//10:])
    Tc_lower = np.min(tim)
    Tc_upper = np.max(tim)
    error = Tc_init*0.1

    lh = asym_lh(dat,tim,ncell)
    mi = Minuit(lh.compute, Tc=Tc_init, r=r_init,GF=GF_init,sigma_sample=Tc_init*0.2,sigma_cell=Tc_init*0.2, \
               error_Tc=error,error_r=0.1,error_GF=0.1,error_sigma_sample=error,error_sigma_cell=error,\
               limit_Tc=(Tc_lower,Tc_upper), limit_r=(0.00001,1),limit_GF=(0,1),limit_sigma_sample=(0.00001,Tc_init),limit_sigma_cell=(0.00001,Tc_init),\
               errordef=0.5,print_level=0)
    mi.migrad();

    fit = dict()
    for i in  mi.values:
        fit.update( {i : {'value' : mi.values[i], '2sigma' : 2*mi.errors[i]}})

    fig = plt.figure(1,figsize=(5,4))


    tf2 = np.linspace(0.01,np.max(tim)*1.1,100)
    d = dist()
    prob = np.zeros(len(tf2))
    nc = np.mean(ncell)
    for t_n,t in enumerate(tf2):
        prob[t_n] = d.pmf_mean(nc,fit['Tc']['value'],fit['r']['value'],fit['GF']['value'],fit['sigma_cell']['value'],fit['sigma_sample']['value'],t)
    plt.plot(tim,dat/ncell,'k.',label='Measurements',zorder=4)
    colorp =  np.array([0.5647058823529412, 0.9333333333333333, 0.5647058823529412]) - np.array([0.4,0.1,0.4])
    plt.plot(tf2,prob/nc,label='probabilistic model',color=colorp,lw=2,zorder=2)
    plt.ylim(0,1.1)
    plt.legend()
    plt.xlabel('time [original units]')
    plt.ylabel('labeling fraction')

    fig.savefig(opath+"/" + name+'.png')
    plt.close(fig)
    return fit


