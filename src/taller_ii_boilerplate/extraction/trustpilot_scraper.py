import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

def scrape_trustpilot_reviews(base_url="https://www.trustpilot.com/review/www.airbnb.com"):
    todas_reseñas = []
    pagina_actual = 1
    reviews_vistos = set()

    while True:
        url = f"{base_url}?page={pagina_actual}"
        nuevos_reviews_agregados = 0  

        print(f"Scraping URL: {url}") 

        try:
            
            response = requests.get(url, timeout=15)

            response.raise_for_status() 

            soup = BeautifulSoup(response.content, 'html.parser')

            
            tarjetas_reseña = soup.find_all('div', attrs={'data-testid': 'service-review-card-v2'})
            
            print(f"Found {len(tarjetas_reseña)} review cards on this page.") 
            
            if not tarjetas_reseña:
                print("No review cards found. Breaking loop.") 
                break

            for tarjeta in tarjetas_reseña:
                
                rating_img = tarjeta.find('img', class_='CDS_StarRating_starRating__614d2e')
                calificacion = None
                if rating_img and rating_img.get('alt'):
                    try:
                        texto_calificacion = rating_img['alt']
                        
                        calificacion = int(texto_calificacion.split(' ')[1])
                    except (ValueError, IndexError, KeyError):
                        print(f"Warning: Could not parse rating from alt text: {rating_img.get('alt')}") 
                        calificacion = None

                
                titulo_tag = tarjeta.find('h2', attrs={'data-service-review-title-typography': 'true'})
                titulo = titulo_tag.get_text(strip=True) if titulo_tag else 'Sin título'

                
                comentario_tag = tarjeta.find('p', attrs={'data-service-review-text-typography': 'true'})
                comentario = comentario_tag.get_text(strip=True) if comentario_tag else 'Sin comentario'

                
                
                if comentario in reviews_vistos:
                    print(f"Skipping duplicate review: {comentario[:50]}...") 
                    continue
                
                reviews_vistos.add(comentario)
                todas_reseñas.append({
                    "Título": titulo,
                    "Comentario": comentario,
                    "Puntaje": calificacion
                })
                with open("reviws.csv", "a", encoding="utf-8") as f:
                    f.write(f"{titulo},{comentario},{calificacion}\n")

                nuevos_reviews_agregados += 1

            
            pagina_actual += 1
            time.sleep(2)  
            
            
            if pagina_actual > 50:
                print("Reached maximum page limit (50). Breaking loop.") 
                break

        except requests.exceptions.RequestException as e:
            print(f"RequestException occurred: {e}") 
            
            if response.status_code == 404:
                print("404 Not Found. Breaking loop.") 
                break
            
            break
        except Exception as e:
            
            print(f"An unexpected error occurred: {e}") 
            break

    
    df = pd.DataFrame(todas_reseñas)
    return df

if __name__ == "__main__":

    try:
    
        os.makedirs("data/raw", exist_ok=True)
        
        df = scrape_trustpilot_reviews()
        
        if not df.empty:
            df.to_csv("comentarios.csv", index=False, encoding="utf-8-sig")
            print("Archivo guardado como comentarios.csv")
        else:
            print("Sin reseñas encontradas")
    except Exception as e:
        print(f"Error: {e}")
