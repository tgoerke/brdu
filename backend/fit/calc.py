import numpy as np
import scipy as sp
import scipy.stats
from iminuit import Minuit
import argparse
import warnings
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import json
from .clapy import asym_lh,dist,cla_det_model


def calc(ncells=None,times=None,datas=None,csvfile="fit/test.csv",opath="fit/static/123"):
    if ncells is None or times is None or datas is None: 
        dat,tim,ncell = np.loadtxt(csvfile).T
        dat = dat*ncell
    else:
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
    #          Tc=1.0, r=0.3,GF=1.0,sigma_sample=0.25,sigma_cell=0.3, \
    #          error_Tc=0.1,error_r=0.1,error_GF=0.1,error_sigma_sample=0.1,error_sigma_cell=0.1,\
    #          limit_Tc=(0.00001,2), limit_r=(0.00001,1),limit_GF=(0,1),limit_sigma_sample=(0.00001,1),limit_sigma_cell=(0.00001,1),\
               errordef=0.5,print_level=0)
    mi.migrad();

    fit = dict()
    for i in  mi.values:
        fit.update( {i : {'value' : mi.values[i], '2sigma' : 2*mi.errors[i]}})
    #with open(opath+'.json', 'w') as outfile:
    #    json.dump(fit, outfile)

    fig = plt.figure(1,figsize=(5,4))


    tf = np.linspace(0.01,np.max(tim)*1.1,1000)
    tf2 = np.linspace(0.01,np.max(tim)*1.1,100)
    d = dist()
    prob = np.zeros(len(tf2))
    nc = np.mean(ncell)
    for t_n,t in enumerate(tf2):
        prob[t_n] = d.pmf_mean(nc,fit['Tc']['value'],fit['r']['value'],fit['GF']['value'],fit['sigma_cell']['value'],fit['sigma_sample']['value'],t)
    plt.plot(tim,dat/ncell,'k.',label='Measurements',zorder=4)
    colorp =  np.array([0.5647058823529412, 0.9333333333333333, 0.5647058823529412]) - np.array([0.4,0.1,0.4])
    plt.plot(tf2,prob/nc,label='probabilistic model',color=colorp,lw=2,zorder=2)
    plt.plot(tf,cla_det_model(tf,fit['Tc']['value'],fit['r']['value'],fit['GF']['value']),label='Nowakowski model',color='#CC79A7',zorder=1)
    plt.ylim(0,1.1)
    plt.legend()
    plt.xlabel('time [original units]')
    plt.ylabel('labeling fraction')

    fig.savefig(opath+'.png')
    plt.close(fig)
    return fit

'''
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str,action="store",dest="csvfile",help="csv file")
    parser.add_argument("-o", "--output", type=str,action="store",dest="outname",help="creates name.json and name.png")
    args = parser.parse_args()

    warnings.filterwarnings('ignore')
    main(args.csvfile,args.outname)

'''


