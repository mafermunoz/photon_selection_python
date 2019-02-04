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
    d_arr=np.zeros([14])
    for i in range(N_LAYERS_BGO):
        d_arr[i]=event.pEvtBgoRec().GetELayer(i)
        if(d_arr[i]<1):
            d_arr[i]=-5
    return d_arr

def e_max_bar(event):
    d_arr=np.zeros([14])
    for i in range (N_LAYERS_BGO):
        d_arr[i]=event.pEvtBgoRec().GetELayerMaxBar(i)


def num_maxlayer(arr):
        return np.argmax(arr)


def num_max_bar(event,e_max):
    d_arr=np.zeros([14])
    for i in range (N_LAYERS_BGO):
        for j in range (N_BARS_BGO):
            if(e_max[i]==event.pEvtBgoRec().GetEdep(i,j)):
                d_arr[i]=event.pEvtBgoRec().GetEdep(i,j)

    return d_arr





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
        d=elayers(event)





if __name__ == '__main__':

    main(sys.argv[1])
