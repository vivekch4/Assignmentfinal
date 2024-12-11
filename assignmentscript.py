import time
import feedparser
import requests
from readability import Document
from bs4 import BeautifulSoup
import openai
import os
import nltk
from nltk.tokenize import sent_tokenize


def ensure_nltk_resources():
    try:
        nltk.download('punkt')
        nltk.download('punkt_tab')
    except Exception as e:
        print(f"Error downloading NLTK resources: {e}")

ensure_nltk_resources()


INSTAGRAM_ACCESS_TOKEN = "EABfwuAuOCQ8BO7h9v7oZB1tBCJatGSbk6Qpr0ezGCZCQuE0xJFHJqEr7nXlmGDG9NZAzOCqeg6HqeeqRHIrzMLkVmXjDaxDiwzZAqMZAP8dkQYy84iLW4P9FWpFdOMoIGKZCo7pcFZCtUfXDBG6Shg6nqGDSkVRoDLc9m4v40pwNQuil8raEV2YQeQwZCGRQZAFnXmtnvg2pBJrvzNbECfbii"
INSTAGRAM_USER_ID = "17841441123508895"
openai.api_key = "sk-proj-O5HHuTqOT4BYArgqpfryoxXhyde9ypsvL8fX4ZCdsD_QMhNjJlwy1ei4MNdV_u16Tethr7aT3BlbkFJgf58rCCyEsn_h-wAlufuayaNlbTvFjN_1gdyvKfMTLUPDz2cqsf3TEPg_ijv_vhV7uesL92i0A"

def download_image(image_url, save_path):
    try:
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return save_path
        else:
            raise Exception(f"Failed to download image. HTTP Status Code: {response.status_code}")
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None

def generate_image(prompt):
    try:
        response = openai.Image.create(prompt=prompt, n=1, size="1024x1024")
        return response['data'][0]['url']
    except Exception as e:
        print(f"Error generating image: {e}")
        return None

def shorten_url(url):
    try:
        response = requests.get(f"http://tinyurl.com/api-create.php?url={url}")
        return response.text
    except Exception as e:
        print(f"Error shortening URL: {e}")
        return url

def get_latest_article(rss_url):
    feed = feedparser.parse(rss_url)
    if not feed.entries:
        raise Exception("No articles found in the RSS feed.")
    latest_entry = feed.entries[0]
    return {
        "title": latest_entry.title,
        "link": latest_entry.link,
        "summary": latest_entry.summary if 'summary' in latest_entry else None,
        "image_url": latest_entry.media_thumbnail[0]['url'] if 'media_thumbnail' in latest_entry else None,
        "published_time": latest_entry.published_parsed if 'published_parsed' in latest_entry else None
    }

def extract_article_content(url):
    try:
        response = requests.get(url)
        doc = Document(response.text)
        article_content = doc.summary()
        soup = BeautifulSoup(article_content, "html.parser")
        text_content = soup.get_text()
        

        print(f"Extracted Article Content: {text_content[:100]}...")  # Print first 100 characters
        
        return text_content
    except Exception as e:
        print(f"Error extracting article content: {e}")
        return ""

def simple_summarize(text, num_sentences=2):
    try:
        sentences = sent_tokenize(text)
        return ' '.join(sentences[:num_sentences])
    except LookupError:
        print("NLTK punkt resource not found. Attempting to download...")
        ensure_nltk_resources()  
        sentences = sent_tokenize(text) 
        return ' '.join(sentences[:num_sentences])

def generate_caption(article_text, article_url):
    try:    
        summary = simple_summarize(article_text, num_sentences=1)

        shortened_url = shorten_url(article_url)
        caption = f"{summary} Read more: {shortened_url}"

        if len(caption) > 200:
            caption = f"{summary.split('.')[0]}... Read more: {shortened_url}"
        print(f"Generated Caption: {caption}")

        return caption.strip()
    except Exception as e:
        print(f"Error generating caption: {e}")
        return f"Check out this article: {shorten_url(article_url)}"

def post_to_instagram(image_url, caption):
    try:
        image_filename = "temp_image.jpg"
        
        if not image_url:
            raise Exception("No image URL provided.")
        
        saved_image_path = download_image(image_url, image_filename)
        
        if not saved_image_path:
            raise Exception("Failed to download image for Instagram post.")

        # Upload media to Instagram
        media_upload_url = f"https://graph.facebook.com/v16.0/{INSTAGRAM_USER_ID}/media"
        
        media_data = {"image_url": image_url, "caption": caption, "access_token": INSTAGRAM_ACCESS_TOKEN}
        
        media_response = requests.post(media_upload_url, data=media_data)
        
        if media_response.status_code != 200:
            raise Exception(f"Error uploading media: {media_response.status_code} - {media_response.text}")

        media_id = media_response.json().get("id")
        
        if not media_id:
            raise Exception("No media ID returned from Instagram.")

        # Publish media to Instagram
        publish_url = f"https://graph.facebook.com/v16.0/{INSTAGRAM_USER_ID}/media_publish"
        
        publish_data = {"creation_id": media_id, "access_token": INSTAGRAM_ACCESS_TOKEN}
        
        publish_response = requests.post(publish_url, data=publish_data)
        
        if publish_response.status_code != 200:
            raise Exception(f"Error publishing media: {publish_response.status_code} - {publish_response.text}")

        print("Successfully posted to Instagram.")
    except Exception as e:
       print(f"Error during Instagram post: {e}")

def automate_instagram_post(rss_url):
    try:
       article = get_latest_article(rss_url)
       
       article_content = extract_article_content(article["link"])

       image_url = article.get("image_url")
       
       if not image_url:
           image_url = generate_image(article["title"])

       caption = generate_caption(article_content, article["link"])
       
       
       if caption and len(caption) > 0:
           post_to_instagram(image_url, caption)
           print("Instagram post completed.")
       else:
           print("No valid caption generated; skipping post.")
           
    except Exception as e:
       print(f"Error automating Instagram post: {e}")

def monitor_rss_feed_by_timestamp(rss_url, interval=300):
   last_published_time = None 
   print("Monitoring RSS feed for new articles...")

   while True:
       try:
           article = get_latest_article(rss_url)
           current_published_time = article["published_time"]

           if current_published_time:
               print(f"Last Timestamp: {last_published_time}")
               print(f"Current Timestamp: {current_published_time}")

               if not last_published_time or current_published_time > last_published_time:
                   print(f"New article detected: {article['title']}")
                   last_published_time = current_published_time  
                   automate_instagram_post(rss_url)
               else:
                   print("No new articles. Checking again...")
           else:
               print("No valid timestamp found for the latest article.")

       except Exception as e:
           print(f"Error monitoring RSS feed: {e}")

       time.sleep(interval)

if __name__ == "__main__":
   RSS_FEED_URL = "https://variety.com/feed/"
   MONITOR_INTERVAL = 300 
   monitor_rss_feed_by_timestamp(RSS_FEED_URL, MONITOR_INTERVAL)