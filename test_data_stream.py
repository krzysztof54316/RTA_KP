import requests
import json
import time

def collect_wikipedia_ml_data(target_per_class=500, output_file='wiki_raw_dataset.json'):
    """
    Pobiera całe, surowe obiekty JSON ze strumienia Wikipedii 
    i buduje zbalansowany zbiór danych (boty vs ludzie) w formacie JSON.
    """
    url = 'https://stream.wikimedia.org/v2/stream/recentchange'
    
    headers = {
        'User-Agent': 'DataEngineeringStudentProject/1.0 (Contact: jan.kowalski@student.edu.pl; Educational Purpose)'
    }
    
    humans_collected = 0
    bots_collected = 0
    collected_events = []  # Tutaj trafią całe obiekty JSON
    
    print(f"Rozpoczynam zbieranie danych. Cel: {target_per_class} ludzi i {target_per_class} botów.")
    print("Łączenie ze strumieniem Wikipedii (Server-Sent Events)...")
    
    try:
        response = requests.get(url, stream=True, headers=headers)
        response.raise_for_status()
        
        for line in response.iter_lines():
            # Warunek stopu - zebraliśmy pełny, zbalansowany dataset
            if humans_collected >= target_per_class and bots_collected >= target_per_class:
                break
                
            if not line:
                continue
                
            decoded_line = line.decode('utf-8')
            
            if decoded_line.startswith('data: '):
                try:
                    event = json.loads(decoded_line[6:])
                    
                    # Interesują nas tylko edycje artykułów
                    if event.get('type') != 'edit':
                        continue
                        
                    is_bot = event.get('bot')
                    
                    # Pilnowanie równego balansu klas
                    if is_bot is True and bots_collected >= target_per_class:
                        continue
                    if is_bot is False and humans_collected >= target_per_class:
                        continue
                        
                    # Dorzucamy CAŁY surowy obiekt JSON do naszej listy
                    collected_events.append(event)
                    
                    if is_bot is True:
                        bots_collected += 1
                    else:
                        humans_collected += 1
                        
                    print(f"[Postęp] Zebrano: Ludzie: {humans_collected}/{target_per_class} | Boty: {bots_collected}/{target_per_class}", end='\r')
                    
                except (json.JSONDecodeError, KeyError, TypeError):
                    continue

        # Po wyjściu z pętli zapisujemy całą strukturę do pliku JSON
        print(f"\n\nZapisywanie {len(collected_events)} obiektów do pliku JSON...")
        with open(output_file, mode='w', encoding='utf-8') as f:
            json.dump(collected_events, f, ensure_ascii=False, indent=4)

        print(f"Sukces! Pełne dane zostały zapisane do pliku: '{output_file}'")
        
    except requests.exceptions.HTTPError as err:
        print(f"\nBłąd HTTP podczas próby połączenia: {err}")
    except Exception as e:
        print(f"\nWystąpił nieoczekiwany błąd: {e}")

if __name__ == "__main__":
    collect_wikipedia_ml_data(target_per_class=500)