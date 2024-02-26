"""
Run this script to prepare the Fashion dataset.

1. Download files from https://www.kaggle.com/paramaggarwal/fashion-product-images-dataset/version/1 and place in
    data/fashionNet/
2. Run the script

"""
from few_shot.utils import mkdir, rmdir
from config import DATA_PATH
import pandas as pd
from tqdm import tqdm as tqdm
import numpy as np
import natsort
import shutil
import os
import sys
sys.path.append('../')

# Creating and deleting folder/files
rmdir(DATA_PATH + '/fashionNet/images_background')
rmdir(DATA_PATH + '/fashionNet/images_evaluation')
rmdir(DATA_PATH + '/fashionNet/refac_Images')
mkdir(DATA_PATH + '/fashionNet/images_background')
mkdir(DATA_PATH + '/fashionNet/images_evaluation')
mkdir(DATA_PATH + '/fashionNet/refac_Images')

print("Is the DATA_PATH is Correct?", os.path.exists(
    DATA_PATH + '/fashionNet/images/'))

'''
Directory File Name Change
1. styles.csv to map image_id and subCategory, class_laebls, meta_sets
2. Rename the images using os.rename() for support and query split
'''

_classes = []
split = []
PATH = os.path.join(DATA_PATH, 'fashionNet/styles.csv')
df = pd.read_csv(PATH, engine='python')
df = df.drop(['Unnamed: 10', 'Unnamed: 11'], axis=1)
df = df.sort_values(by=['id'], ascending=True, inplace=False)
df['class_id'] = df.apply(lambda row: str(
    row['articleType']) + '__' + str(row['id']) + '.jpg', axis=1)
for name in df['class_id']:
    _classes.append(name)

'''
_classes: ['Tshirts__1163.jpg', 'Tshirts__1164.jpg', 'Bagpacks__1165.jpg', 
		'Bagpacks__1525.jpg', 'Bagpacks__1526.jpg']
Format: [ articleType__image_id]

'''
for root, _, files in os.walk(DATA_PATH + '/fashionNet/images/'):
    dirFiles = natsort.natsorted(files, reverse=False)
    for name in range(len(_classes)):
        src_dir = os.path.join(
            DATA_PATH + '/fashionNet/images/', dirFiles[name])
        dst_dir = DATA_PATH + \
            '/fashionNet/refac_Images/{}'.format(_classes[name])
        os.rename(src_dir, dst_dir)

# Find class identities
classes = []
for root, _, files in os.walk(DATA_PATH + '/fashionNet/refac_Images/'):
    for f in files:
        if f.endswith('.jpg'):
            f = f.split('__')
            classes.append(f[0])

class_name = list(set(classes))
# print(len(class_name))

# Meta Training and Testing Split (Support and Query set)
meta_train_PATH = DATA_PATH + '/fashionNet/Meta/meta_train.csv'
meta_train_class = []
df_train = pd.read_csv(meta_train_PATH, engine='python')
for items in df_train['meta_train']:
    meta_train_class.append(items)

meta_test_PATH = DATA_PATH + '/fashionNet/Meta/meta_test.csv'
meta_test_class = []
df_test = pd.read_csv(meta_test_PATH, engine='python')
for items in df_test['meta_test']:
    meta_test_class.append(items)

df_meta_training = df[df['articleType'].isin(meta_train_class)]
meta_train_id = df_meta_training['articleType'].tolist()
df_meta_testing = df[df['articleType'].isin(meta_test_class)]
meta_test_id = df_meta_testing['articleType'].tolist()


background_classes = list(set(meta_train_id))
evaluation_classes = list(set(meta_test_id))

# Create class folders
for c in background_classes:
    mkdir(DATA_PATH + '/fashionNet/images_background/{}/'.format(c))

for c in evaluation_classes:
    mkdir(DATA_PATH + '/fashionNet/images_evaluation/{}/'.format(c))

# Move images to correct location
for root, _, files in os.walk(DATA_PATH + '/fashionNet/refac_Images'):
    for f in tqdm(files, total=len(files)):
        if f.endswith('.jpg'):
            name = f.split('__')
            class_name = name[0]
            image_name = name[0] + '__' + name[1]
            # Send to correct folder
            if class_name not in (evaluation_classes + background_classes):
                continue
            subset_folder = 'images_evaluation' if class_name in evaluation_classes else 'images_background'
            src = '{}/{}'.format(root, f)
            dst = DATA_PATH + \
                '/fashionNet/{}/{}/{}'.format(subset_folder,
                                              class_name, image_name)
            shutil.copy(src, dst)  # Time Complexity O(n), for n num_of samples
