from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np
from glob import glob
import re

SUBSET = True

path = "../KeyFramesExtraction/Result/"
df = pd.read_csv('../Annotations/processedAnnotations_no_corrupted_videos.csv')
count = df.groupby(['CM']).count()['palavra']
threshold = 20
frames = 10
cnn_dataset_path = "./datasets/CNN"

classes_subset = ['cg14', 'cg63', 'cg02', 'cg64', 'cg47', 'cg07', 'cg01']


def getFrameNumber(path):
    return int(re.search(r".*\/frame(\d+)\.jpg", path).group(1))


def getFiles(path, drop_edges=False):
    files = list(glob(path + "/*.jpg"))
    if(len(files) == 0):
        print(path)
    files.sort(key=getFrameNumber)
    if drop_edges:  # Remove the first and the last frames
        files.pop()  # Remove last
        files.pop(0)  # Remove first
    return files


def replaceClass(cg):
    quantity = count[cg]
    if quantity <= threshold:
        return 'others'
    else:
        return cg


if SUBSET:
    df = df.query('CM in @classes_subset')

df['classe'] = df['CM'].map(replaceClass)
df['classe'] = df['classe'].astype('category')

df = df[['palavra', 'classe']]

df['first_letter'] = df['palavra'].map(lambda x: x[0])
df['folder_path'] = path + f'{frames}/' + df['first_letter'] + '/' + df['palavra'] + '/'

# df['files_list'] = df['folder_path'].map(getFiles)
df['files_list'] = df['folder_path'].map(lambda x: getFiles(x, True))

y = to_categorical(df['classe'].cat.codes.values)
X_train, X_test, y_train, y_test = train_test_split(df['files_list'], y, stratify=y,
                                                    test_size=0.2, random_state=0)
y_train = np.repeat(y_train, X_train.map(len), axis=0)
y_test = np.repeat(y_test, X_test.map(len), axis=0)
X_train_sum = np.array(X_train.sum())
X_test_sum = np.array(X_test.sum())

if SUBSET:
    np.save(cnn_dataset_path + '/X_train_no_edge_frames_subset.npy', X_train_sum)
    np.save(cnn_dataset_path + '/X_test_no_edge_frames_subset.npy', X_test_sum)
    np.save(cnn_dataset_path + '/y_train_no_edge_frames_subset.npy', y_train)
    np.save(cnn_dataset_path + '/y_test_no_edge_frames_subset.npy', y_test)
else:
    np.save(cnn_dataset_path + '/X_train_no_edge_frames.npy', X_train_sum)
    np.save(cnn_dataset_path + '/X_test_no_edge_frames.npy', X_test_sum)
    np.save(cnn_dataset_path + '/y_train_no_edge_frames.npy', y_train)
    np.save(cnn_dataset_path + '/y_test_no_edge_frames.npy', y_test)
