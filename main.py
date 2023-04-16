import pickle
import streamlit as st
import pandas as pd
from streamlit_tags import st_tags
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import requests

import imdb
import re
import string

from PIL import Image

#Section- Background
import base64

st.set_page_config(layout="wide")

def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
        background-size: cover
    }}
    </style>
    """,
    unsafe_allow_html=True
    )
add_bg_from_local('5.jpg')    


#Function- Clean Data for reviews
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

#Function- Clean Data for reviews without case
def Data_Clean_without_case(review):
    
    review= re.sub('\[.*?\]', '', review) #removes characters inside []form each reviews
    review = re.sub("\\W"," ",review) #removes /,\ slashes 
    review = re.sub('https?://\S+|www\.\S+', '', review) #remove the links and macthes the white spaces

    review = re.sub('[%s]' % re.escape(string.punctuation), '', review) #remove punctuations from the review
    review= re.sub('\n', '', review) #matches the white spaces and reformat the text
    review = re.sub('\w*\d\w*', '', review) #remove numbers and digits from the reviews   
    return review

def make_genresList(x):
    gen = []
    st = " "
    for i in x:
        if i.get('name') == 'Science Fiction':
            scifi = 'Sci-Fi'
            gen.append(scifi)
        else:
            gen.append(i.get('name'))
    if gen == []:
        return np.NaN
    else:
        return (st.join(gen))

#Function- Recommend
def recommend(selected_movie,cosine_sim,movies):
    #Section- Present
   
    #df[df['date'].astype(str).str.contains('07311954')]
    #movies['movie_title'].contains(selected_movie)
    #print(type(movies['movie_title']))
    if(selected_movie in movies.movie_title.values):
        index_of_the_movie = movies[movies.movie_title == selected_movie]['index'].values[0]
        
        similarity_score = list(enumerate(cosine_sim[index_of_the_movie]))
        sorted_similar_movies = sorted(similarity_score, key = lambda x:x[1], reverse = True) 
        
        #Section-Movie Info
        response = requests.get("https://api.themoviedb.org/3/search/movie?api_key={}&query={}".format(api_key,selected_movie))
        data = response.json()
        if(len(data["results"])!=0):
            id=data["results"][0]["id"]
            
            
            url = "https://api.themoviedb.org/3/movie/{}?api_key={}&language=en-US".format(id,api_key)
            data = requests.get(url)
            data = data.json()
            poster_path = data['poster_path']
            genres_list=make_genresList(data['genres'])
            
            overview=data['overview']
            

            actors,director=[],[]

            cresponse = requests.get("https://api.themoviedb.org/3/movie/{}/credits?api_key={}".format(id,api_key))
            cdata=cresponse.json()
            
            x='cast'
            if(x in cdata.keys()):
                li=cdata["cast"]
                for i in li:
                    if i["known_for_department"]=="Acting" and len(actors)<5:
                            actors.append(i["name"])
            
            x='crew'
            if(x in cdata.keys()):
                c=cdata["crew"]
                for i in c:
                    if i["job"]=="Director" and len(director)<4:
                            director.append(i["name"])


            col1,col2=st.columns((1,2),gap='large')
            if poster_path is not None:
                with col1:
                    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
                    st.image(full_path)
                with col2:
                    st.header(selected_movie.title())
                    if(len(actors)!=0):
                        st.subheader('Actors:')
                        cast=", ".join(actors)
                        st.write(cast)
                    if(len(director)!=0):
                        st.subheader('Director:')
                        dir=", ".join(director)
                        st.write(dir)
                    if(genres_list!=np.NaN):
                        st.subheader('Genre:')
                        g=genres_list.split(' ')
                        gs=", ".join(g)
                        st.write(gs)
                    if(overview!=''):
                        st.subheader('Overview:')
                        st.write(overview)
            else:
                
                st.header(selected_movie.title())
                if(len(actors)!=0):
                    st.subheader('Actors:')
                    cast=", ".join(actors)
                    st.write(cast)
                if(len(director)!=0):
                    st.subheader('Director:')
                    dir=", ".join(director)
                    st.write(dir)
                if(genres_list!=np.NaN):
                    st.subheader('Genre:')
                    g=genres_list.split(' ')
                    gs=", ".join(g)
                    st.write(gs)
                if(overview!=''):
                    st.subheader('Overview:')
                    st.write(overview)
                st.write('')
                st.write('')
            
                            
                        
                            
                            
                        


        #Section-Reommended Movies
        i=1
        for j in range(2):
            if(j==0):
                st.subheader('Recommended Movies')
            else:
                st.write(' ')
                st.write(' ')
            col1, col2, col3,col4,col5 = st.columns(5)
            

            with col1:
                movie=sorted_similar_movies[i]
                index=movie[0]            
                title_from_index = movies[movies.index==index]['movie_title'].values[0]
                
                #FInd ID

                response = requests.get("https://api.themoviedb.org/3/search/movie?api_key={}&query={}".format(api_key,title_from_index))
                data = response.json()
                if(len(data["results"])!=0):
                    id=data["results"][0]["id"]
                    
                
                url = "https://api.themoviedb.org/3/movie/{}?api_key={}&language=en-US".format(id,api_key)
                data = requests.get(url)
                data = data.json()
                poster_path = data['poster_path']
                if (poster_path is not None):
                    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
                    st.write(title_from_index.title())
                    st.image(full_path)
                else:
                    st.write(title_from_index.title())


            with col2:
                i=i+1
                movie=sorted_similar_movies[i]
                index=movie[0]
                title_from_index = movies[movies.index==index]['movie_title'].values[0]
                response = requests.get("https://api.themoviedb.org/3/search/movie?api_key={}&query={}".format(api_key,title_from_index))
                data = response.json()
                if(len(data["results"])!=0):
                    id=data["results"][0]["id"]
                    
                
                url = "https://api.themoviedb.org/3/movie/{}?api_key={}&language=en-US".format(id,api_key)
                data = requests.get(url)
                data = data.json()
                poster_path = data['poster_path']
                if (poster_path is not None):
                    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
                    st.write(title_from_index.title())
                    st.image(full_path)
                else:
                    st.write(title_from_index.title())

            with col3:
                i=i+1
                movie=sorted_similar_movies[i]
                index=movie[0]
                title_from_index = movies[movies.index==index]['movie_title'].values[0]
                
                response = requests.get("https://api.themoviedb.org/3/search/movie?api_key={}&query={}".format(api_key,title_from_index))
                data = response.json()
                if(len(data["results"])!=0):
                    id=data["results"][0]["id"]
                    
                
                url = "https://api.themoviedb.org/3/movie/{}?api_key={}&language=en-US".format(id,api_key)
                data = requests.get(url)
                data = data.json()
                poster_path = data['poster_path']
                if (poster_path is not None):
                    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
                    st.write(title_from_index.title())
                    st.image(full_path)
                else:
                    st.write(title_from_index.title())


            with col4:
                i=i+1
                movie=sorted_similar_movies[i]
                index=movie[0]
                title_from_index = movies[movies.index==index]['movie_title'].values[0]
                
                response = requests.get("https://api.themoviedb.org/3/search/movie?api_key={}&query={}".format(api_key,title_from_index))
                data = response.json()
                if(len(data["results"])!=0):
                    id=data["results"][0]["id"]
                    
                
                url = "https://api.themoviedb.org/3/movie/{}?api_key={}&language=en-US".format(id,api_key)
                data = requests.get(url)
                data = data.json()
                poster_path = data['poster_path']
                if (poster_path is not None):
                    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
                    st.write(title_from_index.title())
                    st.image(full_path)
                else:
                    st.write(title_from_index.title())
                
      

            with col5:
                i=i+1
                movie=sorted_similar_movies[i]
                index=movie[0]
                title_from_index = movies[movies.index==index]['movie_title'].values[0]
                
                response = requests.get("https://api.themoviedb.org/3/search/movie?api_key={}&query={}".format(api_key,title_from_index))
                data = response.json()
                if(len(data["results"])!=0):
                    id=data["results"][0]["id"]
                    
                
                url = "https://api.themoviedb.org/3/movie/{}?api_key={}&language=en-US".format(id,api_key)
                data = requests.get(url)
                data = data.json()
                poster_path = data['poster_path']
                if (poster_path is not None):
                    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
                    st.write(title_from_index.title())
                    st.image(full_path)
                else:
                    st.write(title_from_index.title())
                i=i+1

    else:
        #Section-Not  Present
        
        id=0
        genres,actors,xactors,director,xdirector=[],[],[],[],[]
        
        response = requests.get("https://api.themoviedb.org/3/search/movie?api_key={}&query={}".format(api_key,selected_movie))
        data = response.json()
        if(len(data["results"])!=0):
            id=data["results"][0]["id"]
            response = requests.get(
                "https://api.themoviedb.org/3/movie/{}?api_key={}".format(id,api_key)
            )
          
            data = response.json()
            
            li=data["genres"]
            if(len(li)!=0):
                for i in li:
                    if(len(genres)>=3):
                        break
                    else:
                        genres.append(i["name"])
        
            overview=data['overview']
            cresponse = requests.get("https://api.themoviedb.org/3/movie/{}/credits?api_key={}".format(id,api_key))
            cdata=cresponse.json()
            
            x='cast'
            if(x in cdata.keys()):
                li=cdata["cast"]
                for i in li:
                    if i["known_for_department"]=="Acting" and len(xactors)<5:
                        xactors.append(i["name"])
                    if i["known_for_department"]=="Acting" and len(actors)<3:
                        actors.append(i["name"])
            
            x='crew'
            if(x in cdata.keys()):
                c=cdata["crew"]
                for i in c:
                    if i["job"]=="Director" and len(xdirector)<4:
                        xdirector.append(i["name"])
                    if i["job"]=="Director" and len(director)<1:
                        director.append(i["name"])
        
        
        #Section-Movie Info(NP)

            url = "https://api.themoviedb.org/3/movie/{}?api_key={}&language=en-US".format(id,api_key)
            data = requests.get(url)
            data = data.json()
            poster_path = data['poster_path']
            
            col1,col2=st.columns((1,2),gap='large')
            
            if poster_path is not None:
               
                with col1:
                    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
                    st.image(full_path)
                with col2:
                    st.header(selected_movie.title())
                    if(len(xactors)!=0):
                        st.subheader('Actors:')
                        cast=", ".join(xactors)
                        st.write(cast)
                    if(len(xdirector)!=0):
                        st.subheader('Director:')
                        dir=", ".join(xdirector)
                        st.write(dir)
                    if(genres==np.NaN):
                        st.subheader('Genre:')
                        gs=", ".join(genres)
                        st.write(gs)
                    if(overview!=''):
                        st.subheader('Overview:')
                        st.write(overview)

            else:
                
                st.header(selected_movie.title())
                if(len(xactors)!=0):
                    st.subheader('Actors:')
                    cast=", ".join(xactors)
                    st.write(cast)
                if(len(xdirector)!=0):
                    st.subheader('Director:')
                    dir=", ".join(xdirector)
                    st.write(dir)
                if(genres==np.NaN):
                    st.subheader('Genre:')
                    gs=", ".join(genres)
                    st.write(gs)


            comb=''
            lang=''
            x='original_language'
            if(x in data.keys()):
                lang=data['original_language']
                
                if(lang=='mr'):
                    lang='marathi'
                elif(lang=='hi'):
                    lang='hindi'
                else:
                    lang='english'

            comb=comb+lang+' '
            for i in director:
                comb=comb+i+' '
            for i in actors:
                comb=comb+i+' '
            for i in genres:
                comb=comb+i
                comb=comb+' '    
            
            print(comb)
            movies.loc[len(movies)] = [7973, selected_movie, comb]     
            
            combined_features = movies['comb']

            vectorizer = TfidfVectorizer()

            feature_vectors = vectorizer.fit_transform(combined_features)

            similarity = cosine_similarity(feature_vectors)

            index_of_the_movie = 7973

            similarity_score = list(enumerate(similarity[index_of_the_movie]))

            sorted_similar_movies = sorted(similarity_score, key = lambda x:x[1], reverse = True) 
            
            i=1
            for j in range(2):
                if(j==0):
                    st.subheader('Recommended Movies')
                else:
                    st.write(' ')
                    st.write(' ')
                col1, col2, col3,col4,col5 = st.columns(5)
                

                with col1:
                    movie=sorted_similar_movies[i]
                    index=movie[0]            
                    title_from_index = movies[movies.index==index]['movie_title'].values[0]
                    
                    #FInd ID

                    response = requests.get("https://api.themoviedb.org/3/search/movie?api_key={}&query={}".format(api_key,title_from_index))
                    data = response.json()
                    if(len(data["results"])!=0):
                        id=data["results"][0]["id"]
                        
                    
                    url = "https://api.themoviedb.org/3/movie/{}?api_key={}&language=en-US".format(id,api_key)
                    data = requests.get(url)
                    data = data.json()
                    poster_path = data['poster_path']
                    if (poster_path is not None):
                        full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
                        st.write(title_from_index.title())
                        st.image(full_path)
                    else:
                        st.write(title_from_index.title())


                with col2:
                    i=i+1
                    movie=sorted_similar_movies[i]
                    index=movie[0]
                    title_from_index = movies[movies.index==index]['movie_title'].values[0]
                    response = requests.get("https://api.themoviedb.org/3/search/movie?api_key={}&query={}".format(api_key,title_from_index))
                    data = response.json()
                    if(len(data["results"])!=0):
                        id=data["results"][0]["id"]
                        
                    
                    url = "https://api.themoviedb.org/3/movie/{}?api_key={}&language=en-US".format(id,api_key)
                    data = requests.get(url)
                    data = data.json()
                    poster_path = data['poster_path']
                    if (poster_path is not None):
                        full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
                        st.write(title_from_index.title())
                        st.image(full_path)
                    else:
                        st.write(title_from_index.title())
                    

                with col3:
                    i=i+1
                    movie=sorted_similar_movies[i]
                    index=movie[0]
                    title_from_index = movies[movies.index==index]['movie_title'].values[0]
                    
                    response = requests.get("https://api.themoviedb.org/3/search/movie?api_key={}&query={}".format(api_key,title_from_index))
                    data = response.json()
                    if(len(data["results"])!=0):
                        id=data["results"][0]["id"]
                        
                    
                    url = "https://api.themoviedb.org/3/movie/{}?api_key={}&language=en-US".format(id,api_key)
                    data = requests.get(url)
                    data = data.json()
                    poster_path = data['poster_path']
                    if (poster_path is not None):
                        full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
                        st.write(title_from_index.title())
                        st.image(full_path)
                    else:
                        st.write(title_from_index.title())


                with col4:
                    i=i+1
                    movie=sorted_similar_movies[i]
                    index=movie[0]
                    title_from_index = movies[movies.index==index]['movie_title'].values[0]
                    
                    response = requests.get("https://api.themoviedb.org/3/search/movie?api_key={}&query={}".format(api_key,title_from_index))
                    data = response.json()
                    if(len(data["results"])!=0):
                        id=data["results"][0]["id"]
                        
                    
                    url = "https://api.themoviedb.org/3/movie/{}?api_key={}&language=en-US".format(id,api_key)
                    data = requests.get(url)
                    data = data.json()
                    poster_path = data['poster_path']
                    if (poster_path is not None):
                        full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
                        st.write(title_from_index.title())
                        st.image(full_path)
                    else:
                        st.write(title_from_index.title())
        

                with col5:
                    i=i+1
                    movie=sorted_similar_movies[i]
                    index=movie[0]
                    title_from_index = movies[movies.index==index]['movie_title'].values[0]
                    
                    response = requests.get("https://api.themoviedb.org/3/search/movie?api_key={}&query={}".format(api_key,title_from_index))
                    data = response.json()
                    if(len(data["results"])!=0):
                        id=data["results"][0]["id"]
                        
                    
                    url = "https://api.themoviedb.org/3/movie/{}?api_key={}&language=en-US".format(id,api_key)
                    data = requests.get(url)
                    data = data.json()
                    poster_path = data['poster_path']
                    if (poster_path is not None):
                        full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
                        st.write(title_from_index.title())
                        st.image(full_path)
                    else:
                        st.write(title_from_index.title())
                    i=i+1
        else:
            st.subheader('Movie Not Found')

        return id

#Function- Sentiment Analysis
def sentiment_analysis(mid,selected_movie,tfidf_vectorizer,SVC_Classifier):
    negatives=0
    if(mid==0):
        pass
    else:
        st.write(' ')
        st.write(' ')


        ia = imdb.IMDb()
        search = ia.search_movie(selected_movie)
        id = search[0].movieID
        a = ia.get_movie_reviews(id)
   
        x='reviews'
        if(x not in a['data'].keys()):
            st.subheader('Sorry!!! No Reviews Found')
        else:
       
            st.subheader('Sentiment Anlaysis of Movie Reviews')
            li=[]
            for i in a['data']['reviews']:
                li.append(i['content'])
                #print(i['content'],end='\n\n')
            d={}
            d['review']=li
            df=pd.DataFrame(d)
            #print(df.head())
           
            df["display_review"] = df["review"].apply(Data_Clean_without_case)
            df["review"] = df["review"].apply(Data_Clean)
            cleaned=df["review"]
            vec=tfidf_vectorizer.transform(cleaned)
            df["Sentiment Type"]=SVC_Classifier.predict(vec)
            df["Sentiment"] = df["Sentiment Type"].apply(lambda x: "Positive" if x == 1 else "Negative")
           
            
             
            pos=0  
            for i in range(len(df['Sentiment'])):
                if (df['Sentiment'][i]=='Positive'):
                    pos=pos+1
            tot=len(df['Sentiment'])
            per=(pos/tot)*100
            st.write()
            pos='Total Percentage of Positive Reviews: '+str(int(per))+'%'
            st.subheader(pos)   
            st.write(' ')

            for i in range(10):
                if(i>=df.shape[0]):
                    break
                if(i==0):
                    pass
                else:
                    st.write(' ')
                    st.write(' ')
                col1, col2 = st.columns([4,1],gap="small")


                             
                with col1:
                    st.write(df['display_review'][i])
                with col2:
                    if(df['Sentiment'][i]=='Positive'):
                        st.markdown("Positive :smile:")
                    else:
                        st.write("Negative :slightly_frowning_face:")          
                st.write('')
     






     



def filter_by_pop():
    response = requests.get("https://api.themoviedb.org/3/movie/popular?api_key={}&language=en-US&page=1".format(api_key))
    
    data = response.json()

    
    i=1
    for j in range(3):
        
        st.write(' ')
        st.write(' ')
        col1,col2,col3,col4,col5=st.columns(5)

        with col1:
            field=data['results'][i]
            title=field['original_title']
            poster_path=field['poster_path']
            if (poster_path is not None):
                full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
                st.write(title.title())
                st.image(full_path)
            else:
                st.write(title.title())

                
        with col2:
            i=i+1
            field=data['results'][i]
            title=field['original_title']
            poster_path=field['poster_path']
            if (poster_path is not None):
                full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
                st.write(title.title())
                st.image(full_path)
            else:
                st.write(title.title())

        with col3:
            i=i+1
            field=data['results'][i]
            title=field['original_title']
            poster_path=field['poster_path']
            if (poster_path is not None):
                full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
                st.write(title.title())
                st.image(full_path)
            else:
                st.write(title.title())

        with col4:
            i=i+1
            field=data['results'][i]
            title=field['original_title']
            poster_path=field['poster_path']
            if (poster_path is not None):
                full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
                st.write(title.title())
                st.image(full_path)
            else:
                st.write(title.title())
        
        with col5:
            i=i+1
            field=data['results'][i]
            title=field['original_title']
            poster_path=field['poster_path']
            if (poster_path is not None):
                full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
                st.write(title.title())
                st.image(full_path)
            else:
                st.write(title.title())
            i=i+1

def filter_by_rating():
    response = requests.get("https://api.themoviedb.org/3/movie/top_rated?api_key={}&language=en-US&page=1".format(api_key))
    
    data = response.json()

    
    i=1
    for j in range(3):
    
        st.write(' ')
        st.write(' ')
        col1,col2,col3,col4,col5=st.columns(5)

        with col1:
            field=data['results'][i]
            title=field['original_title']
            poster_path=field['poster_path']
            if (poster_path is not None):
                full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
                st.write(title.title())
                st.image(full_path)
            else:
                st.write(title.title())

                
        with col2:
            i=i+1
            field=data['results'][i]
            title=field['original_title']
            poster_path=field['poster_path']
            if (poster_path is not None):
                full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
                st.write(title.title())
                st.image(full_path)
            else:
                st.write(title.title())

        with col3:
            i=i+1
            field=data['results'][i]
            title=field['original_title']
            poster_path=field['poster_path']
            if (poster_path is not None):
                full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
                st.write(title.title())
                st.image(full_path)
            else:
                st.write(title.title())

        with col4:
            i=i+1
            field=data['results'][i]
            title=field['original_title']
            poster_path=field['poster_path']
            if (poster_path is not None):
                full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
                st.write(title.title())
                st.image(full_path)
            else:
                st.write(title.title())
        
        with col5:
            i=i+1
            field=data['results'][i]
            title=field['original_title']
            poster_path=field['poster_path']
            if (poster_path is not None):
                full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
                st.write(title.title())
                st.image(full_path)
            else:
                st.write(title.title())
            i=i+1


def filter_by_upcoming():
    response = requests.get("https://api.themoviedb.org/3/movie/upcoming?api_key={}&language=en-US&page=1".format(api_key))
    
    data = response.json()

    
    i=1
    for j in range(3):
    
        st.write(' ')
        st.write(' ')
        col1,col2,col3,col4,col5=st.columns(5)

        with col1:
            field=data['results'][i]
            title=field['original_title']
            poster_path=field['poster_path']
            if (poster_path is not None):
                full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
                st.write(title.title())
                st.image(full_path)
            else:
                st.write(title.title())

                
        with col2:
            i=i+1
            field=data['results'][i]
            title=field['original_title']
            poster_path=field['poster_path']
            if (poster_path is not None):
                full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
                st.write(title.title())
                st.image(full_path)
            else:
                st.write(title.title())

        with col3:
            i=i+1
            field=data['results'][i]
            title=field['original_title']
            poster_path=field['poster_path']
            if (poster_path is not None):
                full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
                st.write(title.title())
                st.image(full_path)
            else:
                st.write(title.title())

        with col4:
            i=i+1
            field=data['results'][i]
            title=field['original_title']
            poster_path=field['poster_path']
            if (poster_path is not None):
                full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
                st.write(title.title())
                st.image(full_path)
            else:
                st.write(title.title())
        
        with col5:
            i=i+1
            field=data['results'][i]
            title=field['original_title']
            poster_path=field['poster_path']
            if (poster_path is not None):
                full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
                st.write(title.title())
                st.image(full_path)
            else:
                st.write(title.title())
            i=i+1





#Function- MAIN
api_key='13fedd8467dd3f0744e91dcfc59093af'

movies=pickle.load(open('movie_list.pkl','rb'))
cosine_sim=pickle.load(open('cosine_sim.pkl','rb'))
SVC_Classifier=pickle.load(open('svc.pkl','rb'))
tfidf_vectorizer=pickle.load(open('tfidf_vectorizer.pkl','rb'))


movie_list=[]


movie_list=movies['movie_title']
l=movie_list[:7974]

a=l.tolist()

image = Image.open('1MovieMate.png')
st.image(image,width=200)




#FILTER MOVIES

st.write('')
option = st.selectbox(
    'Search Movies by',
    ('Popularity', 'Top Rated', 'Upcoming Movies'),0)


if(option=='Popularity'):
    filter_by_pop()
elif(option=='Top Rated'):
    filter_by_rating()
elif(option=='Upcoming Movies'):
    filter_by_upcoming()

st.write(' ')
st.write(' ')    
#REcommend

keywords = st_tags(
    label="Enter Movie's Title and Press Enter",
    text='Press Enter',
 
    suggestions=a,
    maxtags = 1,
    key='1')

if(len(keywords)>0):

    selected_movie=keywords[0]
    id=recommend(selected_movie,cosine_sim,movies)
    
    sentiment_analysis(id,selected_movie,tfidf_vectorizer,SVC_Classifier)


