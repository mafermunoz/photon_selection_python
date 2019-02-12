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
psd_y1=-310.7
psd_y2=-324.7
psd_x1=-284.5
psd_x2=-298.5
BGOz=np.array([58.5,87.5,116.5,145.5,174.5,203.5,232.5,261.5,290.5,319.5,348.5,377.5,406.5,435.5])

def elayers(event):
    ##Get energy deposited in each layer of BGO
    d_arr=np.zeros([14])
    for i in range(N_LAYERS_BGO):
        d_arr[i]=event.pEvtBgoRec().GetELayer(i)
        if(d_arr[i]<1):
            d_arr[i]=-5
    return d_arr

def ene_max_bar(event):
    ##Get the bar with the number of the bar with the maximum deposited energy per layer
    d_arr=np.zeros([14])
    for i in range (N_LAYERS_BGO):
        d_arr[i]=event.pEvtBgoRec().GetELayerMaxBar(i)
    return d_arr

def num_maxlayer(event):
    ##Get the layer with the maximum energy deposited
        arr=elayers(event)
        return np.argmax(arr)


def num_max_bar(event):
    ## Get the bar deposited in the BGO bar with the maximum energy deposition for each bar
    a=ene_max_bar(event)
    d_arr=np.zeros([14])
    for i in range (N_LAYERS_BGO):
        for j in range (N_BARS_BGO):
            if(a[i]==event.pEvtBgoRec().GetEdep(i,j)):
                #d_arr[i]=event.pEvtBgoRec().GetEdep(i,j)
                d_arr[i]=j
    return d_arr


def corner_bars(event,n=4):
 ## Returns the number of bars that  have their maximum energy depostion in the corners of the detector, n is the number  of layer we look into(default the fisrt 4 layers due to the typical shower shape of photons)
    x=0
    d=num_max_bar(event)
    ene=ene_max_bar(event)
    for i in range (n):
        if ((d[i]==0 or d[i]==21) and ene[i]>1):
            x=x+1

def mip_event(event):
    #returns the number of layers where the energy deposited is similar to that of a mip_event
    mip=0
    arr=ene_max_bar(event)
    for i in range (arr):
        if(arr[i]<55 and arr[i]>1):
            mip=mip+1

    return 0

def max_ene_psd(event,nhits_psd):
    max_energy_psd=np.zeros(4)#y1,y2,x1,x2
    psd_max=np.array([-5,-5,-5,-5])
    for i in range (nhits_psd):
        z_psd=event.pEvtPsdHits().GetHitZ(i)
        if(z_psd==psd_y1):
            if(event.pEvtPsdHits().fEnergy[i]>=max_energy_psd[0]):#Change potentially to > onlu wihtout the equal.
                max_energy_psd[0]=event.pEvtPsdHits().fEnergy[i]
                psd_max[0]=i
        if(z_psd==psd_y2):
             if(event.pEvtPsdHits().fEnergy[i]>=max_energy_psd[1]):#Change potentially to > onlu wihtout the equal.
                 max_energy_psd[1]=event.pEvtPsdHits().fEnergy[i]
                 psd_max[1]=i
        if(z_psd==psd_x1):
             if(event.pEvtPsdHits().fEnergy[i]>=max_energy_psd[2]):#Change potentially to > onlu wihtout the equal.
                 max_energy_psd[2]=event.pEvtPsdHits().fEnergy[i]
                 psd_max[2]=i
        if(z_psd==psd_x2):
             if(event.pEvtPsdHits().fEnergy[i]>=max_energy_psd[3]):#Change potentially to > onlu wihtout the equal.
                 max_energy_psd[3]=event.pEvtPsdHits().fEnergy[i]
                 psd_max[3]=i
    return (max_energy_psd,psd_max)

def min_ene_cut_psd(max_energy_psd,ene_cut=2):
    if(max_energy_psd[0]>ene_cut and max_energy_psd[1]>ene_cut and max_energy_psd[2]>ene_cut and max_energy_psd[3]>ene_cut):
        return True
    else:
        return False

def min_combined_ene_cut_psd(max_energy_psd,ene_cut=2):
    if((max_energy_psd[2]+max_energy_psd[3])>=ene_cut and (max_energy_psd[0]+max_energy_psd[1])>=ene_cut):
        return True
    else:
        return False

def track_projection_psd(track):
    projection=np.zeros(4)#y1,y2,x1,x2
    projection[0]=track.getDirection().y()*(psd_y1-track.getImpactPoint().z())+track.getImpactPoint().y()
    projection[1]=track.getDirection().y()*(psd_y2-track.getImpactPoint().z())+track.getImpactPoint().y()
    projection[2]=track.getDirection().x()*(psd_x1-track.getImpactPoint().z())+track.getImpactPoint().x()
    projection[3]=track.getDirection().x()*(psd_x2-track.getImpactPoint().z())+track.getImpactPoint().x()
    return projection
def track_bgo_projection(track,num_maxlayer):
    p=np.zeros(2)
    p[0]=track.getDirection().x()*(BGOz[num_maxlayer]-track.getImpactPoint().z())+track.getImpactPoint().x()
    p[1]=track.getDirection().y()*(BGOz[num_maxlayer]-track.getImpactPoint().z())+track.getImpactPoint().y()
    return p


def psd_hit_pos(k,event):
    p=np.zeros(3)#x,y,z
    p[0]=event.pEvtPsdHits().GetHitX(k)
    p[1]=event.pEvtPsdHits().GetHitY(k)
    p[2]=event.pEvtPsdHits().GetHitZ(k)
    return p


def match_track_psd(pos_psd_hit,track_projection,window=18):
    if(pos_psd_hit<(track_projection+window) and (pos_psd_hit>(track_projection-window))):
        return True
    else:
        return False

def match_track_psd_cross_max(match,k,psd_max):
    if (match==True and (psd_max==k)):
        return 1
    else:
        return 0

def match_track_psd_cross_noise(match,k,energy_cut=0.3):
    if(match==True and (event.pEvtPsdHits().fEnergy[k])<=energy_cut):
        return 1
    else:
        return 0

def match_track_psd_count_psd_hits(match,k):
    if(match==True):
        return 1
    else:
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
        nTracks=event.NStkKalmanTrack()
        #nTracks=
        #print nTracks
        if(nTracks==0): continue
        nhits_psd=event.pEvtPsdRec().GetTotalHits()
        #print nhits_psd
        if(nhits_psd>35):continue
        max_energy_psd, psd_max=max_ene_psd(event,nhits_psd)
        max_energy_psd_y=max_energy_psd[0]+max_energy_psd[1]
        max_energy_psd_x=max_energy_psd[2]+max_energy_psd[3]

        if(min_ene_cut_psd(max_energy_psd)==True):##I dont think this cut is relevant if I have the value afterwards
            continue
        if(min_combined_ene_cut_psd(max_energy_psd)==True):
            continue
        for j in range(nTracks):
            track=event.pStkKalmanTrack(j)
            theta_track=track.getDirection().Theta()*180/pi
            plane=track.getImpactPointPlane()
            if(plane==0):
                continue
            if(track.GetNPoints()<(6-plane)):
                continue
            track_psd_projection=track_projection_psd(track)
            if(np.abs(track_psd_projection[2])>=400 or np.abs(track_psd_projection[1])>=400):
                continue
            counter_psd=np.zeros(3)
            for k in range (nhits_psd):
                pos_psd_hits=psd_hit_pos(k,event)
                if(pos_psd_hits[2]==psd_y1):
                    match=match_track_psd(pos_psd_hits[1],track_psd_projection[0])
                    counter_psd[0]=counter_psd[0]+match_track_psd_cross_max(match,k,psd_max[0])
                    counter_psd[1]=counter_psd[1]+match_track_psd_cross_noise(match,k)
                    counter_psd[2]=counter_psd[2]+match_track_psd_count_psd_hits(match,k)

                if(pos_psd_hits[2]==psd_y2):
                    match=match_track_psd(pos_psd_hits[1],track_psd_projection[1])
                    counter_psd[0]=counter_psd[0]+match_track_psd_cross_max(match,k,psd_max[1])
                    counter_psd[1]=counter_psd[1]+match_track_psd_cross_noise(match,k)
                    counter_psd[2]=counter_psd[2]+match_track_psd_count_psd_hits(match,k)

                if(pos_psd_hits[2]==psd_x1):
                    match=match_track_psd(pos_psd_hits[0],track_psd_projection[2])
                    counter_psd[0]=counter_psd[0]+match_track_psd_cross_max(match,k,psd_max[2])
                    counter_psd[1]=counter_psd[1]+match_track_psd_cross_noise(match,k)
                    counter_psd[2]=counter_psd[2]+match_track_psd_count_psd_hits(match,k)

                if(pos_psd_hits[2]==psd_x2):
                    match=match_track_psd(pos_psd_hits[0],track_psd_projection[3])
                    counter_psd[0]=counter_psd[0]+match_track_psd_cross_max(match,k,psd_max[3])
                    counter_psd[1]=counter_psd[1]+match_track_psd_cross_noise(match,k)
                    counter_psd[2]=counter_psd[2]+match_track_psd_count_psd_hits(match,k)

                crossing=counter_psd[2]-counter_psd[1]
                if(crossing>0):
                    continue
                if((counter_psd[0]-counter_psd[1])>1):
                    continue

                bgo_stk_proj=track_bgo_projection(track,num_maxlayer(event))

                if(np.abs(bgo_stk_proj[0])>300 or np.abs(bgo_stk_proj[1])>300):
                    continue
                for l in range (num_maxlayer(event)+2):
                    a=l

        print i
if __name__ == '__main__':

    main(sys.argv[1])
