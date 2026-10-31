# Low-Glow — İnsan ve Gezegen Odaklı Tasarım Çekirdeği

> **Tasarım amacı:** Teknoloji ile insan, toplum ve doğal çevre arasındaki etkileşimi; gereksiz karmaşıklığı, görsel yükü, kaynak tüketimini ve olumsuz etkileri azaltırken anlaşılabilirliği, erişilebilirliği, etkinliği, güvenilirliği ve uzun ömürlülüğü artıracak biçimde tasarlamak.

**Belge türü:** Bağlamdan bağımsız tasarım ilkeleri ve uygulama yönergesi\
**Kullanım alanı:** Dijital ürünler, web siteleri, uygulamalar, teknik belgeler, kontrol panoları, veri görselleştirmeleri, sunumlar, grafikler ve diğer dijital çıktılar\
**Görsel kimlik:** Low-Glow / True Black / Quiet Technical Editorial\
**Sürüm:** 1.0

---

## 1. Temel Yaklaşım

Bu belgeyi, tasarım ve geliştirme işlerinde kalıcı başvuru ilkesi olarak kullan. Herhangi bir teknolojiye, platforma, kişiye, markaya veya tek bir projeye bağımlı olma. Hedef bağlamın gereksinimlerini ayrıca değerlendir; ancak bu çekirdekteki ilkeleri gerekçesiz biçimde terk etme.

Tasarım başarısını yalnızca görünüşle ölçme. Şu hedefleri birlikte gözet:

1. **İnsanî etkinlik:** Bilgi kolay bulunmalı ve anlaşılmalı; görevler gereksiz adım, dikkat veya çaba gerektirmemeli.
2. **Erişilebilirlik:** İçerik farklı duyusal, bilişsel ve motor gereksinimlerde kullanılabilir olmalı.
3. **Görsel konfor:** Parlama, metin boyutu, satır uzunluğu, karşıtlık, yoğunluk ve hareket ölçülü biçimde yönetilmeli.
4. **Kaynak verimliliği:** Görüntüleme, işlemci, ağ, depolama ve veri aktarımı için gereksiz yük oluşturulmamalı.
5. **Çevresel sorumluluk:** Tasarımın yaşam döngüsü, bakım ihtiyacı, kaynak tüketimi, yenileme sıklığı ve atık etkileri düşünülmeli.
6. **Güvenilirlik ve süreklilik:** Çözüm kararlı, bakımı yapılabilir, anlaşılır, güvenli ve gerektiğinde geri alınabilir olmalı.
7. **Özgünlük:** Kimlik; görsel efekt yığmakla değil, tutarlı ilkeler, düzen, tipografi ve anlamlı ayrıntılarla kurulmalı.

Bu hedefler arasında ödünleşimler olabilir. Bunları saklama; seçenekleri, kanıtları, maliyetleri ve gerekçeleri açıkça belirt.

## 2. Görsel Kimlik: Low-Glow

### 2.1. Genel Karakter

Görsel dil sakin, teknik, yalın, rafine ve zamansız olmalıdır. Karanlık görünümü bir süsleme değil, bilinçli bir görüntüleme tercihi olarak ele al.

- **True Black:** Destekleyen ekranlarda ana zemin için tam siyahı (`#000000`) varsayılan kabul et.
- **Low-Glow:** Parlak, ışıklı, titreşen veya dikkat isteyen efektlerden kaçın; vurguyu renk, boşluk ve tipografiyle kur.
- **Quiet Technical Editorial:** Teknik çizim, sistem haritası ve editoryal yayın düzeninden ilham al; ancak gereksiz dekoratif ayrıntıları kullanma.
- **Düşük görsel gürültü:** Aynı anda öne çıkan öğe sayısını sınırla. Her vurgu anlamlı bir görevi desteklemeli.
- **Özgünlük:** Hazır bir temayı yalnızca renk değiştirerek sunma. İçerik ve bağlama uygun özgün bir düzen geliştir.

Sunucu fotoğrafları, devre kartı klişeleri, neon ışımalar, sahte terminal metinleri, parçacık animasyonları, aşırı yuvarlatılmış kartlar ve dekoratif rozetleri varsayılan olarak kullanma. Ancak açık bir gereksinimi karşılıyorlarsa değerlendir.

### 2.2. Ana Renk Paleti

Aşağıdaki palet, tasarım sisteminin temel renk sözlüğüdür. Değerler başlangıç token'larıdır; her bileşende tek tek ve tutarsız biçimde yeniden tanımlanmamalıdır.

| Tasarım belirteci | Değer | Kullanım |
|---|---|---|
| `--color-bg` | `#000000` | Ana zemin; OLED odaklı True Black |
| `--color-surface` | `#080B09` | Zemin üzerinde düşük ayrımlı ikincil yüzey |
| `--color-text` | `#C5CDC8` | Ana metin; saf beyaz yerine yumuşatılmış açık gri |
| `--color-muted` | `#AEB7B1` | Açıklama ve ikincil gövde metni |
| `--color-subtle` | `#9AA49E` | Meta bilgi, etiket ve ikincil işaretler; karşıtlığı ayrıca doğrula |
| `--color-accent` | `#9DBFA8` | Ölçülü adaçayı yeşili; bağlantı, odak ve seçili öğeler |
| `--color-border` | `#242C27` | İnce ayraçlar, kenarlıklar ve yapısal sınırlar |

Kurallar:

- Saf siyah ana zemin olarak korunur; zemin üzerinde her şeyi eşit parlaklıkta gösterme.
- Saf beyazı (`#FFFFFF`) geniş metin alanlarında varsayılan metin rengi yapma.
- Parlak neon, yüksek doygunluklu çoklu vurgu paletleri ve yapay parıltı kullanma.
- Adaçayı yeşilini her yerde değil, anlamlı etkileşim ve yönlendirme noktalarında kullan.
- Renk tek başına anlam taşımasın; bağlantılar, durumlar ve hata/başarı işaretleri biçim, metin veya simgeyle de ayırt edilebilsin.
- Renkleri yüzey ve metin bağlamında ayrı ayrı sınayarak karşıtlık oranlarını gerçek kullanım çifti üzerinden hesapla.
- Bu paletin herkes için en konforlu olduğu veya belirli bir sağlık durumuna klinik yarar sağladığı iddia edilmemelidir.

### 2.3. Işık, Karşıtlık ve OLED

OLED ekranlarda siyah piksellerin ışık yayımının kapanabilmesi, siyah ağırlıklı tasarımı enerji bakımından anlamlı kılabilir. Gerçek kazanç panel teknolojisi, parlaklık, içerik, görüntüleme alanı ve cihazın diğer bileşenlerine bağlıdır. Ölçüm yapılmadan tasarruf yüzdesi verme.

Tam siyah tasarımın görsel konfor bakımından herkes için üstün olduğunu varsayma. Yüksek karşıtlık okunabilirliği destekler; ancak bazı kişiler, ortamlarda veya görevlerde başka bir karşıtlık düzenini daha rahat bulabilir. Kullanım bağlamına uygun seçenekler sun ve gerçek kullanıcı ihtiyacını varsayımla ikame etme.

### 2.4. Tipografi ve Yerleşim

- Öncelik okunabilirlik, hiyerarşi ve metnin taranabilirliğidir.
- Gövde metni için yaklaşık `18–20px`, satır yüksekliği için `1.6–1.75` başlangıç noktası olarak değerlendirilebilir; bunlar evrensel kural değil, sınanacak tasarım değerleridir.
- Uzun metinlerde yaklaşık `60–70` karakterlik satır genişliğiyle başla ve içeriğe göre ayarla.
- Çok ince yazı karakterlerinden, gereksiz büyük harf kullanımından, sıkıştırılmış satırlardan ve yalnızca renkle kurulan hiyerarşiden kaçın.
- Başlıklarda belirgin, gövde metninde rahat okunan bir sans-serif; kod ve teknik etiketlerde tutarlı bir monospace yazı tipi kullan.
- Önce sistem yazı tiplerini değerlendir. Haricî font kullanılıyorsa dosya sayısı, lisansı, yükleme davranışı, dil kapsamı ve yedek font zinciri doğrulansın.
- Boşluk, ölçek, çizgi kalınlığı ve bölüm numaralandırmasını tutarlı kullan.
- İçerik genişliği, görev ve ekran boyutuna göre ayarlanmalı; uzun satırlar tüm ekrana yayılmamalıdır.

## 3. İnsan Odaklılık ve Erişilebilirlik

Erişilebilirliği sonradan eklenen bir kontrol listesi değil, tasarımın başlangıç koşulu olarak ele al.

- Normal metinde WCAG 2.2 AA düzeyindeki en az `4.5:1`, büyük metinde `3:1` karşıtlık eşiklerini uygula.
- Daha yüksek karşıtlık yararlı olabilecek ana metinlerde AAA düzeyindeki `7:1` hedefini de değerlendir; bunu bütün kullanıcılar için otomatik olarak daha rahat kabul etme.
- Klavye ile gezinme, görünür odak göstergeleri, mantıklı başlık sırası ve anlaşılır bağlantı adları sağla.
- Görsel bilgiyi mümkün olduğunda gerçek metinle de sun; anlamlı görsellere uygun ikâme metin ver.
- İçerik büyütme ve dar ekran düzenini doğrula; yakınlaştırma sırasında işlev veya bilgi kaybolmamalıdır.
- Kullanıcının sistem tercihlerini destekle: `prefers-color-scheme` ile renk teması, `prefers-reduced-motion` ile hareket azaltma.
- Hareketi gerekli olmadıkça kullanma. Hareket kullanılıyorsa anlamlı, kısa ve azaltılabilir olmalı.
- Tema, yazı boyutu veya yoğunluk ayarı sağlandığında seçimlerin açık, erişilebilir ve kararlı çalışmasını sağla.
- WCAG, ISO veya başka bir standarda uyum iddiası ancak ilgili kapsam ve ölçütler gerçekten sınandıysa kullanılmalıdır.

Erişilebilirlik standardına uyum, kişisel görsel konforun garantisi değildir. Sağlık durumları hakkında tanı koyma, tedavi vaadinde bulunma veya belirli renklerin klinik olarak yararlı olduğunu kanıtsız biçimde ileri sürme. Gerektiğinde profesyonel değerlendirme ile genel tasarım önerilerini birbirinden ayır.

## 4. Çevresel Sorumluluk ve Dijital Verimlilik

Bir dijital ürünün çevresel etkisini yalnızca renk veya dosya boyutuna indirgeme. Ürünün tasarımını, geliştirilmesini, dağıtımını, kullanımını, bakımını ve emekliye ayrılmasını birlikte değerlendir.

- Basit statik çözüm yeterliyse gereksiz çalışma zamanı, çatı veya bağımlılık ekleme.
- JavaScript, ağ isteği, üçüncü taraf izleme, otomatik video ve sürekli çalışan efektleri yalnızca açık bir ihtiyaç varsa kullan.
- Görselleri uygun ölçekte sun; SVG'leri gereksiz ayrıntıdan arındır; raster görselleri uygun biçim ve sıkıştırmayla hazırla.
- Büyük medya ve yazı tipi dosyalarının yüklenmesini gerçekten gerektiği durumlarla sınırla.
- Kullanılmayan kodu, bağımlılıkları, bileşenleri ve ağ çağrılarını kaldır.
- Performans, erişilebilirlik, gizlilik ve güvenliği çevresel hedefler uğruna feda etme; bu nitelikleri birlikte değerlendir.
- Enerji, karbon veya kaynak tasarrufuna ilişkin nicel iddialar için yöntem, veri, sınır ve ölçüm dönemi belirt. Ölçülemeyen kazanımları sayı olarak sunma.
- Gerektiğinde kaynak kullanımı, performans ve karbon yoğunluğu için uygun ölçüm yöntemlerini araştır; farklı ölçüm birimlerini birbirine karıştırma.

## 5. Bilgi Mimarisi ve Etkileşim

- Önce kullanıcının amacı ve en önemli görevleri belirle; ardından içerik hiyerarşisini oluştur.
- Bir ekranda veya bölümde tek bir açık görsel odak bulunmasına dikkat et.
- Bölüm etiketleri, numaralandırma ve ayraçlar yalnızca içeriği düzenlemeye hizmet etsin.
- Kartları ve panelleri varsayılan çözüm olarak kullanma; içerik bir liste, düz metin veya tablo ile daha iyi anlaşılabiliyorsa daha basit biçimi seç.
- Durum bilgisi, hata ve başarı mesajları açık ve metinsel olmalı; yalnızca renge veya animasyona dayanmamalı.
- Haricî hizmetlere, canlı sayımlara veya ağ bağlantısına bağımlı dekoratif bileşenlerden kaçın.
- Kullanıcıya ait veri toplamayı varsayılan olarak en aza indir; ölçüm ve izleme gerekliyse amacını, kapsamını ve gizlilik etkisini değerlendir.

## 6. Kaynak Disiplini ve Karar Kayıtları

Tasarım kararlarını yalnızca alışkanlığa, beğeniye veya popüler örneklere dayandırma. Öncelik sırası:

1. İlgili uluslararası standartlar ve resmî teknik şartnameler.
2. Platform ve teknoloji sahibinin güncel birincil belgeleri.
3. Sistematik derlemeler ve hakemli araştırmalar.
4. Kamu kurumları ve uzman araştırma kuruluşlarının rehberleri.
5. Uygulama örnekleri ve topluluk kaynakları; fikir üretmek için, birincil kanıt yerine değil.

Her önemli iddia ve karar için mümkünse şu bilgileri kaydet: kaynak, bağlantı, yayımlanma ve güncellenme tarihi, belge statüsü, desteklediği iddia, kapsam, sınırlamalar ve son doğrulama tarihi.

Birincil kaynağa erişilebiliyorsa yalnızca ikincil kaynak özetine dayanma. Kaynakların statülerini birbirine karıştırma: bir standart, taslak rehber, akademik bulgu, üretici önerisi ve kişisel tasarım tercihi aynı kanıt düzeyinde değildir.

Kaynaklar çelişirse çelişkiyi saklama; yöntem, örneklem, bağlam, tarih ve genellenebilirlik sınırlarını kaydet. Tam metne erişemediğin belgeyi okumuş gibi gösterme. Telif ve lisans koşullarını denetle; korunmuş materyali izinsiz kopyalamak yerine kendi özgün anlatımını üret ve kaynak göster.

Gelecek olasılıklarını düşünürken Value Sensitive Design, sistem düşüncesi, senaryo geliştirme ve spekülatif tasarım gibi yöntemleri kullanabilirsin. Bu yöntemleri normatif teknik standartmış gibi sunma.

## 7. Uygulama Yöntemi

Her işte aşağıdaki sırayı izle; işin ölçeğine göre adımları orantılı uygula:

1. **Bağlamı anla:** Amaç, kullanıcılar, ortam, sınırlar, mevcut yapı ve başarı ölçütlerini belirle.
2. **Kanıtı araştır:** Resmî kaynakları ve gerekli araştırmaları kontrol et; belirsizlikleri kaydet.
3. **Tasarımı kur:** Bu çekirdeğin renk, tipografi, yerleşim, etkileşim ve verimlilik ilkelerini kullan.
4. **Basit çözümü seç:** İhtiyaç karşılanıyorsa daha karmaşık araç ekleme; seçenekleri gerekçeyle karşılaştır.
5. **Uygula:** Mevcut işlevleri koru, değişiklikleri küçük ve geri alınabilir tut.
6. **Doğrula:** İşlevsellik, erişilebilirlik, uyarlanabilirlik, güvenlik, performans ve kaynak yükünü sınamaya tabi tut.
7. **Regresyonu denetle:** Değişikliğin mevcut işlevleri, bağlantıları, düzeni veya kullanıcı tercihlerini bozmadığını tekrar kontrol et.
8. **Kaydet:** Gerçekleşen işlemleri, kullanılan kaynakları, ölçümleri, başarısızlıkları ve açık riskleri belgele.
9. **İyileştir:** Yeni bulguları ve deneyim sonuçlarını tasarım belirteçlerine, kaynak kayıtlarına ve karar notlarına işle.

## 8. Kalite ve Kabul Ölçütleri

Bir çıktı ancak ilgili ölçütler değerlendirilip sonuçlar kaydedildiğinde tamamlanmış kabul edilir.

- Görsel dil tutarlı ve bağlama uygun mu?
- Renk ve yazı sistemi tanımlı belirteçleri kullanıyor mu?
- Metin karşıtlığı, yakınlaştırma, dar ekran düzeni, klavye kullanımı ve odak görünürlüğü sınandı mı?
- Sistem renk ve hareket tercihleri doğru ele alınıyor mu?
- Görseller, yazı tipleri ve bağımlılıklar gereğinden ağır mı?
- Dış bağlantı veya üçüncü taraf hizmeti olmadan çalışması gereken bölümler çalışıyor mu?
- Güvenlik ve gizlilik açısından gereksiz bir veri toplama veya erişim izni var mı?
- Yapılan değişiklikler mevcut işlevleri bozdu mu?
- Kaynaklara dayanan iddialar doğru, güncel ve sınırları belirtilmiş mi?
- Tamamlanmamış testler, başarısızlıklar ve belirsizlikler açıkça belirtilmiş mi?

Otomatik taramalar tek başına kalite kanıtı değildir. Uygun olduğunda manuel inceleme, gerçek cihazda görüntüleme ve kullanıcı odaklı sınama da uygula.

## 9. Bu Çekirdeğin Esnetilebileceği ve Esnetilemeyeceği Noktalar

**Bağlayıcı temel ilkeler:** Dürüst kanıt kullanımı, erişilebilirlik, insan odaklılık, kaynak sorumluluğu, gereksiz karmaşıklığın azaltılması, güvenlik ve ölçülemeyen başarıyı iddia etmeme.

**Varsayılan tasarım tercihleri:** True Black zemin, `#C5CDC8` ana metin, `#9DBFA8` adaçayı vurgusu, düşük görsel gürültü, teknik-editoryal düzen, sınırlı hareket ve özgün vektör grafikleri.

**Bağlama göre uyarlanabilecek unsurlar:** Açık tema ikâmesi, yazı boyutları, bileşen biçimleri, bilgi yoğunluğu, simge kullanımı, teknoloji seçimi ve animasyon miktarı.

Bir tercih hedef platformda kullanılamıyorsa, erişilebilirliği bozuyorsa veya somut gereksinimlerle çatışıyorsa sebebini kaydet ve en yakın güvenilir ikâmeyi seç. Salt estetik tercih, erişilebilirlik veya güvenlik gereksinimlerini geçersiz kılmamalıdır.

## 10. Yetkili Başvuru Kaynakları

Aşağıdaki bağlantılar sürekli geçerli tasarım ilkeleri için başlangıç kaynaklarıdır. Kullanımdan önce güncel sürümlerini ve belgelerin resmî statülerini tekrar kontrol et.

### Standartlar ve İnsan Odaklı Tasarım

- **W3C — WCAG 2.2:** https://www.w3.org/TR/WCAG22/\
  Web erişilebilirliği için normatif başarı ölçütleri.
- **W3C WAI — Contrast Minimum:** https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html\
  Metin karşıtlığı ölçütleri.
- **W3C WAI — Reflow:** https://www.w3.org/WAI/WCAG22/Understanding/reflow.html\
  Dar ekran ve yakınlaştırmada içerik düzeni.
- **W3C — Media Queries Level 5:** https://www.w3.org/TR/mediaqueries-5/\
  Kullanıcı renk ve hareket tercihleriyle ilişkili medya özellikleri.
- **ISO 9241-210:2019:** https://www.iso.org/standard/77520.html\
  Etkileşimli sistemlerin yaşam döngüsü boyunca insan odaklı tasarım. ISO'nun kayıt sayfası bu sürümün 2025'te gözden geçirilip güncel kaldığını belirtir.
- **ISO 9241-171:2025:** https://www.iso.org/standard/86308.html\
  Yazılım erişilebilirliği için yayımlanmış uluslararası standart.

### Sürdürülebilirlik ve Yazılım Verimliliği

- **W3C — Web Sustainability Guidelines:** https://www.w3.org/TR/web-sustainability-guidelines/\
  İnsan, gezegen ve refah boyutlarını kapsayan web sürdürülebilirliği rehberi. 2026-09-24 sürümü W3C Group Note Draft statüsündedir; normatif Recommendation gibi sunma. Yayın geçmişi: https://www.w3.org/standards/history/web-sustainability-guidelines/
- **ISO/IEC 21031:2024 — Software Carbon Intensity:** https://www.iso.org/standard/86612.html\
  Yazılım sistemlerinin karbon yoğunluğunu hesaplama yöntemi; ISO sayfasında yayımlanmış uluslararası standart olarak listelenir.
- **Green Software Foundation — SCI:** https://greensoftware.foundation/standards/sci/
- **Green Software Patterns:** https://patterns.greensoftware.foundation/
- **web.dev — Web Vitals:** https://web.dev/articles/vitals
- **Chrome for Developers — Lighthouse:** https://developer.chrome.com/docs/lighthouse/overview

### Platform Uygulaması

- **MDN — `prefers-color-scheme`:** https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/%40media/prefers-color-scheme
- **MDN — `prefers-reduced-motion`:** https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/%40media/prefers-reduced-motion
- **Android Developers — Dark theme:** https://developer.android.com/develop/ui/views/theming/darktheme\
  Koyu tema ve ekran teknolojisine bağlı enerji etkisi hakkında platform rehberi; mobil sonuçları başka ekran sınıflarına doğrudan genelleme.

### Değerler ve İkâme Gelecekler

- **Value Sensitive Design Lab — Envisioning Cards:** https://vsdesign.org/toolkits/envisioningcards/
- **UK Government Office for Science — The Futures Toolkit:** https://www.gov.uk/government/publications/futures-toolkit-for-policy-makers-and-analysts/the-futures-toolkit-html
- **SpeculativeEdu — Online Repository:** https://github.com/speculativeedu/The-SpeculativeEdu-Online-Repository

Bu katalog kapalı veya değişmez değildir. Yeni kaynak eklenecekse otoritesi, kaynağın statüsü, kapsadığı iddialar ve lisans koşulları doğrulanmalıdır.

---

## Kısa Kullanım Talimatı

Bu belgeyi yeni bir projeye başlarken temel tasarım bağlamı olarak yükle veya ana yönergenin başına ekle. Ardından projeye özgü amacı, hedef kullanıcıları, teslimatları ve teknik kısıtları ayrı bir bölümde tanımla. Projeye özel talimatlar bu çekirdeği yalnızca gerekçeli, belgelenmiş ve güvenlik/erişilebilirlik ilkeleriyle çelişmeyen durumlarda özelleştirmelidir.

**Özet:** True Black. Soft Light. Quiet Structure. Human First. Planet Aware. Evidence Always.
