## Program to create the  photon selection with python

#import matplotlib as plt
from __future__ import division
import numpy as np
import ROOT
from ROOT import  TFile, TTree, TH1F
ROOT.gSystem.Load('libDmpEvent.so')
import sys
import os
import yaml
import glob



pi=np.pi
N_LAYERS_BGO=int(14)
N_BARS_BGO=22

def elayers(event):
    ##Get energy deposited in each layer of BGO
    d_arr=np.zeros([14])
    for i in range(N_LAYERS_BGO):
        d_arr[i]=event.pEvtBgoRec().GetELayer(i)
        if(d_arr[i]<1):
            d_arr[i]=-5
    return d_arr

def num_max_bar(event):
    ##Get the bar with the number of the bar with the maximum deposited energy per layer
    d_arr=np.zeros([14])
    for i in range (N_LAYERS_BGO):
        d_arr[i]=event.pEvtBgoRec().GetELayerMaxBar(i)
    return d_arr

def num_maxlayer(event):
    ##Get the layer with the maximum energy deposited
        arr=elayers(event)
        return np.argmax(arr)


def e_max_bar(event,e_max):
    ## Get the energy deposited in the BGO bar with the maximum energy deposition for each bar
    d_arr=np.zeros([14])
    for i in range (N_LAYERS_BGO):
        for j in range (N_BARS_BGO):
            if(e_max[i]==event.pEvtBgoRec().GetEdep(i,j)):
                d_arr[i]=event.pEvtBgoRec().GetEdep(i,j)

    return d_arr


def corner_bars(event,n=4):
 ## Returns the number of bars that  have their maximum energy depostion in the corners of the detector, n is the number  of layer we look into(default the fisrt 4 layers due to the typical shower shape of photons)
    e_max_bar(event,)
    num_max_bar(event)


def mip_event():
#returns the number of layers where the energy deposited is similar to that of a mip_event
    return 0



def main(inputfile,outputpath='/atlas/users/mmunozsa/photon_selection_python'):

    #f=TFile.Open(inputfile)
    myTree=ROOT.DmpChain("CollectionTree")
    myTree.Add(inputfile)
    n_entries=myTree.GetEntries()
    print(n_entries)
    ## Create outputfile
    new_file=outputpath+inputfile.split("/")[-1].replace(".root","_photons.root")
    output_file=TFile(new_file,'recreate')
    newTree=myTree.CloneTree(0)
    ## Create numpy array where all the iimportant info will be saved
    output_np=np.zeros(n_entries,dtype=[('Energy','float64')])
    ##output_np=np.zeros(n_entries)

    for i in range (n_entries):
        event=myTree.GetDmpEvent(i)
        ene=event.pEvtBgoRec().GetTotalEnergy()
        output_np['Energy'][i]=ene
        core3=event.pEvtBgoRec().GetEnergyCore3()
        ##d=elayers(event)
        ##dd=e_max_bar(event)
        if (num_maxlayer(event)>4):
            continue

        ##ddd=num_max_bar(event,dd)





if __name__ == '__main__':

    main(sys.argv[1])
