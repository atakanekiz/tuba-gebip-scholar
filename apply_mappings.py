
import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Load the dataset
file_path = r'data/gebip_scholar_final.csv'
df = pd.read_csv(file_path)

# Mappings based on suggestions and analysis
mappings = {
    # Existing Categories
    'Uluslararası İlişkiler': 'Siyaset Bilimi ve Uluslararası İlişkiler',
    'İnşaat Mühendisliği': 'İnşaat Mühendisliği',
    'İşletme': 'İktisat ve İşletme',
    'İktisat': 'İktisat ve İşletme',
    'Bankacılık Ve İşletme': 'İktisat ve İşletme',
    'Ekonometri': 'İktisat ve İşletme',
    'İşletme/Örgütsel Davranış': 'İktisat ve İşletme',
    'Finans': 'İktisat ve İşletme',
    'Pazarlama': 'İktisat ve İşletme',
    
    'Şehir ve Bölge Planlama': 'Mimarlık ve Şehir Planlama',
    
    'İklim Değişikliği, Deniz Kirliliği': 'Çevre Bilimleri ve Mühendisliği',
    'Deniz Bilimleri': 'Çevre Bilimleri ve Mühendisliği',
    
    'Uzay Bilimleri': 'Fizik ve Astronomi',
    'Yoğun Madde Fiziği': 'Fizik ve Astronomi',
    
    # Health / Biology related
    'Biyomedikal Mühendisliği': 'Tıp ve Sağlık Bilimleri',
    'Biyoedikal Mühendisliği': 'Tıp ve Sağlık Bilimleri',
    'Çocuk Romatolojisi': 'Tıp ve Sağlık Bilimleri',
    'İmmünoloji': 'Tıp ve Sağlık Bilimleri',
    'Göz Hastalıkları': 'Tıp ve Sağlık Bilimleri',
    'Ortopedi ve Travmatoloji': 'Tıp ve Sağlık Bilimleri',
    'Histoloji Ve Embriyoloji': 'Tıp ve Sağlık Bilimleri',
    'Histoloji ve Embriyoloji': 'Tıp ve Sağlık Bilimleri',
    'Histoloji ve Embroiyoloji': 'Tıp ve Sağlık Bilimleri',
    'Fizyoterapi ve Rehabilitasyon': 'Tıp ve Sağlık Bilimleri',
    'Tı/İç Hastalıkları': 'Tıp ve Sağlık Bilimleri',
    'Farmasotik Teknoloji': 'Tıp ve Sağlık Bilimleri',
    'Farmakognozi': 'Tıp ve Sağlık Bilimleri',
    'Eczacılık / Farmakognozi': 'Tıp ve Sağlık Bilimleri', 
    'Oral Patoloji': 'Tıp ve Sağlık Bilimleri',
    'Tıbbi Patoloji': 'Tıp ve Sağlık Bilimleri',
    
    # Social / Humanities
    'İletişim': 'Sosyal Bilimler ve Eğitim',
    'İletişim/Reklamcılık': 'Sosyal Bilimler ve Eğitim',
    'Sualtı Kültür Mirasının Korunması': 'Sosyal Bilimler ve Eğitim', 
    'Müzelerde Önleyici Koruma Çalışmaları': 'Beşeri Bilimler',
    
    # New Category
    'Endüstri Mühendisliği': 'Endüstri Mühendisliği',
    
    # Other Engineering mappings
    'Gemi İnş. ve Gemi Mak. Müh.': 'Makine Mühendisliği',
    'Gemi İnşaatı ve Denizcilik': 'Makine Mühendisliği',
    'Geomatik Mühendisliği': 'İnşaat Mühendisliği',
    'Havacılık ve Uzay Mühendisliği': 'Makine Mühendisliği',
    'İmalat Teknolojileri': 'Makine Mühendisliği',
    
    # Biology / Bioinformatics
    'Biyoenformatik': 'Biyoloji ve Yaşam Bilimleri',
    
    # 2025 Cohort Mappings
    'Kütle Çekimi Kuramları': 'Fizik ve Astronomi',
    'Elektrokimya': 'Kimya',
    'Moleküler Genetik / Epigenetik / Embriyonik Kök Hücre': 'Biyoloji ve Yaşam Bilimleri',
    'Deneysel Katı Hal Fiziği': 'Fizik ve Astronomi',
    'Biyofotonik': 'Fizik ve Astronomi',
    'Uygulamalı Matematik': 'Matematik ve İstatistik',
    'Organik Kimya': 'Kimya',
    'Hücre Kültürü ve Doku Mühendisliği': 'Biyoloji ve Yaşam Bilimleri',
    'Malzeme Tasarım ve Davranışları': 'Malzeme Bilimi ve Nanoteknoloji',
    'Katı Cisimler Mekaniği / Peridinamik / Kırılma Mekaniği': 'Makine Mühendisliği',
    'Gıda Bilimi ve Mühendisliği': 'Gıda ve Tarım Bilimleri',
    'Yöneylem Araştırması / Lojistik / Matematiksel Optimizasyon': 'Endüstri Mühendisliği',
    'Nanomalzeme Sentez Mühendisliği': 'Malzeme Bilimi ve Nanoteknoloji',
    'Metalurji ve Malzeme Mühendisliği': 'Malzeme Bilimi ve Nanoteknoloji',
    'Karşılaştırmalı Edebiyat': 'Beşeri Bilimler',
    'Gelişim Psikolojisi': 'Sosyal Bilimler ve Eğitim',
    'Bilim Tarihi': 'Beşeri Bilimler',
    'Bilişsel Psikoloji': 'Sosyal Bilimler ve Eğitim',
    'Deneysel Psikoloji': 'Sosyal Bilimler ve Eğitim',
    'Ortadoğu Tarihi / Yakınçağ Osmanlı Tarihi': 'Beşeri Bilimler',
    'Bilgisayar ve Öğretim Teknolojileri Eğitimi': 'Sosyal Bilimler ve Eğitim',
    'Analitik Kimya': 'Kimya',
    'Kardiyoloji': 'Tıp ve Sağlık Bilimleri',
    'Tıbbi Biyokimya': 'Tıp ve Sağlık Bilimleri',
    'Kanser Biyolojisi / RNA Biyolojisi': 'Biyoloji ve Yaşam Bilimleri',
    'Çocuk Sağlığı ve Hastalığı': 'Tıp ve Sağlık Bilimleri',
    'Farmasötik Toksikoloji': 'Tıp ve Sağlık Bilimleri',
}

# Apply mappings
def apply_map(row):
    if row['genel_alan'] == 'Diğer':
        # Check explicit mapping
        if row['alan'] in mappings:
            return mappings[row['alan']]
        # Additional fuzzy checks or minor cleanups
        if 'Eczacılık' in str(row['alan']):
             return 'Tıp ve Sağlık Bilimleri'
    return row['genel_alan']

original_diger_count = len(df[df['genel_alan'] == 'Diğer'])
print(f"Original 'Diger' count: {original_diger_count}")

df['genel_alan'] = df.apply(apply_map, axis=1)

new_diger_count = len(df[df['genel_alan'] == 'Diğer'])
print(f"New 'Diğer' count: {new_diger_count}")
print(f"Mapped {original_diger_count - new_diger_count} entries.")

# Save
df.to_csv(file_path, index=False)
print("Saved updated CSV.")
