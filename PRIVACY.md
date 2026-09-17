[English](#-english) | [Türkçe](#-türkçe)

<a id="-english"></a>

# Privacy Statement

This project is a threat-intelligence tool. It fetches **public IoC
(indicator of compromise) data** published by the
[T.C. Siber Güvenlik Başkanlığı (SGB)](https://siberguvenlik.gov.tr) API and
converts it into filtering/blocking lists.

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

## What about the SGB API?

Queries to the SGB API are governed by the SGB website terms of use and any
applicable public-data policies. This project is not affiliated with or
endorsed by the presidency.

---

<a id="-türkçe"></a>

# Gizlilik Bildirimi

Bu proje bir siber tehdit istihbaratı aracıdır. [T.C. Siber Güvenlik
Başkanlığı](https://siberguvenlik.gov.tr) API'si tarafından yayımlanan
**kamuya açık IoC (tehdit göstergesi) verilerini** indirir ve filtreleme/engelleme
listelerine dönüştürür.

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

## SGB API'si hakkında

SGB API'sine yapılan sorgular, SGB web sitesinin kullanım koşullarına ve geçerli
kamuya-açık veri politikalarına tabidir. Bu proje kurumla bağlantılı değildir
veya kurum tarafından desteklenmez.