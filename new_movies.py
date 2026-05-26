import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client

url: str = os.environ.get("URL")
key: str = os.environ.get("API_KEY")

supabase: Client = create_client(url,key)


def extract_poster(soup2):
  image_container = soup2.find('aside', class_='v3-side')
  image = image_container.find('img')['src']

  if image:
    return image
  else:
    return None

def extract_link(soup2):

  return None


response = requests.get('https://tamilyogi.dance/genre/tamil/')
soup = BeautifulSoup(response.text, 'lxml')
movie_container = soup.find('div', class_='hamad-grid').find_all('article', class_='movie-card')

for index, movie_card in enumerate(movie_container):

  web_link2 = movie_card.find('a')['href']
  title = movie_card.find('div', class_="card-info").find('h3').text.split("Tamil")[0]

  response2 = requests.get(web_link2)
  soup2 = BeautifulSoup(response2.text, 'lxml')
  poster = extract_poster(soup2)
  link = extract_link(soup2)

  data = {
    'id': index+1,
    'title': title,
    'poster': poster,
    'link': link,
  }

  try:
    supabase.table("latest_movies").upsert(data).execute()
    print('success!')
  except Exception as e:
    print("Error: on database insersion")
  
  
 
