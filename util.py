'''
Author: David Radke
Date: April 25, 2021
'''

import re, datetime, time, csv
import matplotlib.pyplot as plt
import pandas as pd
import urllib.request as rq
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
import numpy as np
import json
import os


def loadData(url):
    dataset = rq.urlopen(url)
    dataset = dataset.read()
    dataset = json.loads(dataset)

    return dataset

def loadMarketAvg(path):
    df = pd.read_csv(path)
    lows = np.array(df["Low"])
    highs = np.array(df["High"])
    avg = np.flip(np.mean(np.stack((lows, highs), axis=0).T,axis=1))
    # close = np.array(df["Close"])
    return avg

def meanALCX(alcx_price):
    start, end, step = 0, 24, 24
    mean_alcx = []
    while end <= alcx_price.size:
        mean_alcx.append(np.mean(alcx_price[start:end]))
        start+=step
        end+=step

    return np.array(mean_alcx)


def plotCompare(mean_alcx, market_avg, diffs, window):
    fig = plt.figure(figsize=(10, 6))
    mean_diffs = np.mean(diffs)
    diffs = (diffs - np.amin(diffs)) / (np.amax(diffs) - np.amin(diffs))
    for i, val in enumerate(diffs):
        plt.axvline(i, c='r', alpha=val,lw=10)
    # plt.plot(np.arange(diffs.shape[0]), diffs, label='Diffs')
    plt.plot(np.arange(mean_alcx.shape[0]), mean_alcx, c='b', label='ALCX')
    plt.plot(np.arange(market_avg.shape[0]), market_avg, c='g', label='CCI 30')
    plt.xlabel("Days Since Inception", fontsize=16)
    plt.ylabel("Normalized Price", fontsize=16)
    plt.text(mean_alcx.shape[0]-10, 0.0, "Mean Diff: "+str(round(mean_diffs,1)), fontsize=15, bbox=dict(facecolor='w', edgecolor='k', pad=3.0))
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.legend(fontsize=15)
    plt.title("Dynamic Time Warping ("+str(window)+" day window) with CCI30 and ALCX Price", fontsize=18)
    plt.show()

def doDTW(mean_alcx, market_avg, window=7):
    end = 0
    diffs = []
    while end <= market_avg.size:
        if (end-window) < 0:
            start = 0
        else:
            start = (end-window)
        focal = mean_alcx[start:end]
        target = market_avg[start:end]
        d, path = fastdtw(focal, target, dist=euclidean)
        diffs.append(d)
        end+=1
    return np.array(diffs)

#
# path = "data/cci30_OHLCV.csv"
# market_avg = loadMarketAvg(path)
#
#
# url = 'https://api.flipsidecrypto.com/api/v2/queries/43f66ead-faf9-4f46-9bae-29760810d3b0/data/latest'
# dataset = loadData(url)
#
# df = pd.DataFrame(dataset)
# df = df.sort_values('HOUR')
# alcx_price = np.array(df["PRICE"])[:-2]
#
#
# mean_alcx = meanALCX(alcx_price)
# market_avg = market_avg[(-1*mean_alcx.size):]
#
# # normalize
# mean_alcx = (mean_alcx - np.amin(mean_alcx)) / (np.amax(mean_alcx) - np.amin(mean_alcx))
# market_avg = (market_avg - np.amin(market_avg)) / (np.amax(market_avg) - np.amin(market_avg))
#
#
# diffs = doDTW(mean_alcx, market_avg, window=7)
#
# plotCompare(mean_alcx, market_avg, diffs)
#
#
# print(df)
# exit()
