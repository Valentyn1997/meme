import pandas as pd
import numpy as np

def closest_emoji(V, A, n=5):
    '''function to find n closest emojis basing on valence and arousal scores'''
    dists = []
    emoji_va = pd.read_csv('emoji_va_scores.csv')
    for index, emoji in emoji_va.iterrows():
        diff_V = emoji.V - V
        diff_A = emoji.A - A
        euclid_dist = np.power(np.power(diff_V, 2) + np.power(diff_A, 2), 0.5)
        emoji_va.loc[index, 'dist'] = euclid_dist
    emoji_va = emoji_va.sort_values(by='dist')
    return emoji_va.iloc[0:n, :].Emoji