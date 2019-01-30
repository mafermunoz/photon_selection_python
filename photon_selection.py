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

def main(inputfile,outputpath=''):

    f=TFile.Open(inputfile)
    myTree=ROOT.DmpChain("CollectionTree")
    myTree.Add(f)
    n_entries=myTree.GetEntries()
    print(n_entries)

    new_file=outputpath+inputfile.split("/")[-1].replace(".root","_photons.root")
    output_file=TFile(new_file,'recreate')

    for i in range (n_entries):
        event=myTree.GetDmpEvent(i)
        print event.pEvtBgoRec().GetTotalEnergy()






if __name__ == '__main__':

    main(sys.argv[1])
