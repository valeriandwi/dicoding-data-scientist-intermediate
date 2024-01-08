# -*- coding: utf-8 -*-
"""NLP-Dicoding-Submission.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1qcHH3S0Qvh_VFlBk-Qyre7HIR4Z7Ap4p
"""

import pandas as pd

#load dataset
df = pd.read_csv("emotion.csv", sep=',')
df.head(10)

#get total data
df.shape

#get data info
df.info()

#get data count by categories
df.Emotion.value_counts()

"""**Cleansing Data**"""

#import and download package
import nltk, os, re , string

from keras.layers import Input, LSTM, Bidirectional, SpatialDropout1D, Dropout
from keras.models import Model
from keras.callbacks import EarlyStopping
from keras.preprocessing.text import Tokenizer, text_to_word_sequence
from keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet as wn

nltk.download('wordnet')
nltk.download('stopwords')

#lower case words
df.Text = df.Text.apply(lambda x: x.lower())

#remove functuation
def rem_fun(data) :
  return(data.translate(str.maketrans('','', string.punctuation)))
  df.Text = df.Text.apply(lambda x : cleaner(x))

# remove stopword
st_words = stopwords.words()
def stopword(data):
    return(' '.join([w for w in data.split() if w not in st_words ]))
    df.Text = df.Text.apply(lambda x: stopword(x))

df.head(10)

#data emotion
emotion = pd.get_dummies(df.Emotion)
df_emotion = pd.concat([df, emotion], axis=1)
df_emotion = df_emotion.drop(columns='Emotion')
df_emotion.head(10)

text = df_emotion['Text'].values
label = df_emotion[['anger','fear','happy','love','sadness','surprise']].values

text

label

#Split data into training and validation
from sklearn.model_selection import train_test_split
text_train, text_test, label_train, label_test = train_test_split(text, label, test_size=0.2, shuffle=True)

#Show splitted dataset size
print(text_train.shape)
print(text_test.shape)

#Tokenizer
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

tokenizer = Tokenizer(num_words=5000, oov_token = 'OOV', filters='!"#$%&()*+,-./:;<=>@[\]^_`{|}~ ')
tokenizer.fit_on_texts(text_train)
tokenizer.fit_on_texts(text_test)

sequence_train = tokenizer.texts_to_sequences(text_train)
sequence_test = tokenizer.texts_to_sequences(text_test)

padded_train = pad_sequences(sequence_train)
padded_test = pad_sequences(sequence_test)

#Create Model
import tensorflow as tf
model = tf.keras.Sequential([
    tf.keras.layers.Embedding(input_dim=5000, output_dim=64),
    tf.keras.layers.LSTM(128),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(6, activation='softmax')
])
model.compile(optimizer='adam', metrics=['accuracy'], loss='categorical_crossentropy')
model.summary()

#callback to stop training when reach accuracy > 0.9
class myCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}) :
    if(logs.get('accuracy') > 0.9 and logs.get('val_accuracy') > 0.9) :
      self.model.stop_training = True
callbacks = myCallback()

num_epochs = 50
history = model.fit(padded_train, label_train, epochs=num_epochs,
                    validation_data=(padded_test, label_test), callbacks = [callbacks], verbose=2)