# -*- coding: utf-8 -*-
# wp-analizer.py

import sys
import os
import traceback
import sqlite3 # Standart kütüphane

# --- Gerekli Kütüphaneleri Kontrol Et ---
try:
    import pandas as pd
except ImportError:
    print("Hata: 'pandas' kütüphanesi bulunamadı.")
    print("Lütfen kurun: pip install pandas")
    sys.exit(1)
try:
    from PIL import Image
except ImportError:
     print("Hata: 'Pillow' kütüphanesi bulunamadı (PIL yerine kullanılır).")
     print("Lütfen kurun: pip install Pillow")
     sys.exit(1)
try:
     # Matplotlib grafik çizimi için
     import matplotlib.pyplot as plt
     # Kullanıcı arayüzü olmayan sistemlerde hata vermemesi için backend ayarı
     import matplotlib
     matplotlib.use('Agg') # 'Agg' backend'i grafik çizimini dosyaya yapar, GUI gerektirmez
except ImportError:
     print("Hata: 'matplotlib' kütüphanesi bulunamadı.")
     print("Lütfen kurun: pip install matplotlib")
     sys.exit(1)

# Renkler (opsiyonel)
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    R = Fore.RED; Y = Fore.YELLOW; G = Fore.GREEN; C = Fore.CYAN; RESET = Style.RESET_ALL
except ImportError:
    R = Y = G = C = RESET = ""

# --- Uyarılar ---
print(f"""{Y}
=================== UYARI ===================
- Bu araç, şifrelenmemiş WhatsApp mesaj veritabanını ('msgstore.db')
  analiz etmek için tasarlanmıştır.
- 'msgstore.db' dosyasına erişim genellikle ROOT YETKİSİ gerektirir
  ve/veya telefonunuzdan manuel olarak kopyalamanız gerekir.
- Veritabanı şifreliyse (crypt12, crypt14 vb.), bu betik doğrudan
  çalışmaz. Önce şifresinin çözülmesi gerekir (bu işlem ayrı araçlar
  ve anahtar dosyası gerektirir).
- Bu betik 'pandas', 'Pillow' ve 'matplotlib' kütüphanelerini
  gerektirir. Eksikse 'pip install pandas Pillow matplotlib' ile kurun.
- Gizliliğe dikkat edin! Başkalarının mesajlarını izinsiz analiz
  etmek yasal ve etik değildir.
===========================================
{RESET}""")

DEFAULT_DB_PATH = "msgstore.db"

class WhatsAppAnalyzer:
    def __init__(self, db_path=DEFAULT_DB_PATH):
        self.db_path = db_path
        self.conn = None
        self.cursor = None

        if not os.path.exists(self.db_path):
            print(f"{R}Hata: Veritabanı dosyası bulunamadı: '{self.db_path}'{RESET}")
            print(f"{Y}Lütfen 'msgstore.db' dosyasının bu betikle aynı dizinde olduğundan emin olun veya doğru yolu belirtin.{RESET}")
            # sys.exit(1) # Hata durumunda çıkmak yerine None döndürebiliriz
            raise FileNotFoundError(f"Veritabanı dosyası bulunamadı: {self.db_path}")

        print(f"{C}'{self.db_path}' veritabanına bağlanılıyor...{RESET}")
        try:
            # Veritabanı bağlantısı
            # Check_same_thread=False multithreading için gerekebilir ama burada gereksiz gibi.
            self.conn = sqlite3.connect(self.db_path) # URI=True kullanmak daha modern olabilir
            self.cursor = self.conn.cursor()
            print(f"{G}Veritabanı bağlantısı başarılı.{RESET}")
            # Temel tablo kontrolü
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='messages';")
            if not self.cursor.fetchone():
                 print(f"{R}Hata: Veritabanında 'messages' tablosu bulunamadı! Dosya bozuk veya şifreli olabilir.{RESET}")
                 self.conn.close()
                 raise ValueError("Messages tablosu bulunamadı.")

        except sqlite3.Error as e:
            print(f"{R}SQLite Hatası: Veritabanına bağlanılamadı veya okunamadı!{RESET}")
            print(f"{R}Detay: {e}{RESET}")
            print(f"{Y}Dosyanın şifreli olmadığından veya bozuk olmadığından emin olun.{RESET}")
            if self.conn: self.conn.close()
            raise # Hatayı tekrar fırlat ki program devam etmesin
        except Exception as e:
             print(f"{R}Veritabanı bağlantısında beklenmedik hata: {e}{RESET}")
             if self.conn: self.conn.close()
             raise

    def close_connection(self):
        """Veritabanı bağlantısını kapatır."""
        if self.conn:
            self.conn.close()
            print(f"{Y}Veritabanı bağlantısı kapatıldı.{RESET}")

    def analyze_messages(self):
        """Mesajları okur ve Pandas DataFrame'e yükler."""
        if not self.conn: return None
        print(f"{C}Mesajlar okunuyor ve analiz ediliyor...{RESET}")
        try:
            # SQL sorgusu (sütun isimleri WhatsApp sürümüne göre değişebilir)
            # 'key_remote_jid' genellikle gönderen/alan kişiyi belirtir.
            # 'timestamp' ms cinsinden olabilir, 1000'e bölerek saniyeye çeviriyoruz.
            # 'data' mesaj içeriği (text), 'media_wa_type' medya tipini gösterebilir.
            query = """
                SELECT
                    timestamp / 1000 as unix_time, -- Saniyeye çevir
                    datetime(timestamp / 1000, 'unixepoch', 'localtime') as datetime_str, -- Okunabilir tarih
                    key_remote_jid as contact,
                    CASE from_me WHEN 0 THEN 'Alınan' ELSE 'Gönderilen' END as direction, -- Mesaj yönü
                    data as message_text, -- Text mesajlar için
                    media_wa_type as media_type, -- Medya tipi (0: text, 1: image, 2: audio, 3: video, etc.)
                    media_size as media_size_bytes -- Medya boyutu
                FROM messages
                ORDER BY timestamp ASC
            """
            # Sorguyu Pandas ile çalıştır
            df = pd.read_sql_query(query, self.conn)

            # Zaman damgasını datetime nesnesine çevir
            df['datetime'] = pd.to_datetime(df['unix_time'], unit='s')

            print(f"{G}Toplam {len(df)} mesaj başarıyla okundu.{RESET}")
            return df

        except pd.io.sql.DatabaseError as e:
             print(f"{R}Pandas SQL Hatası: Sorgu çalıştırılamadı veya tablo/sütun bulunamadı.{RESET}")
             print(f"{R}Detay: {e}{RESET}")
             print(f"{Y}Veritabanı yapısı beklenenden farklı olabilir.{RESET}")
             return None
        except Exception as e:
            print(f"{R}Mesaj analizi sırasında beklenmedik hata: {e}{RESET}")
            traceback.print_exc()
            return None

    def visualize_activity_by_hour(self, df: pd.DataFrame, output_file="activity_by_hour.png"):
        """Mesaj aktivitesini saate göre görselleştirir."""
        if df is None or df.empty:
             print(f"{Y}Görselleştirilecek mesaj verisi yok.{RESET}")
             return
        if 'matplotlib' not in sys.modules:
             print(f"{R}Hata: 'matplotlib' yüklenemediği için görselleştirme yapılamıyor.{RESET}")
             return

        print(f"{C}Saatlik aktivite grafiği oluşturuluyor -> {output_file}{RESET}")
        try:
            # Saate göre grupla ve mesaj sayısını al
            hourly_activity = df.groupby(df['datetime'].dt.hour).size() # size() veya count()['unix_time']

            plt.figure(figsize=(12, 6)) # Grafik boyutu
            hourly_activity.plot(kind='bar', color='skyblue')
            plt.title('Saatlere Göre Mesaj Aktivitesi')
            plt.xlabel('Saat (0-23)')
            plt.ylabel('Mesaj Sayısı')
            plt.xticks(rotation=0) # X ekseni yazılarını düz yap
            plt.grid(axis='y', linestyle='--') # Arka plan çizgileri
            plt.tight_layout() # Kenar boşluklarını ayarla

            # Dosyaya kaydet
            plt.savefig(output_file)
            plt.close() # Grafiği kapat (bellekte kalmasın)
            print(f"{G}📊 Aktivite grafiği başarıyla kaydedildi: {output_file}{RESET}")

        except Exception as e:
            print(f"{R}Grafik oluşturulurken hata oluştu: {e}{RESET}")
            traceback.print_exc()

    # Medya analizi (PIL gerektirir)
    def extract_media_metadata(self, limit=10):
        """Veritabanındaki medya bilgilerini okur (limitli)."""
        if not self.conn: return
        if 'PIL' not in sys.modules:
             print(f"{R}Hata: 'Pillow' kütüphanesi yüklenemediği için medya analizi yapılamıyor.{RESET}")
             return

        print(f"\n{C}Medya metadatası okunuyor (ilk {limit} kayıt)...{RESET}")
        try:
            # message_media tablosu ve sütunları kontrol edilmeli
            # Sütunlar: message_row_id, chat_row_id, file_path, file_size, mime_type, media_key, width, height...
            # raw_data genellikle thumbnail içerir, tam dosya file_path'te olabilir.
            query = f"SELECT message_row_id, file_path, mime_type, file_size, width, height FROM message_thumbnails LIMIT {limit}" # Thumbnails daha güvenli
            # query = f"SELECT _id, file_path, mime_type, size, width, height FROM media_data LIMIT {limit}" # media_data tablosu varsa
            media_df = pd.read_sql_query(query, self.conn)

            if media_df.empty:
                 print(f"{Y}Veritabanında medya bilgisi bulunamadı (veya tablo adı yanlış).{RESET}")
                 return

            print(f"{G}Bulunan Medya Kayıtları:{RESET}")
            for index, row in media_df.iterrows():
                 # Bilgileri yazdır
                 print(f" - ID: {row['message_row_id']}, Tip: {row['mime_type']}, Boyut: {row.get('file_size', 'N/A')}, "
                       f"Çözünürlük: {row.get('width','?')}x{row.get('height','?')}, Path: {row.get('file_path', 'N/A')}")

                 # raw_data varsa ve Pillow kuruluysa resmi açmayı deneyebiliriz ama riskli.
                 # try:
                 #     if row['raw_data']:
                 #         img = Image.open(BytesIO(row['raw_data']))
                 #         print(f"    Thumbnail Boyutu: {img.size}")
                 # except Exception as img_err:
                 #     print(f"    Thumbnail okuma hatası: {img_err}")

        except pd.io.sql.DatabaseError as e:
             print(f"{R}Medya bilgisi okunurken SQL Hatası: {e}{RESET}")
             print(f"{Y}'message_thumbnails' veya 'media_data' tablosu/sütunları bulunamadı veya farklı.{RESET}")
        except Exception as e:
             print(f"{R}Medya analizi sırasında beklenmedik hata: {e}{RESET}")
             traceback.print_exc()


# Ana Çalıştırma Bloğu
if __name__ == "__main__":
    db_file = input(f"Analiz edilecek WhatsApp veritabanı dosyasının yolu [Varsayılan: {DEFAULT_DB_PATH}]: ").strip() or DEFAULT_DB_PATH

    analyzer = None
    try:
        analyzer = WhatsAppAnalyzer(db_path=db_file)
        df_messages = analyzer.analyze_messages()

        if df_messages is not None and not df_messages.empty:
             print("\n--- Analiz Seçenekleri ---")
             print("1: Saatlik Aktivite Grafiği Oluştur")
             print("2: Medya Metadatasını Göster (Limitli)")
             print("0: Çıkış")
             choice = input("Yapmak istediğiniz işlem: ").strip()

             if choice == '1':
                  analyzer.visualize_activity_by_hour(df_messages)
             elif choice == '2':
                  analyzer.extract_media_metadata(limit=20) # İlk 20 medyayı göster
             else:
                  print("Çıkılıyor.")

    except FileNotFoundError:
         print(f"{R}Program sonlandırıldı (Veritabanı dosyası bulunamadı).{RESET}")
    except ValueError as e: # Mesages tablosu bulunamadı vb.
         print(f"{R}Program sonlandırıldı (Veritabanı Hatası: {e}).{RESET}")
    except Exception as e:
         print(f"{R}Ana programda beklenmedik hata: {e}{RESET}")
         traceback.print_exc()
    finally:
         # Bağlantıyı kapat
         if analyzer:
              analyzer.close_connection()