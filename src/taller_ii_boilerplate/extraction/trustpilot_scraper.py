import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

def scrape_trustpilot_reviews(base_url="https://www.trustpilot.com/review/www.airbnb.com"):
    all_reviews = []
    current_page = 1


    while True:
        url = f"{base_url}?page={current_page}"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

        
        
            review_cards = soup.find_all('article', {'class': 'styles_reviewCard__meSdm'})

            if not review_cards:
                break

            for card in review_cards:
            
            
                rating_img = card.find('div', {'class': 'styles_starRating__BhKtt'}).find('img')
                rating = None
                if rating_img and rating_img.get('alt'):
                    try:
                        rating_text = rating_img['alt']
                        rating = int(rating_text.split(' ')[1])
                    except (ValueError, IndexError, KeyError):
                        rating = None

            
            
                review_text_element = card.find('p', {'class': 'CDS_Typography_appearance-default__dd9b51 CDS_Typography_prettyStyle__dd9b51 CDS_Typography_body-l__dd9b51', 'data-relevant-review-text-typography': True})
                
                review_text = review_text_element.get_text(strip=True) if review_text_element else "No review text found"

            
            
                if "See more" in review_text:
                    review_text = review_text.replace("See more", "").strip()

            
            
            
                if len(review_text) < 50:
                    continue

                all_reviews.append({
                    'review_text': review_text,
                    'rating': rating
                })

            current_page += 1
            time.sleep(1)

        except requests.exceptions.RequestException as e:
        
            if response.status_code == 404:
                break
        
        
            break
        except Exception as e:
            break

    df = pd.DataFrame(all_reviews)
    return df

if __name__ == "__main__":


    try:
    
        os.makedirs("data/raw", exist_ok=True)
        
        reviews_df = scrape_trustpilot_reviews()
        
        if not reviews_df.empty:
            output_path = "data/raw/reviews.csv"
            reviews_df.to_csv(output_path, index=False)
        else:
    except Exception as e:
        print(f"error: {e}")
