# TC-SGB `filter-lists` branch

Rolling single-commit mirror of Brave / AdGuard custom filter lists.
Refreshed daily by the `Scheduled Fetch` workflow; history is not kept
(force-pushed) so daily snapshots never bloat the repo. A feed that
fails on a given day keeps serving its last good snapshot.

Files are numbered so Brave (which sorts subscriptions by URL) shows
them in country order. `04` is reserved for Lithuania (NKSC), whose
source sits behind a Cloudflare challenge and cannot be fetched yet.

Brave'de abone ol: `brave://adblock` → Add filter list via URL:

- Türkiye | TC-SGB:
    https://raw.githubusercontent.com/bayraktarozcan/TC-SGB-API-to-List/filter-lists/01-turkiye-sgb_adguard.txt
- Polonya | CERT.PL:
    https://raw.githubusercontent.com/bayraktarozcan/TC-SGB-API-to-List/filter-lists/02-polonya-certpl_adguard.txt
- Slovenya | CERT.SI:
    https://raw.githubusercontent.com/bayraktarozcan/TC-SGB-API-to-List/filter-lists/03-slovenya-certsi_adguard.txt

Azerbaycan | Blacklist.gov.az listesi kapsam dışıdır: ürettiği sonuçlar
güvenilir değildi, bu yüzden artık yayımlanmıyor ve `03-azerbaycan-`
dosyası bu daldan kaldırıldı. / The Azerbaijani blacklist.gov.az list
is out of scope: its contents were unreliable, so it is no longer
published and its file has been removed from this branch.
