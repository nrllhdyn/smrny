# Soru 5: Önbellekleme (Caching) ve Veri Yapıları

import functools
import time
import threading

@functools.lru_cache(maxsize=3) # Önbellek boyutu 3 ile sınırlı
def test_func(param1, param2):
    print(f"Fonksiyon çalışıyor: param1={param1}, param2={param2}")
    time.sleep(2) # 2 saniye bekle
    return f"Sonuç: {param1 * 2 + param2}"

# Önbelleği test etme
print("İlk çağrı (önbellekte yok):")
sonuc1 = test_func(5, 10)
print(f"Sonuç 1: {sonuc1}\n")

print("İkinci çağrı aynı parametrelerle (önbellekten gelecek):")
sonuc2 = test_func(5, 10)
print(f"Sonuç 2: {sonuc2}\n")

print("Üçüncü çağrı farklı parametrelerle (önbellekte yok):")
sonuc3 = test_func(6, 12)
print(f"Sonuç 3: {sonuc3}\n")

print("Dördüncü çağrı farklı parametrelerle (önbellekte yok, LRU devreye girecek):")
sonuc4 = test_func(7, 14)
print(f"Sonuç 4: {sonuc4}\n")

print("Beşinci çağrı ilk parametrelerle (önbellekte yok, en eski LRU çıkarılacak):")
sonuc5 = test_func(5, 10) # (5, 10) tekrar çağrılıyor, ama önbellekte yer kalmadığı için tekrar hesaplanacak.
print(f"Sonuç 5: {sonuc5}\n")

print("Önbellek Bilgileri:")
print(f"Önbellek boyutu: {test_func.cache_info().maxsize}")
print(f"Geçerli boyut: {test_func.cache_info().currsize}")
print(f"İsabet sayısı (cache hit): {test_func.cache_info().hits}")
print(f"Kaçırma sayısı (cache miss): {test_func.cache_info().misses}")



# TTL (Time To Live) ile önbellekleme
class TTL_LRU_Cache:
    def __init__(self, maxsize=128, ttl=60):
        self.maxsize = maxsize
        self.ttl = ttl # saniye cinsinden yaşam süresi
        self.cache = {}
        self.lru_keys = [] # LRU için anahtar listesi
        self.lock = threading.Lock()

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = self._make_key(args, kwargs)
            with self.lock:
                if key in self.cache:
                    value, expiry_time = self.cache[key]
                    if expiry_time > time.time(): # TTL kontrolü
                        self._update_lru(key) # LRU listesini güncelle
                        print(f"(TTL Cache) Önbellekten getiriliyor: key={key}")
                        return value
                    else:
                        print(f"(TTL Cache) TTL süresi doldu, yeniden hesaplanıyor: key={key}")
                        del self.cache[key] # Süresi dolan girdiyi sil
                        self.lru_keys.remove(key) # LRU listesinden de sil
                else:
                    print(f"(TTL Cache) Önbellekte yok, hesaplanıyor: key={key}")

                value = func(*args, **kwargs)
                self._add_to_cache(key, value)
                return value
        return wrapper

    def _make_key(self, args, kwargs):
        key = args
        if kwargs:
            key += tuple(sorted(kwargs.items())) # kwargs'ı sıralı tuple'a dönüştür
        return key

    def _update_lru(self, key):
        if key in self.lru_keys:
            self.lru_keys.remove(key) # Mevcutsa listeden çıkar
        self.lru_keys.append(key) # En sona ekle (en son kullanılan)

    def _add_to_cache(self, key, value):
        if len(self.cache) >= self.maxsize:
            oldest_key = self.lru_keys.pop(0) # En eski anahtarı al
            del self.cache[oldest_key] # Önbellekten çıkar
        self.cache[key] = (value, time.time() + self.ttl) # Değer ve TTL ile birlikte sakla
        self._update_lru(key) # LRU listesine ekle

    def cache_info(self): # cache_info benzeri bir metot (basit)
        return {
            'maxsize': self.maxsize,
            'currsize': len(self.cache),
            'ttl': self.ttl,
            'lru_keys': self.lru_keys.copy() # Kopya döndür, thread safety için
        }


# TTL ile önbellekleme örneği
ttl_cache_instance = TTL_LRU_Cache(maxsize=2, ttl=5) # Önbellek boyutu 2, TTL 5 saniye

@ttl_cache_instance # TTL_LRU_Cache örneğini dekoratör olarak kullan
def ttl_fonksiyon(param):
    print(f"(TTL Fonksiyon) Çalışıyor: param={param}")
    time.sleep(1)
    return f"(TTL Sonuç) {param * 3}"

print("\n--- TTL Önbellek Testi ---")

print("İlk çağrı (TTL önbellekte yok):")
sonuc_ttl1 = ttl_fonksiyon(10)
print(f"Sonuc 1: {sonuc_ttl1}\n")

print("İkinci çağrı aynı parametrelerle (TTL önbellekten gelecek):")
sonuc_ttl2 = ttl_fonksiyon(10)
print(f"Sonuc 2: {sonuc_ttl2}\n")

print("Bekle 6 saniye (TTL süresi dolacak)...")
time.sleep(6)

print("Üçüncü çağrı aynı parametrelerle (TTL süresi dolduğu için yeniden hesaplanacak):")
sonuc_ttl3 = ttl_fonksiyon(10)
print(f"Sonuc 3: {sonuc_ttl3}\n")

print("Dördüncü çağrı farklı parametrelerle (TTL önbellekte yok):")
sonuc_ttl4 = ttl_fonksiyon(20)
print(f"Sonuc 4: {sonuc_ttl4}\n")

print("Beşinci çağrı ilk parametrelerle (önbellekte yer yok, LRU devreye girecek):")
sonuc_ttl5 = ttl_fonksiyon(10) # (10) tekrar çağrılıyor, ama önbellekte yer kalmadığı için tekrar hesaplanacak.
print(f"Sonuc 5: {sonuc_ttl5}\n")

print("TTL Önbellek Bilgileri:")
print(f"Önbellek boyutu: {ttl_cache_instance.cache_info()['maxsize']}")
print(f"Geçerli boyut: {ttl_cache_instance.cache_info()['currsize']}")
print(f"TTL (saniye): {ttl_cache_instance.cache_info()['ttl']}")
print(f"LRU Anahtarları (en eskiden en yeniye): {ttl_cache_instance.cache_info()['lru_keys']}")


