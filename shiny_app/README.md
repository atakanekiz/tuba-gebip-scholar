# TÜBA GEBİP Akademik Performans Keşif Aracı - Shiny Dashboard

Bu Shiny uygulaması, TÜBA GEBİP ödül sahiplerinin akademik performans metriklerini keşfetmek için interaktif bir gösterge panelidir.

## Özellikler

- **📈 Keşif Aracı**: Özelleştirilebilir eksenler, renkler ve boyutlarla interaktif scatter plotlar
- **👤 Araştırmacı Profili**: Bireysel araştırmacıların detaylı profilleri
- **📊 Özet İstatistikler**: Genel istatistikler ve dağılımlar
- **🏆 Ödül Anı Analizi**: Ödül anı vs güncel performans karşılaştırması
- **📋 Veri Tablosu**: Aranabilir, sıralanabilir veri tablosu
- **ℹ️ Hakkında**: Metodoloji ve sorumluluk reddi

## Gereksinimler

### R Paketleri

```r
install.packages(c(
  "shiny",
  "plotly",
  "DT",
  "dplyr",
  "tidyr",
  "readr",
  "stringr",
  "scales"
))
```

### Alternatif: renv ile Kurulum

```r
# R konsolunda
install.packages("renv")
renv::restore()
```

## Yerel Olarak Çalıştırma

### Yöntem 1: RStudio ile

1. RStudio'da `app.R` dosyasını açın
2. Sağ üst köşedeki "Run App" butonuna tıklayın
3. Uygulama tarayıcınızda açılacaktır

### Yöntem 2: R Konsolundan

```r
# Çalışma dizinini shiny_app klasörüne ayarlayın
setwd("path/to/tuba_odulleri_scholar/shiny_app")

# Uygulamayı çalıştırın
shiny::runApp()
```

### Yöntem 3: Komut Satırından

```bash
cd path/to/tuba_odulleri_scholar/shiny_app
R -e "shiny::runApp()"
```

## Deployment Seçenekleri

### 1. shinyapps.io (Önerilen - En Kolay)

shinyapps.io, Shiny uygulamalarını bulutta barındırmak için ücretsiz bir hizmettir.

#### Adımlar:

1. **Hesap Oluşturun**: https://www.shinyapps.io/ adresinden ücretsiz hesap oluşturun

2. **rsconnect Paketini Yükleyin**:
```r
install.packages("rsconnect")
```

3. **Hesabınızı Bağlayın**:
   - shinyapps.io hesabınıza giriş yapın
   - Account > Tokens sayfasına gidin
   - "Show" butonuna tıklayın ve token'ı kopyalayın
   - R konsolunda:
```r
rsconnect::setAccountInfo(
  name="<ACCOUNT_NAME>",
  token="<TOKEN>",
  secret="<SECRET>"
)
```

4. **Uygulamayı Deploy Edin**:
```r
# shiny_app dizininde
rsconnect::deployApp()
```

5. **Web Sitenize Embed Edin**:
```html
<iframe 
  src="https://<ACCOUNT_NAME>.shinyapps.io/<APP_NAME>/" 
  width="100%" 
  height="800px" 
  frameborder="0">
</iframe>
```

#### Ücretsiz Plan Limitleri:
- 5 aktif uygulama
- Ayda 25 aktif saat
- 1 GB RAM

### 2. Shiny Server (Kendi Sunucunuzda)

Kendi sunucunuzda Shiny Server kurarak sınırsız kullanım sağlayabilirsiniz.

#### Ubuntu/Debian için Kurulum:

```bash
# R'yi kurun
sudo apt-get update
sudo apt-get install r-base

# Shiny paketini kurun
sudo su - -c "R -e \"install.packages('shiny', repos='https://cran.rstudio.com/')\""

# Shiny Server'ı indirin ve kurun
wget https://download3.rstudio.org/ubuntu-18.04/x86_64/shiny-server-1.5.20.1002-amd64.deb
sudo gkpg -i shiny-server-1.5.20.1002-amd64.deb

# Uygulamanızı kopyalayın
sudo cp -R /path/to/shiny_app /srv/shiny-server/gebip_dashboard

# Shiny Server'ı başlatın
sudo systemctl start shiny-server
```

Uygulama `http://your-server-ip:3838/gebip_dashboard/` adresinde erişilebilir olacaktır.

### 3. Docker ile Deployment

Docker container'ı ile uygulamayı herhangi bir yerde çalıştırabilirsiniz.

#### Dockerfile Örneği:

```dockerfile
FROM rocker/shiny:latest

# Sistem bağımlılıklarını kurun
RUN apt-get update && apt-get install -y \
    libcurl4-gnutls-dev \
    libssl-dev \
    libxml2-dev

# R paketlerini kurun
RUN R -e "install.packages(c('shiny', 'plotly', 'DT', 'dplyr', 'tidyr', 'readr', 'stringr', 'scales'), repos='https://cloud.r-project.org/')"

# Uygulamayı kopyalayın
COPY shiny_app /srv/shiny-server/
COPY data /srv/shiny-server/data

# Port'u expose edin
EXPOSE 3838

# Shiny Server'ı çalıştırın
CMD ["/usr/bin/shiny-server"]
```

#### Docker ile Çalıştırma:

```bash
# Image'ı build edin
docker build -t gebip-dashboard .

# Container'ı çalıştırın
docker run -p 3838:3838 gebip-dashboard
```

### 4. RStudio Connect (Ticari)

Kurumsal kullanım için RStudio Connect kullanabilirsiniz:
- Gelişmiş güvenlik özellikleri
- Kullanıcı yönetimi
- Zamanlanmış raporlar
- Daha fazla bilgi: https://www.rstudio.com/products/connect/

## Veri Dosyası

Uygulama, `../data/gebip_scholar_final.csv` dosyasını okur. Bu dosyanın mevcut olduğundan emin olun.

## Sorun Giderme

### "Paket bulunamadı" Hatası

```r
# Eksik paketleri yükleyin
install.packages(c("shiny", "plotly", "DT", "dplyr", "tidyr", "readr", "stringr", "scales"))
```

### "Veri dosyası bulunamadı" Hatası

- `data/gebip_scholar_final.csv` dosyasının doğru konumda olduğundan emin olun
- `app.R` dosyasındaki veri yolunu kontrol edin

### Türkçe Karakter Sorunları

- CSV dosyasının UTF-8 encoding ile kaydedildiğinden emin olun
- R'de:
```r
Sys.setlocale("LC_ALL", "Turkish")
```

### shinyapps.io'ya Deploy Hatası

- Tüm gerekli paketlerin yüklendiğinden emin olun
- `rsconnect` paketinin güncel olduğunu kontrol edin
- Veri dosyasının uygulama klasöründe olduğundan emin olun

## Performans İpuçları

1. **Veri Önbellekleme**: Büyük veri setleri için `reactiveFileReader()` kullanın
2. **Plotly Optimizasyonu**: Çok fazla nokta varsa örnekleme yapın
3. **Lazy Loading**: Sekmeleri lazy loading ile yükleyin

## Özelleştirme

### Tema Değiştirme

`ui.R` içinde:
```r
library(shinythemes)
fluidPage(
  theme = shinytheme("flatly"),  # veya "cerulean", "cosmo", vb.
  ...
)
```

### Renk Şeması

`www/custom.css` dosyasını düzenleyerek renkleri özelleştirebilirsiniz.

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## İletişim

Sorularınız için: atakanekiz@iyte.edu.tr

📷 @dr_atakan_ekiz | @ekizlab

## Güncellemeler

- **v1.0.0** (Ocak 2026): İlk sürüm
  - 6 ana sekme
  - Interaktif görselleştirmeler
  - Araştırmacı profilleri
  - Veri indirme özellikleri
