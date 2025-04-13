# 401 Multi-Tool Suite

<pre>
██╗  ██╗ ██████╗  ██╗
██║  ██║██╔═████╗███║
███████║██║██╔██║╚██║
╚════██║████╔╝██║ ██║
     ██║╚██████╔╝ ██║
     ╚═╝ ╚═════╝  ╚═╝
</pre>

Çeşitli ağ, güvenlik ve yardımcı programlama görevleri için Python betiklerinden oluşan bir koleksiyon.

---

## ⚠️ ÖNEMLİ UYARI VE YASAL UYARI ⚠️

Bu araç koleksiyonu **yalnızca eğitim ve yasal test amaçlı** olarak tasarlanmıştır.

* **Sorumluluk:** Bu araçların kullanımından doğacak **tüm sorumluluk kullanıcıya aittir**. Araçları kullanmadan önce yerel ve uluslararası yasalara uyduğunuzdan emin olun.
* **Yasa Dışı Kullanım:** Araçların (özellikle **Call Bomb**, **SMS Bomb** ve **Crash**) izinsiz sistemlere, ağlara veya kişilere karşı kullanılması **yasa dışıdır** ve ciddi sonuçlar doğurabilir. Geliştirici, araçların kötüye kullanılmasından sorumlu tutulamaz.
* **API Güvenilmezliği:** SMS Bomb, Call Bomb ve Netflix Checker gibi araçlar, üçüncü parti API'lere dayanmaktadır. Bu API'ler sık sık **değişebilir, kısıtlanabilir veya tamamen kaldırılabilir**. Bu nedenle, bu araçların işlevselliği zamanla **bozulabilir veya tamamen durabilir**.
* **Riskler:** Bombardıman araçları IP adresinizin engellenmesine veya operatörünüzle sorun yaşamanıza neden olabilir. Crash aracı, hedef sistemlere zarar verebilir.

**Bu araçları indirerek ve kullanarak yukarıdaki şartları kabul etmiş sayılırsınız.**

---

## Tool Araçları ve Özellikleri

1.  **Call Bomb (`call_bomb.py`):**
    * Belirtilen telefon numarasına çeşitli servisler (şu anda Truecaller API'si üzerinden) aracılığıyla otomatik arama (veya OTP SMS) isteği gönderir.
    * *Not:Arada api güncellemeleri yüzünden çalışmayabilir.*

2.  **Crash (`crash.py`):**
    * Belirtilen hedef IP ve porta yüksek hacimli UDP paketleri göndererek ağ testi veya (izinli) stres testi yapar.
    * **UYARI:** İzinsiz sistemlere karşı kullanmak hizmet reddi (DoS) saldırısıdır ve yasa dışıdır kullanım kullanıcının sorumlulugundadır.

3.  **SMS Bomb (`sms_bomb.py`):**
    * Çok sayıda farklı web sitesi ve uygulamanın API'sini kullanarak belirtilen telefon numarasına yoğun OTP/mesaj gönderimi yapar.
    * *Not:Callbomb da oldugu gibi arada gerçeklesen api guncellemeleri yüzünden çalısmayabilir ya iletişim kısmından bizimle iletişime gecin veya yeni güncellemeleri bekleyiniz*

4.  **Base64 Decode (`base64decode.py`):**
    * Base64 formatında kodlanmış metinleri çözer.*

5.  **Netflix Checker (`netflix_checker.py`):**
    * Verilen e-posta ve şifre kombinasyonlarının Netflix'te geçerli olup olmadığını Selenium kullanarak otomatik olarak kontrol eder.
    * *Not:Netflix tarafındaki güncellemeler yüzünden devredışı kalabilir aynı şekilde iletişim kısmındaki hesaplarla ya iletişime geçin yada yeni güncellemeyi bekleyiniz*

---

## Gereksinimler

* **Python:** Sürüm 3.7 veya üstü önerilir.
* **Google Chrome:** Netflix Checker aracı için gereklidir.
* **ChromeDriver:** Netflix Checker için gereklidir. Kullandığınız Google Chrome sürümüyle uyumlu olmalı ve sisteminizin `PATH` değişkenine eklenmiş olmalı veya betiklerin bulunduğu dizinde yer almalıdır. [ChromeDriver İndirme](https://chromedriver.chromium.org/downloads)

---

## Kurulum
Eğer hiçbir paket yüklü değil ise bu adımları uygulayın: (termux için)
1-termux-setup-storage (gelen izine izin verin)
2-pkg install git
3-pkg install python )Eğer y/n sorusu gelirse y deyip devam edin)
4-pkg install clang
Termux kurulu ise şu adımları takip edin:
git clone https://github.com/poruqs/401tool2.git
(eğer git i clone ettiyseniz güncellemek için git pull yazın)
cd 401tool2

Başlatmak için:
    python main.py

## Önemli Notlar

* **Etik Kullanım:** Lütfen bu araçları sorumlu bir şekilde ve yalnızca yasalara uygun durumlarda kullanın.

---
## İletişim

Telegram Kanalımız : https://t.me/Hack_401

Discord : (Çok Yakında!)

İnstagram : @themyxaaisbest
            @afk.kloxss
            @trx.west_

*Bu Tool  [2025-04-13] tarihinde güncellenmiştir.*