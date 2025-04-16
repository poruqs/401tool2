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

Bu araç koleksiyonu **öncelikle eğitim ve yasal test amaçlı** olarak tasarlanmıştır. Lütfen kullanmadan önce aşağıdaki uyarıları **çok dikkatli** bir şekilde okuyun:

* **Sorumluluk:** Bu araçların kullanımından doğacak **tüm yasal ve etik sorumluluk tamamen kullanıcıya aittir**. Araçları kullanmadan önce bulunduğunuz ülkenin ve hedef sistemin bulunduğu ülkenin yasalarına, ayrıca ilgili hizmet sağlayıcıların (Google, Netflix, sosyal medya platformları vb.) kullanım koşullarına uyduğunuzdan **kesinlikle** emin olun.
* **Yasa Dışı Kullanım:** Araçların (özellikle **Call Bomb**, **SMS Bomb**, **DoS/DDoS Saldırıları** ve **Wi-Fi Jammer**) **size ait olmayan veya kullanma izniniz olmayan** sistemlere, ağlara veya kişilere karşı kullanılması **kesinlikle yasa dışıdır** ve **çok ciddi yasal sonuçlar** (yüksek para cezaları, hapis cezası, erişim engelleri vb.) doğurabilir. Geliştirici, araçların herhangi bir şekilde kötüye kullanılmasından veya yasa dışı kullanımından **kesinlikle sorumlu tutulamaz.**
* **API Güvenilmezliği:** `SMS Bomb`, `Call Bomb` gibi araçlar, üçüncü parti web sitelerinin ve servislerin API'lerine (uygulama programlama arayüzleri) dayanmaktadır. Bu API'ler **resmi değildir, belgeleri yoktur ve servis sağlayıcıları tarafından sık sık değiştirilir, kısıtlanır veya tamamen kapatılır.** Bu nedenle, bu araçların işlevselliği **garanti edilmez** ve büyük olasılıkla **çalışmayacaklar veya hatalarla** karşılaşacaksınız. Bu durum, betiklerin kendisinde bir hata olduğu anlamına gelmez, dayandıkları dış servislerin değişmesinden kaynaklanır.
* **Framework Araçları ve Karmaşıklık:** Menüdeki "Framework" olarak işaretlenmiş seçenekler (`Web Saldırı`, `Instagram Araçları`, `Sosyal Medya Bulucu`, `Wi-Fi Jammer`, `DDoS Araçları`), kendi içlerinde birçok farklı harici aracı (genellikle GitHub'dan indirilen) kurmayı ve çalıştırmayı denerler. Bu iç araçların çalışması **garanti değildir** ve şunlara bağlıdır:
    * Harici aracın GitHub deposunun hala erişilebilir ve güncel olması.
    * Kurulum için gerekli **bağımlılıkların** (belirli Python kütüphaneleri, sistem kütüphaneleri, derleme araçları vb.) sisteminizde **kurulu olması**. Eksik bağımlılıklar kurulumun veya aracın çalışmasının başarısız olmasına neden olur.
    * Gerekli **izinlerin** (`sudo` gibi) doğru şekilde kullanılması.
    * **Derleme** gerektiren araçlar (`Dirb`, `aSYNcrone` gibi) için sisteminizde `gcc`, `make`, `build-essential` gibi araçların kurulu olması ve derlemenin başarılı olması.
    * Harici aracın kendisinin **güncel ve çalışır** durumda olması (bazıları yıllardır güncellenmemiş olabilir).
* **Eski Teknolojiler (Python 2.7):** `insta_saldırı.py` içindeki **InstaBrute** ve `web_saldırı.py` içindeki **Blazy** gibi bazı araçlar, artık **desteklenmeyen ve güvenlik açıkları barındıran Python 2.7** sürümünü gerektirir. Modern sistemlerde Python 2.7 genellikle kurulu değildir ve bu araçlar **çalışmayacaktır.** Python 2 kurmaya çalışmak önerilmez.
* **Donanım ve Sürücü Gereksinimleri:** Özellikle `Wi-Fi Jammer` araçları, çalışabilmek için **Monitör Modu (Monitor Mode)** ve **Paket Enjeksiyonu (Packet Injection)** özelliklerini destekleyen **özel bir Wi-Fi adaptörüne**, bu adaptör için **doğru ve uyumlu sürücülere** ve genellikle **Linux tabanlı bir işletim sistemine** ihtiyaç duyar. Standart Wi-Fi kartları ve işletim sistemleri ile bu araçlar çalışmaz.
* **İşlevsiz Araçlar:** `Netflix Checker` gibi bazı araçlar, hedeflenen servisin (Netflix) aldığı güvenlik önlemleri (CAPTCHA, JavaScript kontrolleri, API değişiklikleri vb.) nedeniyle mevcut yöntemlerle (basit `requests` kullanımı) **çalışmamaktadır.**
* **Riskler:** Bombardıman araçları IP adresinizin veya telefon numaranızın ilgili servisler tarafından engellenmesine yol açabilir. DoS/DDoS ve Wi-Fi Jammer araçları, hedeflediğiniz (veya yanlışlıkla hedeflediğiniz) sistemlere, ağlara zarar verebilir, hizmet kesintilerine yol açabilir ve **kritik iletişimleri (acil durum çağrıları vb.) engelleyebilir.**
* **UTF-8 Kodlaması:** Bu projedeki `.py` dosyaları Türkçe karakterler ve özel semboller içerir. Dosyaları kopyalayıp kaydederken metin düzenleyicinizde **UTF-8 kodlamasını** seçtiğinizden emin olun, aksi takdirde "non-basic ASCII" hatası alabilirsiniz.

**Bu araçları indirerek, kurarak veya kullanarak yukarıda belirtilen tüm uyarıları, riskleri ve yasal sorumlulukları okuduğunuzu, anladığınızı ve KABUL ETTİĞİNİZİ beyan etmiş sayılırsınız.**

---

## ✨ DİKKAT: ANA MENÜ İÇİN COLORAMA GEREKLİ ✨

Ana menünün (`401main.py`) düzgün ve renkli çalışması için `colorama` kütüphanesinin **yüklü olması gerekmektedir**. Eğer kurulu değilse, program başlangıçta bir uyarı verecektir.

### Colorama Kurma

`colorama` kütüphanesini aşağıdaki komutla kolayca kurabilirsiniz:

```bash
pip install colorama
Veya Python 3 için:

Bash

pip3 install colorama
Tool Araçları ve Özellikleri (Ana Menüye Göre)
Aşağıdaki liste, 401main.py betiğindeki (son güncellenen) menüye ve araçların tahmini durumlarına karşılık gelir:

Call Bomb (call_bomb.py): Belirtilen telefon numarasına Truecaller API'si üzerinden otomatik arama/OTP isteği gönderir. (Durum: API güncelliği şüpheli, API Sorunlu)
SMS Bomb (sms_bomb.py): Çok sayıda farklı servisin API'sini kullanarak belirtilen numaraya yoğun OTP/mesaj gönderimi yapar. (Durum: API'ler çok sık değiştiği için API Sorunlu)
DoS Saldırısı (DoS.py): Hedef IP ve porta yüksek hacimli UDP paketleri gönderir (UDP Flood). (Durum: Kod çalışır - YASADIŞI KULLANMAYIN!)
Yedek DDoS (Basit_ddos.py): Hedef URL'ye sürekli HTTP GET istekleri gönderir (Requests Flood). (Durum: Kod çalışır - YASADIŞI KULLANMAYIN!)
Netflix Checker (netflix-checker.py): E-posta/şifre ile Netflix girişi denemesi (Requests ile simülasyon). (Durum: ÇALIŞMIYOR - KULLANIM DIŞI)
Base64 Decode (base64decode.py): Base64 kodlu metni çözer. (Durum: Çalışır)
IP Toolkit (iptool.py): IP araçları (Konum, DNS, Port Tarama, MAC). (Durum: Çoğu özelliği çalışır, bazıları OS/Harici Araca bağlı)
Chromecast Hack (chromecast_hack.py): Yerel Chromecast'e komut gönderir. (Durum: API Belirsiz - Çalışmayabilir)
Web Saldırı Araçları (web_saldırı.py): Web araçları framework'ü (Skipfish, Sublist3r, Dirb, Blazy(Py2) vb.). (Durum: Framework - İç araçların çalışması bağımlılıklara/kuruluma bağlı)
Instagram Araçları (insta_saldırı.py): Sosyal medya araçları framework'ü (InstaBrute(Py2), Faceshell vb.). (Durum: Framework - İç araçların çalışması şüpheli/Py2)
Sosyal Medya Bulucu (sosyalmedya_bulma.py): OSINT araçları framework'ü (Social Mapper(Zor Kurulum), Sherlock, FindUser vb.). (Durum: Framework/OSINT - İç araçların çalışması bağımlılıklara bağlı)
Wi-Fi Jammer (wifi_jammer.py): Wi-Fi Jammer/Deauth framework'ü. (Durum: Framework - YASADIŞI! - Donanım/izin/Linux gerektirir)
DDoS Araçları (DDoS.py): DDoS araçları framework'ü (Slowloris, GoldenEye, UFONet vb.). (Durum: Framework - Kurulum/derleme/izin gerektirir. YASADIŞI KULLANMAYIN!)
Gereksinimler
(Sizin yazdıklarınız temel alınarak eklemeler yapılmıştır)

Python: Sürüm 3.7 veya üstü önerilir. (Python 2.7 gerektiren bazı iç araçlar çalışmayacaktır).
Pip: Python paket yöneticisi (pip veya pip3). Python ile birlikte gelir veya ayrıca kurulur. (Eklendi)
Git: Versiyon kontrol sistemi (Framework içindeki araçları GitHub'dan indirmek için gereklidir). (Eklendi)
Temel Python Kütüphaneleri: (Eklendi) Ana menünün ve bazı araçların çalışması için şunlar gereklidir (Kurulum bölümünde komutu verilmiştir):
colorama
requests
urllib3
uuid
ipaddress
Not: Bu temel kütüphaneleri aşağıdaki kurulum bölümünde belirtilen komutla kurabilirsiniz.
Sistem Araçları (Gerektiğinde): (Eklendi) Framework içindeki bazı araçların kurulumu veya çalışması için aşağıdaki gibi ek araçlar veya kütüphaneler gerekebilir (İşletim sisteminize göre kurmanız gerekebilir):
Derleme Araçları: gcc, make, build-essential (Debian/Ubuntu), python3-dev vb. (Örn: Dirb, aSYNcrone için)
Kabuk: bash (.sh uzantılı betikleri çalıştırmak için - örn: FindUser, KawaiiDeauther)
Termux için: clang, coreutils, build-essential vb. (pkg install ... ile)
Diğer özel sistem kütüphaneleri (Araçların kendi belgelerine bakın).
İşletim Sistemi: (Eklendi) Araçların çoğu platform bağımsız olsa da, özellikle Wi-Fi Jammer, derleme gerektiren araçlar ve düşük seviye ağ işlemleri yapanlar genellikle Linux ortamında daha stabil çalışır veya sadece orada çalışır. Windows veya macOS'ta uyumluluk sorunları veya ek yapılandırma ihtiyacı olabilir. Termux üzerinde bazıları çalışabilir ancak kısıtlamalar olabilir.
Özel Donanım: (Eklendi) Wi-Fi Jammer araçları için Monitör Modu (Monitor Mode) ve Paket Enjeksiyonu (Packet Injection) destekleyen uyumlu bir Wi-Fi adaptörü KESİNLİKLE GEREKLİDİR. Standart laptop Wi-Fi kartları genellikle bunu desteklemez. Harici USB Wi-Fi adaptörleri (örn. Alfa Kartlar) yaygın olarak kullanılır. Ayrıca doğru sürücülerin de kurulu olması gerekir.
İnternet Bağlantısı: (Eklendi) Kurulumlar ve bazı API'ler için gereklidir.
Kurulum
(Sizin yazdıklarınız temel alınarak eklemeler/açıklamalar yapılmıştır)

Temel Python Kütüphanelerini Kurma (Tüm Sistemler İçin Önerilen):

İlk olarak, ana menünün ve birçok aracın ihtiyaç duyduğu temel Python kütüphanelerini kurun:
Bash

pip install colorama requests urllib3 uuid ipaddress
(veya pip3 install ...)
Depoyu İndirme ve Klasöre Girme (Tüm Sistemler):

Eğer aracı daha önce indirmediyseniz:
Bash

git clone [https://github.com/poruqs/401tool2.git](https://github.com/poruqs/401tool2.git)
cd 401tool2
Eğer daha önce indirdiyseniz ve güncellemek istiyorsanız:
Bash

cd 401tool2
git pull
Termux İçin Ek Adımlar (Eğer Termux Kullanıyorsanız ve İlk Kez Kuruyorsanız):

Eğer hiçbir paket yüklü değil ise bu adımları uygulayın: (termux için)
termux-setup-storage (gelen izine izin verin)
pkg update && pkg upgrade -y (Paketleri güncellemek önemlidir)
pkg install git python python-pip clang build-essential coreutils -y (Gerekli temel paketler, python-pip python için pip kurar.) (Not: pkg install python komutunda y/n sorusu gelirse y deyip devam edin)
Framework İçindeki Araçların Kurulumu: (Eklendi)

Ana menüden bir framework aracını (örn. Web Saldırı, DDoS Araçları) seçtiğinizde, içindeki spesifik araçlar için genellikle bir "Install" seçeneği sunulur.
Bu "Install" seçeneğini kullanmak, o araca özel bağımlılıkları (pip install -r requirements.txt gibi) kurmayı veya derleme (make) yapmayı dener.
Bu kurulumların başarılı olması için sisteminizde gerekli diğer araçların (gcc, make, python3-dev vb.) kurulu olması gerekebilir. Hata alırsanız, hata mesajlarını okuyarak eksik bağımlılıkları manuel olarak kurmanız gerekebilir.
Başlatma
Ana menüyü (401main.py) çalıştırmak için, 401tool2 klasörünün içindeyken aşağıdaki komutu kullanın:

Bash

python 401main.py
Veya sisteminiz varsayılan olarak Python 2 kullanıyorsa veya python3 komutunu kullanmanız gerekiyorsa:

Bash

python3 401main.py
sudo Kullanımı: Özellikle Wi-Fi Jammer gibi donanıma doğrudan erişen araçlar veya bazı kurulum komutları (sudo içerenler) root yetkisi gerektirebilir. Eğer "Permission denied", "Operation not permitted" gibi hatalar alırsanız veya aracın çalışması için root gerektiği belirtilmişse, ana betiği sudo python3 401main.py şeklinde çalıştırmayı deneyebilirsiniz. Ancak sudo komutunu gereksiz yere kullanmak güvenlik riski oluşturabilir, sadece gerektiğinde kullanın.
Önemli Notlar
Etik Kullanım: Lütfen bu araçları sorumlu bir şekilde ve yalnızca test etme veya güvenlik araştırması yapma izniniz olan sistemler üzerinde, yasalara ve etik kurallara uygun durumlarda kullanın.
Framework Mantığı: Menüdeki "(Framework)" ile işaretli seçenekler, aslında birçok farklı aracı bir araya getiren ve onları kurup çalıştırmak için bir arayüz sunan betiklerdir. Bu framework'ler çalışsa bile, içindeki her bir aracın ayrı ayrı kurulması ve çalıştırılması gerekebilir ve bu süreçlerde sorunlar yaşanabilir.
Harici Dosyalar: iptool.py içindeki "ARP Spoof" ve "RPC Dump" özellikleri, sizin ayrıca temin edip indirmeniz ve betikle aynı dizinde (veya içinde) bir files klasörü oluşturup oraya koymanız gereken harici programlara (arpspoof.exe, rpcdump.exe vb.) ihtiyaç duyar. Bu dosyalar bu pakete dahil değildir.
UTF-8 Kodlaması: Tüm .py dosyalarını ve bu readme.md dosyasını metin düzenleyicinizde açarken veya kaydederken UTF-8 kodlamasını kullandığınızdan emin olun. Aksi takdirde Türkçe karakterler veya özel semboller nedeniyle hatalar alabilirsiniz.
İletişim
Telegram Kanalımız : https://www.google.com/search?q=https://t.me/Hack_401

Discord : (Çok Yakında!)

İnstagram : @themyxaaisbest, @afk.kloxss, @trx.west_

Bu Tool [2025-04-16] tarihinde güncellenmiştir.