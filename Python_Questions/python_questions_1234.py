############################################################################################################
# Soru 1: Palindrom Kontrolü ve Optimizasyonu
def is_palindrome(s):
    processed_string = ''.join(char for char in s if char.isalnum()).lower()
    return processed_string == processed_string[::-1]

test_cases = ["A mama","A man, a plan, a canal: Panama","Ey Edip, Adana’da pide ye!"]
# Fonksiyonu test etmek icin asagidaki yprum satirini kaldirin.

# for test in test_cases:
#     print(test + ":", is_palindrome(test))


############################################################################################################
# Soru 2: İkinci En Büyük Sayıyı Bulma
def second_max(n: list) -> int:
    if len(set(n)) < 2 or not n:
        raise ValueError("Input should have at least 2 different elements")
    return sorted(n)[-2]

test_cases = [
    [], 
    [1, 1, 1, 1, 1], 
    [3, 3, 3, 3, 3],
    [],
    [1,2,3,4,5,6,5,4,7,8,9,10]]

# Fonksiyonu test etmek icin asagidaki yprum satirini kaldirin.
# for test in test_cases:
#     print(test, second_max(test))

############################################################################################################
# Soru 3: Dosya İstatistikleri

import string
from collections import Counter
filepath = "test.txt"
def statsics_file(file_path):
    with open(file_path, "r") as file:
        try:
            data = file.read()

            data = data.lower()
            punctuation_marks = string.punctuation
            data = data.translate(str.maketrans('', '', punctuation_marks))

            words = data.split()
            total_words = len(words)

            freq_words = Counter(words)

            most_freq_5_words = freq_words.most_common(5)

            return print(f"Toplam kelime sayısı: {total_words}\n Kelime frekansları: {freq_words}\n En çok geçen 5 kelime: {most_freq_5_words}")
        except FileNotFoundError:
            return "Dosya bulunamadı"
        except Exception as e:
            return f"Olusan hata: {e}"

# Fonksiyonu test etmek icin asagidaki yprum satirini kaldirin.
# test = statsics_file(filepath)


############################################################################################################
############################################################################################################
# Soru 4: Asenkron İstekler ve Hata Yönetimi

import aiohttp
import asyncio
import logging
from typing import List, Tuple
# Verilen URL'den web sayfasını getirir ve içeriği döndürür.
async def fetch_url(url: str, session: aiohttp.ClientSession, semaphore: asyncio.Semaphore, timeout: int) -> Tuple[str, str or None]:
    try:
        async with semaphore:  
            async with session.get(url, timeout=timeout) as response:
                response.raise_for_status()  
                html_content = await response.text()
                return url, html_content
    except aiohttp.ClientError as e:
        error_message = f"İstemci Hatası: {type(e).__name__} - {e}"
        return url, error_message
    except asyncio.TimeoutError:
        error_message = "Zaman Aşımı Hatası"
        return url, error_message
    except Exception as e:
        error_message = f"Beklenmeyen Hata: {type(e).__name__} - {e}"
        return url, error_message
    
# Verilen URL listesinden web sayfalarını asenkron olarak getirir.
async def fetch_urls_async(urls: List[str], concurrency_limit: int = 5, request_timeout: int = 10) -> List[Tuple[str, str or None]]:
    semaphore = asyncio.Semaphore(concurrency_limit) 
    timeout = aiohttp.ClientTimeout(total=request_timeout)

    async with aiohttp.ClientSession(timeout=timeout) as session: 
        tasks = [fetch_url(url, session, semaphore, request_timeout) for url in urls]
        results = await asyncio.gather(*tasks)
        return results

if __name__ == "__main__":
    urls = [
        "https://www.google.com",
        "https://simeranya.com.tr/",
        "https://httpbin.org/delay/3",  # 3 saniye gecikmeli yanıt
        "https://httpbin.org/status/404", # 404 Hatası
        "https://nonexistent-domain.example", # Bağlantı Hatası
        "https://httpbin.org/status/500", # 500 Sunucu Hatası
        "https://www.wikipedia.org" # Büyük sayfa, zaman aşımı testi için kullanılabilir
    ]

    async def main():
        concurrency = 3 
        timeout_seconds = 5

        print(f"URL'ler asenkron olarak getiriliyor (eşzamanlılık sınırı: {concurrency}, zaman aşımı: {timeout_seconds} saniye)...")
        results = await fetch_urls_async(urls, concurrency_limit=concurrency, request_timeout=timeout_seconds)

        print("\nSonuçlar:")
        for url, content in results:
            print(f"\nURL: {url}")
            if content:
                if isinstance(content, str) and "Hata" in content: # Basit hata kontrolü
                    print(f"  Durum: HATA")
                    print(f"  Hata Mesajı: {content}")
                else:
                    print(f"  Durum: BAŞARILI")
                    print(f"  HTML İçeriği (ilk 200 karakter):\n  {content[:200]}...") # Sadece ilk 200 karakteri göster
            else:
                print("  Durum: Belirsiz (İçerik yok)")

    asyncio.run(main())

