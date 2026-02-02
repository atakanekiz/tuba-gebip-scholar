# Quick Start Guide - TÜBA GEBİP Shiny Dashboard

## 🚀 Hızlı Başlangıç (5 Dakika)

### Adım 1: R'yi Kontrol Edin

Terminalden veya R konsolundan:
```r
R.version.string
```

R 4.0 veya üzeri olmalı. Değilse https://cran.r-project.org/ adresinden güncelleyin.

### Adım 2: Paketleri Yükleyin

R konsolunda veya RStudio'da:
```r
source("install_packages.R")
```

Bu script tüm gerekli paketleri otomatik olarak yükleyecektir.

### Adım 3: Uygulamayı Çalıştırın

#### RStudio Kullanıyorsanız:
1. `app.R` dosyasını açın
2. Sağ üst köşedeki **"Run App"** butonuna tıklayın
3. Uygulama otomatik olarak tarayıcınızda açılacaktır

#### R Konsolu Kullanıyorsanız:
```r
setwd("path/to/tuba_odulleri_scholar/shiny_app")
shiny::runApp()
```

#### Komut Satırından:
```bash
cd path/to/tuba_odulleri_scholar/shiny_app
Rscript -e "shiny::runApp()"
```

---

## 🌐 Web Sitenize Deploy Etme

### Seçenek 1: shinyapps.io (Ücretsiz, En Kolay)

#### 1. Hesap Oluşturun
- https://www.shinyapps.io/ adresine gidin
- "Sign Up" ile ücretsiz hesap oluşturun

#### 2. Token'ınızı Alın
- Hesabınıza giriş yapın
- Account > Tokens sayfasına gidin
- "Show" butonuna tıklayın
- "Show Secret" butonuna tıklayın
- Tüm kodu kopyalayın

#### 3. R'de Token'ı Ayarlayın
```r
# rsconnect paketini yükleyin
install.packages("rsconnect")

# Token'ınızı yapıştırın (shinyapps.io'dan kopyaladığınız kod)
rsconnect::setAccountInfo(
  name="<ACCOUNT_NAME>",
  token="<TOKEN>",
  secret="<SECRET>"
)
```

#### 4. Deploy Edin
```r
# shiny_app dizininde
setwd("path/to/tuba_odulleri_scholar/shiny_app")
rsconnect::deployApp()
```

#### 5. Web Sitenize Embed Edin
Deploy tamamlandıktan sonra size bir URL verilecek:
`https://<ACCOUNT_NAME>.shinyapps.io/<APP_NAME>/`

HTML sitenize eklemek için:
```html
<iframe 
  src="https://<ACCOUNT_NAME>.shinyapps.io/<APP_NAME>/" 
  width="100%" 
  height="900px" 
  style="border: none; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
</iframe>
```

### Seçenek 2: Kendi Sunucunuzda (Shiny Server)

Ubuntu/Debian için:

```bash
# 1. R'yi kurun
sudo apt-get update
sudo apt-get install -y r-base

# 2. Shiny paketini kurun
sudo su - -c "R -e \"install.packages('shiny', repos='https://cran.rstudio.com/')\""

# 3. Shiny Server'ı indirin
wget https://download3.rstudio.org/ubuntu-18.04/x86_64/shiny-server-1.5.20.1002-amd64.deb

# 4. Shiny Server'ı kurun
sudo gdebi shiny-server-1.5.20.1002-amd64.deb

# 5. Uygulamanızı kopyalayın
sudo mkdir -p /srv/shiny-server/gebip
sudo cp -R /path/to/shiny_app/* /srv/shiny-server/gebip/
sudo cp -R /path/to/data /srv/shiny-server/

# 6. İzinleri ayarlayın
sudo chown -R shiny:shiny /srv/shiny-server/gebip
sudo chmod -R 755 /srv/shiny-server/gebip

# 7. Shiny Server'ı başlatın
sudo systemctl start shiny-server
sudo systemctl enable shiny-server
```

Uygulama şu adreste erişilebilir olacak:
`http://your-server-ip:3838/gebip/`

---

## 🔧 Sorun Giderme

### Uygulama Açılmıyor

**Hata**: "Error in file(con, "r") : cannot open the connection"

**Çözüm**: Veri dosyasının doğru konumda olduğundan emin olun:
```r
# app.R içinde veri yolunu kontrol edin
# Gerekirse mutlak yol kullanın
df <- read_csv("C:/path/to/data/gebip_scholar_final.csv")
```

### Türkçe Karakterler Bozuk

**Çözüm**: R konsolunda:
```r
Sys.setlocale("LC_ALL", "Turkish")
```

### Paket Yükleme Hatası

**Çözüm**: CRAN mirror'ını değiştirin:
```r
options(repos = c(CRAN = "https://cloud.r-project.org/"))
install.packages("paket_adi")
```

### shinyapps.io Deploy Hatası

**Hata**: "Error: Unhandled Exception: Child Task xxxxxx failed"

**Çözüm**:
1. Tüm paketlerin güncel olduğundan emin olun
2. Veri dosyasının uygulama klasöründe olduğunu kontrol edin
3. Deploy loglarını kontrol edin:
```r
rsconnect::showLogs()
```

---

## 📊 Kullanım İpuçları

### 1. Keşif Aracı
- X ve Y eksenlerini değiştirerek farklı ilişkileri keşfedin
- Renklendirme ile grupları ayırt edin
- Boyutlandırma ile üçüncü bir değişken ekleyin
- Filtreleri kullanarak belirli yıl aralıklarına odaklanın

### 2. Araştırmacı Profili
- Dropdown menüden araştırmacı seçin
- Zaman serisi grafiklerinde ödül yılı işaretlidir
- Google Scholar profiline doğrudan link vardır

### 3. Veri Tablosu
- Arama kutusunu kullanarak hızlıca filtreleyin
- Sütun başlıklarına tıklayarak sıralayın
- Filtrelenmiş veriyi CSV olarak indirin

---

## 🎨 Özelleştirme

### Renk Şemasını Değiştirme

`www/custom.css` dosyasını düzenleyin:
```css
/* Ana renk */
.metric-card {
  background: linear-gradient(135deg, #YOUR_COLOR1 0%, #YOUR_COLOR2 100%);
}

/* Link rengi */
a {
  color: #YOUR_COLOR;
}
```

### Logo Ekleme

`app.R` içinde titlePanel'e logo ekleyin:
```r
titlePanel(
  div(
    img(src = "logo.png", height = "50px"),
    "TÜBA GEBİP Akademik Performans Keşif Aracı"
  )
)
```

Logo dosyasını `www/` klasörüne koyun.

---

## 📞 Destek

Sorularınız için:
- Email: atakanekiz@iyte.edu.tr
- Twitter: @dr_atakan_ekiz

---

## ✅ Checklist

Deployment öncesi kontrol listesi:

- [ ] R 4.0+ yüklü
- [ ] Tüm paketler yüklü (`install_packages.R` çalıştırıldı)
- [ ] Uygulama yerel olarak çalışıyor
- [ ] Veri dosyası doğru konumda
- [ ] Türkçe karakterler düzgün görünüyor
- [ ] shinyapps.io hesabı oluşturuldu (eğer kullanılacaksa)
- [ ] Token ayarlandı
- [ ] Deploy başarılı
- [ ] Web sitesinde iframe testi yapıldı

---

Başarılar! 🎉
