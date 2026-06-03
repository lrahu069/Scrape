import os
import sys
import random
from playwright.sync_api import sync_playwright
from supabase import create_client, Client

url: str = os.environ.get("URL")
key: str = os.environ.get("API_KEY")

supabase: Client = create_client(url,key)


def safe_goto(page, url, timeout=80000):
  try:
    page.goto(url, timeout=timeout)
    return True
  except Exception as e:
    sys.stderr.write(f"\n❌ failed to load {url}: {e}\n")
    return False

def safe_get(currentpage, selector, attr=None):
  el = currentpage.query_selector(selector)
  if not el:
    return None
  if not attr:
    return el.inner_text()
  else:
    return el.get_attribute(attr)
  
def get_resolution(quality):
  start = quality.split(" ")[-1].strip("()")
  if start[0].isalpha():
    return quality.split(" ")[-2].strip("()")
  else:
    return start

  
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
  
  try:
    page.goto(base_url + movies_2026, timeout=80000)  # 80s
  except Exception as e:
    sys.stderr.write(f"\n❌ timeout/load error for '{base_url + movies_2026}': {e}\n")
    browser.close()
    sys.exit(1)

  # Add delay between actions to mimic humans
  page.wait_for_timeout(random.randint(2000, 4000))  # ms

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
      sys.stderr.write('''\n can't access page1 content, broken address or url might have changed!
        check : https://kuttymovies.mobile/kuttymovies/tamil_2026_movies.html''')
      continue
    if not safe_goto(page, base_url + movie['nexthop2']):
      continue
    page.wait_for_timeout(random.randint(2000, 4000))  # ms
    nexthop3 = safe_get(page, ".menu a", "href")


  
    #pg 3
    if not nexthop3:
      sys.stderr.write(f"\n can't access page2 content, check : {movie['nexthop2']}")
      continue
    if not safe_goto(page, base_url + nexthop3):
      continue
    page.wait_for_timeout(random.randint(2000, 4000)) #ms
    quality = safe_get(page, ".menu a")
    resolution = get_resolution(quality) if quality else None
    nexthop4 = safe_get(page, ".menu a", "href")

      

    #pg 4
    if not nexthop4:
      sys.stderr.write(f"\n can't access page3 content, check : {nexthop3}")
      continue
    if not safe_goto(page, base_url + nexthop4):
      continue
    page.wait_for_timeout(random.randint(2000, 4000)) #ms
    nexthop5 = safe_get(page, ".menu a", "href")
  
      

    #pg 5
    if not nexthop5:
      sys.stderr.write(f"\n can't access page4 content, check : {nexthop4}")
      continue
    if not safe_goto(page, base_url + nexthop5):
      continue
    page.wait_for_timeout(random.randint(2000, 4000)) #ms
    nexthop6 = safe_get(page, "center a", "href")
  
      

    #pg 6
    if not nexthop6:
      sys.stderr.write(f"\n can't access page5 content, check : {nexthop5}")
      continue
    if not safe_goto(page, nexthop6):
      continue
    page.wait_for_timeout(random.randint(2000, 4000)) #ms
    nexthop7 = safe_get(page, "center a", "href")
  
      

    #pg 7
    if not nexthop7:
      sys.stderr.write(f"\n can't access page6 content, check : {nexthop6}")
      continue
    if not safe_goto(page, nexthop7):
      continue
    page.wait_for_timeout(random.randint(2000, 4000)) #ms
    nexthop8 = safe_get(page, "center a", "href")
  
      

    #pg 8 
    if not nexthop8:
      sys.stderr.write(f"\n can't access page7 content, check : {nexthop7}")
      continue
    if not safe_goto(page, nexthop8):
      continue
    page.wait_for_timeout(random.randint(2000, 4000)) #ms
    link = safe_get(page, "iframe", "src")
    if not link:
      sys.stderr.write(f"\n can't access page8 content, check : {nexthop8}")
      continue


    data = {
      'id': index + 1,
      'title': movie['title'],
      'poster': None,
      'resolution': resolution,
      'link': link,
    }

    try:
      supabase.table("latest_movies").upsert(data).execute()
      print(f"Success! id:{index+1}, Movie Title:{movie['title']}")
    except Exception as e:
      sys.stderr.write(f"DB Error:, Movie Title:{movie['title']}, {e}")
  #loop ends here

  #closes browser
  browser.close()