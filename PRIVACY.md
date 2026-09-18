[English](#-english) | [Türkçe](#-türkçe)

<a id="-english"></a>

# Privacy Statement

This project is a threat-intelligence tool. It fetches **public IoC
(indicator of compromise) data** published by the
[T.C. Siber Güvenlik Başkanlığı (SGB)](https://siberguvenlik.gov.tr) API and
converts it into filtering/blocking lists.

## Our commitment to you

- **This project does not collect, store, sell, or share any user data — and it
  never will.**
- There is no account, no sign-up, no login, no analytics, no cookies, no
  tracking, and no telemetry. Nothing about this project is designed around your
  data, and we have **no interest in it whatsoever**.
- Privacy is a **deliberate design decision we make and keep**. The only data
  this software ever touches is the public threat-intelligence data you choose
  to process; apart from the API requests you trigger, everything happens
  locally on your machine.
- If this stance ever had to change, it would require an explicit change to the
  source code, and this statement would be updated and announced through the
  [CHANGELOG](CHANGELOG.md). We would never change it silently.

## What this tool does with data

- **Source data** — requests are sent to the SGB API to download publicly
  published cyber-threat indicators. No account, login, or personal data is
  required or transmitted.
- **Local processing** — validation, normalization, scoring, deduplication, and
  output generation all happen locally on your machine. Data is not sent to any
  third party by this project.
- **No telemetry** — this project contains no analytics, crash reporting, or
  usage tracking.
- **Logs** — application logs may include IoC values (domains, IPs, URLs) for
  debugging; these are written where you run the tool.

## About the SGB API and changing rules

- Queries to the SGB API are governed by the SGB website's terms of use and any
  applicable public-data policies.
- Those rules and policies are outside our control and **can change over time**.
  If you rely on this tool, please periodically review the SGB website's privacy
  policy / terms of use as well as this file (`PRIVACY.md`) so you stay
  informed.
- This project is not affiliated with or endorsed by the presidency.

---

<a id="-türkçe"></a>

# Gizlilik Bildirimi

Bu proje bir siber tehdit istihbaratı aracıdır. [T.C. Siber Güvenlik
Başkanlığı](https://siberguvenlik.gov.tr) API'si tarafından yayımlanan
**kamuya açık IoC (tehdit göstergesi) verilerini** indirir ve filtreleme/engelleme
listelerine dönüştürür.

## Size verdiğimiz söz

- **Bu proje hiçbir kullanıcı verisini toplamaz, saklamaz, satmaz veya
  paylaşmaz — ve asla paylaşmayacaktır.**
- Hesap yok, üyelik yok, giriş yok, analitik yok, çerez yok, takip yok,
  telemetri yok. Bu projenin hiçbir kısmı veriniz üzerine kurgulanmamıştır ve
  **verinizle en ufak bir ilgimiz yoktur**.
- Gizlilik, **bilinçli aldığımız ve koruduğumuz bir tasarım kararıdır**. Bu
  yazılımın dokunduğu tek veri, işlemeyi seçtiğiniz kamuya açık tehdit
  istihbaratı verisidir; tetiklediğiniz API istekleri dışında her şey makinenizde
  yerel olarak gerçekleşir.
- Bu duruşun değişmesi gerekirse, kaynak kodda açık bir değişiklik gerektirir ve
  bu bildirim güncellenip [CHANGELOG](CHANGELOG.md) üzerinden duyurulur. Asla
  sessizce değiştirmeyiz.

## Bu araç verilerle ne yapar

- **Kaynak veriler** — SGB API'sine yalnızca yayımlanmış siber tehdit
  göstergelerini indirmek için istek gönderilir. Hesap, giriş veya kişisel veri
  gerekmez ve iletilmez.
- **Yerel işleme** — doğrulama, normalleştirme, puanlama, yinelenen kayıtları
  ayıklama ve çıktı üretimi tamamen makinenizde gerçekleşir. Bu proje verileri
  üçüncü taraflara göndermez.
- **Telemetri yok** — bu proje herhangi bir analiz, çökme raporu veya kullanım
  takibi içermez.
- **Günlükler** — uygulama günlükleri hata ayıklama amacıyla IoC değerlerini
  (alan adları, IP'ler, URL'ler) içerebilir; bunlar aracı çalıştırdığınız yere
  yazılır.

## SGB API'si ve değişen kurallar hakkında

- SGB API'sine yapılan sorgular, SGB web sitesinin kullanım koşullarına ve
  geçerli kamuya-açık veri politikalarına tabidir.
- Bu kural ve politikalar kontrolümüz dışındadır ve **zamanla değişebilir**. Bu
  aracı kullanıyorsanız, güncel kalmak için lütfen SGB web sitesinin gizlilik
  politikasını / kullanım koşullarını ve bu dosyayı (`PRIVACY.md`) periyodik
  olarak gözden geçirin.
- Bu proje kurumla bağlantılı değildir veya kurum tarafından desteklenmez.