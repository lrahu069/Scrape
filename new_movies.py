import os
import sys
from playwright.sync_api import sync_playwright
from supabase import create_client, Client

url: str = os.environ.get("URL")
key: str = os.environ.get("API_KEY")

supabase: Client = create_client(url,key)


def safe_get(currentpage, selector, attr=None):
  el = currentpage.query_selector(selector)
  if not el:
    return None
  if not attr:
    return el.inner_text()
  else:
    return el.get_attribute(attr)
  
base_url = "https://kuttymovies.mobile"
movies_2026 = "/kuttymovies/tamil_2026_movies.html"

with sync_playwright() as p:
  browser = p.chromium.launch(headless=True)
  # Launch with stealth-like settings
  context = browser.new_context(
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    viewport={"width": 1280, "height": 720},
    locale="en-US"
  )

  page = context.new_page()
  page.goto(base_url + movies_2026)

  # Add delay between actions to mimic humans
  page.wait_for_timeout(1500)  # ms

  movies = []
  for movie in page.query_selector_all(".menu a"):
    movies.append({
      'title' : movie.inner_text(),
      'nexthop2' : movie.get_attribute("href")
    })

  #blocks the auto-download before it begins
  page.route("**/*.mp4", lambda route: route.abort())
  page.route("**/*.mkv", lambda route: route.abort())

  for index,movie in enumerate(movies):

    #pg 2
    if not movie['nexthop2']:
      sys.stderr.write('''can't access page1 content, broken address or url might have changed!
        check : https://kuttymovies.mobile/kuttymovies/tamil_2026_movies.html''')
      continue
    page.goto(base_url+movie['nexthop2'])
    page.wait_for_timeout(1800)  # ms
    nexthop3 = safe_get(page, ".menu a", "href")


  
    #pg 3
    if not nexthop3:
      sys.stderr.write(f"\n can't access page2 content, check : {movie['nexthop2']}")
      continue
    page.goto(base_url+nexthop3)
    page.wait_for_timeout(1000) #ms
    resolution = safe_get(page, ".menu a")
    nexthop4 = safe_get(page, ".menu a", "href")

      

    #pg 4
    if not nexthop4:
      sys.stderr.write(f"\n can't access page3 content, check : {nexthop3}")
      continue
    page.goto(base_url+nexthop4)
    page.wait_for_timeout(1300) #ms
    nexthop5 = safe_get(page, ".menu a", "href")
  
      

    #pg 5
    if not nexthop5:
      sys.stderr.write(f"\n can't access page4 content, check : {nexthop4}")
      continue
    page.goto(base_url+nexthop5)
    page.wait_for_timeout(1700) #ms
    nexthop6 = safe_get(page, "center a", "href")
  
      

    #pg 6
    if not nexthop6:
      sys.stderr.write(f"\n can't access page5 content, check : {nexthop5}")
      continue
    page.goto(nexthop6)
    page.wait_for_timeout(1300) #ms
    nexthop7 = safe_get(page, "center a", "href")
  
      

    #pg 7
    if not nexthop7:
      sys.stderr.write(f"\n can't access page6 content, check : {nexthop6}")
      continue
    page.goto(nexthop7)
    page.wait_for_timeout(1800) #ms
    nexthop8 = safe_get(page, "center a", "href")
  
      

    #pg 8 
    if not nexthop8:
      sys.stderr.write(f"\n can't access page7 content, check : {nexthop7}")
      continue
    page.goto(nexthop8)
    page.wait_for_timeout(1300) #ms
    link = safe_get(page, "iframe", "src")


    data = {
      'id': index + 1,
      'title': movie['title'],
      'poster': None,
      'resolution': resolution,
      'link': link,
    }

    try:
      supabase.table("latest_movies").upsert(data).execute()
      print('success!')
    except Exception as e:
      sys.stderr.write(f"Error: on database insersion, Movie Title:{movie['title']}")
  #loop ends here

  #closes browser
  browser.close()