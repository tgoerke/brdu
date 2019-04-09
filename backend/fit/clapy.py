import numpy as np
import scipy as sp
import scipy.stats

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
def cla_det_model(t, tc=0.2, f=0.3, GF=0.5, mode=1, **kwargs):
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
    TC = tc
    S = TC*f
    G2M = 0.5*(1-S)
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



