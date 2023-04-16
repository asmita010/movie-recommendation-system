import pickle
import streamlit as st
import numpy as np
import pandas as pd
import difflib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import re
import string
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC

# loading the data from the csv file to apandas dataframe
movies_data = pd.read_csv('../owndata/final/final_final_data_index.csv')

combined_features = movies_data['comb']

vectorizer = TfidfVectorizer()

feature_vectors = vectorizer.fit_transform(combined_features)

similarity = cosine_similarity(feature_vectors)


pickle.dump(similarity,open('cosine_sim.pkl','wb'))

final_data=movies_data[['index','movie_title','comb']]
pickle.dump(final_data,open('movie_list.pkl','wb'))


#SENTIMENT
ds = pd.read_csv('../kaggledata/imdb_reviews.csv')

def Data_Clean(review):
    review = review.lower() #converts in to lower case
    review= re.sub('\[.*?\]', '', review) #removes characters inside []form each reviews
    review = re.sub("\\W"," ",review) #removes /,\ slashes 
    review = re.sub('https?://\S+|www\.\S+', '', review) #remove the links and macthes the white spaces
    review = re.sub('<.*?>+', '', review) #removes <br> tags specially <>
    review = re.sub('[%s]' % re.escape(string.punctuation), '', review) #remove punctuations from the review
    review= re.sub('\n', '', review) #matches the white spaces and reformat the text
    review = re.sub('\w*\d\w*', '', review) #remove numbers and digits from the reviews   
    return review

ds["review"] = ds["review"].apply(Data_Clean)
ds['Value'] = ds['sentiment'].apply(lambda x: 1 if x =='positive' else 0)
x=ds["review"]
y=ds["Value"]

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3,random_state=0)

tfidf=TfidfVectorizer()
xv_train=tfidf.fit_transform(x_train)#Learn vocabulary and idf, return document-term matrix.
xv_test=tfidf.transform(x_test) #Learn vocabulary and idf from training set.

features=len(tfidf.get_feature_names())

classifier=LinearSVC()
SVC_Classifier=classifier.fit(xv_train,y_train)

pickle.dump(SVC_Classifier,open('svc.pkl','wb'))

pickle.dump(tfidf,open('tfidf_vectorizer.pkl','wb'))



'''
list_of_all_titles = movies_data['movie_title'].tolist()

movie_name=st.text_input('Enter Movie Title')
st.write(inp)


find_close_match = difflib.get_close_matches(movie_name, list_of_all_titles)

close_match = find_close_match[0]

similarity_score = list(enumerate(similarity[index_of_the_movie]))

sorted_similar_movies = sorted(similarity_score, key = lambda x:x[1], reverse = True) 

i = 1

for movie in sorted_similar_movies:
  index = movie[0]
  title_from_index = movies_data[movies_data.index==index]['movie_title'].values[0]
  if (i<30):
    st.write(i, '.',title_from_index)
    i+=1

'''