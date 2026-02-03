import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

# Sayfa yapılandırması
st.set_page_config(page_title="TÜBA GEBİP Akademik Performans Keşif Aracı", layout="wide", page_icon="📊")

st.title("📊 TÜBA GEBİP Akademik Performans Keşif Aracı")
st.markdown("TÜBA GEBİP ödül sahiplerinin akademik metriklerini keşfedin. Görselleştirmeyi yapılandırmak için yan paneli kullanın.")

# Veri yükleme
@st.cache_data
def load_data():
    df = pd.read_csv("data/gebip_scholar_final.csv")
    # Sayısal sütunları garantiye al
    numeric_cols = ['yili', 'toplam_atif', 'h_indeksi', 'i10_indeksi', 
                    'toplam_yayin', 'odul_aninda_atif', 'odul_aninda_yayin']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("Veri dosyası 'data/gebip_scholar_final.csv' bulunamadı.")
    st.stop()

# --- Sekmeler ---
tab1, tab3, tab2, tab4, tab5, tab6 = st.tabs(["📈 Keşif Aracı", "📊 Özet İstatistikler", "👤 Araştırmacı Profili", "🏆 Ödül Anı Analizi", "📋 Veri Tablosu", "ℹ️ Hakkında"])

with tab1:
    # --- Kenar Çubuğu Kontrolleri ---
    st.sidebar.header("🎨 Görselleştirme Ayarları")

    # Eksen Seçimi
    st.sidebar.subheader("Eksenler")
    axis_options = {
        "Ödül Yılı": "yili",
        "Toplam Atıf": "toplam_atif",
        "H-İndeksi": "h_indeksi",
        "i10-İndeksi": "i10_indeksi",
        "Toplam Yayın": "toplam_yayin",
        "Ödül Anında Atıf": "odul_aninda_atif",
        "Ödül Anında Yayın": "odul_aninda_yayin"
    }
    
    x_axis_label = st.sidebar.selectbox("X Ekseni", options=list(axis_options.keys()), index=0)
    y_axis_label = st.sidebar.selectbox("Y Ekseni", options=list(axis_options.keys()), index=1)
    
    # Logaritmik Ölçek Seçeneği
    log_y = st.sidebar.checkbox("Logaritmik Y Ekseni", value=True)
    
    x_col = axis_options[x_axis_label]
    y_col = axis_options[y_axis_label]

    # Görsel Kodlama
    st.sidebar.subheader("🎨 Stil")
    
    # Renk
    color_options = {
        "Hiçbiri": None, 
        "Genel Alan": "genel_alan", 
        "Detaylı Alan": "alan", 
        "Kurum": "calistigi_kurum", 
        "Ödül Yılı": "yili"
    }
    color_label = st.sidebar.selectbox("Renklendir", options=list(color_options.keys()), index=1)
    color_col = color_options[color_label]

    # Vurgulama
    st.sidebar.subheader("✨ Vurgulama")
    all_researchers_sorted = sorted(df['adi_soyadi'].dropna().unique().tolist())
    highlight_options = ["Hiçbiri"] + all_researchers_sorted
    
    highlight_researcher = st.sidebar.selectbox(
        "Araştırmacı Vurgula", 
        options=highlight_options,
        index=0
    )
    


    # Filtreleme
    st.sidebar.subheader("🔍 Filtreler")
    
    # Yıl filtresi
    min_year = int(df['yili'].min())
    max_year = int(df['yili'].max())
    selected_years = st.sidebar.slider("Yıl Aralığı", min_year, max_year, (min_year, max_year))
    
    # Alan filtresi
    # Alan filtresi
    all_fields = sorted(df['genel_alan'].dropna().unique().tolist())
    
    # Session state initialization for multiselect
    if "selected_fields_key" not in st.session_state:
        st.session_state.selected_fields_key = all_fields

    def select_all_fields():
        st.session_state.selected_fields_key = all_fields

    def deselect_all_fields():
        st.session_state.selected_fields_key = []

    col_btn1, col_btn2 = st.sidebar.columns(2)
    col_btn1.button("Tümünü Seç", on_click=select_all_fields)
    col_btn2.button("Temizle", on_click=deselect_all_fields)

    selected_fields = st.sidebar.multiselect("Genel Alana Göre Filtrele", options=all_fields, key="selected_fields_key")
    
    # Scholar ID filtresi (sadece ID'si olanlar)
    only_with_id = st.sidebar.checkbox("Sadece Scholar ID'si Olanlar", value=True)

    # Filtreleri Uygula
    df_plot = df[
        (df['yili'] >= selected_years[0]) & 
        (df['yili'] <= selected_years[1]) &
        (df['genel_alan'].isin(selected_fields))
    ]
    
    if only_with_id:
        df_plot = df_plot[df_plot['scholar_id'] != 'no id found']
    
    # İstatistikler için filtrelenmiş veriyi sakla (Axis NA filtresinden önce)
    df_filtered_stats = df_plot.copy()

    df_plot = df_plot.dropna(subset=[x_col, y_col])

    st.sidebar.markdown("---")
    st.sidebar.subheader("📐 Görünüm Ayarları")
    
    # Boyut (Alta taşındı)
    size_options = {
        "Hiçbiri": None, 
        "H-İndeksi": "h_indeksi", 
        "Toplam Atıf": "toplam_atif", 
        "Toplam Yayın": "toplam_yayin"
    }
    size_label = st.sidebar.selectbox("Boyutlandır", options=list(size_options.keys()), index=1)
    size_col = size_options[size_label]
    
    opacity = st.sidebar.slider("Nokta Opaklığı", 0.1, 1.0, 0.7)

    # --- Çizim ---
    if df_plot.empty:
        st.warning("⚠️ Seçilen filtreler için veri bulunmuyor.")
    else:
        # Hover verisi
        hover_data = {
            'adi_soyadi': True, 
            'calistigi_kurum': True, 
            'alan': True,
            'genel_alan': True,
            'yili': True,
            'h_indeksi': True,
            'toplam_atif': True,
            'toplam_yayin': True
        }
        
        # Sütun isimlerini Türkçeleştirme haritası
        labels_map = {
            'yili': 'Ödül Yılı',
            'toplam_atif': 'Toplam Atıf',
            'h_indeksi': 'H-İndeksi',
            'i10_indeksi': 'i10-İndeksi',
            'toplam_yayin': 'Toplam Yayın',
            'odul_aninda_atif': 'Ödül Anında Atıf',
            'odul_aninda_yayin': 'Ödül Anında Yayın',
            'genel_alan': 'Genel Alan',
            'alan': 'Alan',
            'calistigi_kurum': 'Kurum',
            'adi_soyadi': 'Adı Soyadı'
        }

        fig = px.scatter(
            df_plot,
            x=x_col,
            y=y_col,
            color=color_col,
            size=size_col,
            size_max=25,
            opacity=opacity,

            log_y=log_y,
            hover_name="adi_soyadi",
            hover_data=hover_data,
            title=f"{y_axis_label} vs. {x_axis_label}",
            labels=labels_map,
            height=650
        )

        # Vurgulanan araştırmacıyı ekle
        if highlight_researcher and highlight_researcher != "Hiçbiri":
            highlighted_data = df_plot[df_plot['adi_soyadi'] == highlight_researcher]
            if not highlighted_data.empty:
                # Siyah çember içine al (Annotation symbol replacement)
                fig.add_trace(
                    go.Scatter(
                        x=highlighted_data[x_col],
                        y=highlighted_data[y_col],
                        mode='markers',
                        marker=dict(
                            color='black',
                            size=18,
                            symbol='circle-open', 
                            line=dict(width=3, color='black')
                        ),
                        name="Vurgulanan",
                        hoverinfo='skip',
                        showlegend=False
                    )
                )
                
                # Başlığa ismi ekle (Formatlı)
                fig.update_layout(
                    title={
                        'text': f"{y_axis_label} vs. {x_axis_label}<br><span style='font-size: 75%; color: gray;'>({highlight_researcher} siyah çember ile işaretlenmiştir)</span>",
                        'y': 0.95,
                        'x': 0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'
                    }
                )

        
        fig.update_layout(
            font=dict(size=12),
            title_font_size=18
        )
        


        st.plotly_chart(fig, use_container_width=True)
        
        # Metrikleri göster
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Toplam Araştırmacı", len(df_plot))
        with col2:
            st.metric("Ortalama H-İndeksi", f"{df_plot['h_indeksi'].mean():.1f}")
        with col3:
            st.metric("Ortalama Toplam Atıf", f"{df_plot['toplam_atif'].mean():.0f}")
        with col4:
            st.metric("Ortalama Toplam Yayın", f"{df_plot['toplam_yayin'].mean():.0f}")
        


with tab2:
    st.header("👤 Araştırmacı Profili")
    st.markdown("Bireysel araştırmacıların detaylı akademik profillerini inceleyin.")
    
    # Sadece ID'si olanları listele
    df_with_id = df[df['scholar_id'] != 'no id found'].copy()
    
    # Araştırmacı seçimi
    researcher_names = sorted(df_with_id['adi_soyadi'].tolist())
    selected_researcher = st.selectbox(
        "🔍 Araştırmacı Seçin",
        options=researcher_names,
        index=0 if researcher_names else None
    )
    
    if selected_researcher:
        # Seçilen araştırmacının verilerini al
        researcher_data = df_with_id[df_with_id['adi_soyadi'] == selected_researcher].iloc[0]
        
        # Profil Başlığı
        st.markdown(f"## {researcher_data['adi_soyadi']}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"**🏛️ Kurum:** {researcher_data['calistigi_kurum'] if pd.notna(researcher_data['calistigi_kurum']) else 'N/A'}")
            st.markdown(f"**🔬 Alan:** {researcher_data['genel_alan'] if pd.notna(researcher_data['genel_alan']) else 'N/A'}")
        with col2:
            st.markdown(f"**🏆 Ödül Yılı:** {int(researcher_data['yili']) if pd.notna(researcher_data['yili']) else 'N/A'}")
            st.markdown(f"**📚 Detaylı Alan:** {researcher_data['alan'] if pd.notna(researcher_data['alan']) else 'N/A'}")
        with col3:
            if pd.notna(researcher_data['scholar_id']) and researcher_data['scholar_id'] != 'no id found':
                scholar_url = f"https://scholar.google.com/citations?user={researcher_data['scholar_id']}"
                st.markdown(f"**🔗 [Google Scholar Profili]({scholar_url})**")
        
        st.markdown("---")
        
        # Temel Metrikler
        st.subheader("📊 Temel Akademik Metrikler")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                "H-İndeksi",
                f"{int(researcher_data['h_indeksi'])}" if pd.notna(researcher_data['h_indeksi']) else "N/A",
                help="Araştırmacının h-indeksi"
            )
        
        with col2:
            st.metric(
                "i10-İndeksi",
                f"{int(researcher_data['i10_indeksi'])}" if pd.notna(researcher_data['i10_indeksi']) else "N/A",
                help="En az 10 atıf alan yayın sayısı"
            )
        
        with col3:
            st.metric(
                "Toplam Atıf",
                f"{int(researcher_data['toplam_atif']):,}" if pd.notna(researcher_data['toplam_atif']) else "N/A",
                help="Toplam alınan atıf sayısı"
            )
        
        with col4:
            st.metric(
                "Toplam Yayın",
                f"{int(researcher_data['toplam_yayin'])}" if pd.notna(researcher_data['toplam_yayin']) else "N/A",
                help="Toplam yayın sayısı"
            )
        
        with col5:
            # Atıf/Yayın oranı hesapla
            if pd.notna(researcher_data['toplam_yayin']) and researcher_data['toplam_yayin'] > 0:
                cit_per_pub = researcher_data['toplam_atif'] / researcher_data['toplam_yayin']
                st.metric(
                    "Atıf/Yayın",
                    f"{cit_per_pub:.1f}",
                    help="Yayın başına ortalama atıf"
                )
            else:
                st.metric("Atıf/Yayın", "N/A")
        
        st.markdown("---")
        
        # Ödül Anı Karşılaştırması
        st.subheader("🏆 Ödül Anı vs Güncel Performans")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Atıf karşılaştırması
            award_cit = researcher_data['odul_aninda_atif'] if pd.notna(researcher_data['odul_aninda_atif']) else 0
            current_cit = researcher_data['toplam_atif'] if pd.notna(researcher_data['toplam_atif']) else 0
            cit_growth = current_cit - award_cit
            cit_growth_pct = (cit_growth / award_cit * 100) if award_cit > 0 else 0
            
            st.metric(
                "Atıf Artışı",
                f"{int(cit_growth):,}",
                f"{cit_growth_pct:.1f}% artış",
                help=f"Ödül anı: {int(award_cit):,} → Güncel: {int(current_cit):,}"
            )
            
            # Atıf bar chart
            fig_cit = go.Figure(data=[
                go.Bar(name='Ödül Anı', x=['Atıf'], y=[award_cit], marker_color='lightblue'),
                go.Bar(name='Güncel', x=['Atıf'], y=[current_cit], marker_color='darkblue')
            ])
            fig_cit.update_layout(
                title="Atıf Karşılaştırması",
                barmode='group',
                height=300,
                showlegend=True
            )
            st.plotly_chart(fig_cit, use_container_width=True)
        
        with col2:
            # Yayın karşılaştırması
            award_pub = researcher_data['odul_aninda_yayin'] if pd.notna(researcher_data['odul_aninda_yayin']) else 0
            current_pub = researcher_data['toplam_yayin'] if pd.notna(researcher_data['toplam_yayin']) else 0
            pub_growth = current_pub - award_pub
            pub_growth_pct = (pub_growth / award_pub * 100) if award_pub > 0 else 0
            
            st.metric(
                "Yayın Artışı",
                f"{int(pub_growth)}",
                f"{pub_growth_pct:.1f}% artış",
                help=f"Ödül anı: {int(award_pub)} → Güncel: {int(current_pub)}"
            )
            
            # Yayın bar chart
            fig_pub = go.Figure(data=[
                go.Bar(name='Ödül Anı', x=['Yayın'], y=[award_pub], marker_color='lightgreen'),
                go.Bar(name='Güncel', x=['Yayın'], y=[current_pub], marker_color='darkgreen')
            ])
            fig_pub.update_layout(
                title="Yayın Karşılaştırması",
                barmode='group',
                height=300,
                showlegend=True
            )
            st.plotly_chart(fig_pub, use_container_width=True)
        
        st.markdown("---")
        
        # Zaman Serisi Grafikleri
        st.subheader("📈 Zaman İçinde Gelişim")
        
        # Log scale toggle
        use_log_scale = st.checkbox("📊 Logaritmik Ölçek Kullan (Y-ekseni)", value=True, help="Büyük değer aralıkları için logaritmik ölçek kullanın")
        
        col1, col2 = st.columns(2)
        
        # Yıllık atıf verilerini parse et
        def parse_yearly_data(data_str):
            if pd.isna(data_str) or data_str == '':
                return {}, []
            
            data_dict = {}
            pairs = str(data_str).split('|')
            for pair in pairs:
                pair = pair.strip()
                if ':' in pair:
                    year, count = pair.split(':')
                    try:
                        data_dict[int(year.strip())] = int(count.strip())
                    except ValueError:
                        continue
            
            if data_dict:
                years = sorted(data_dict.keys())
                cumulative = []
                total = 0
                for year in years:
                    total += data_dict[year]
                    cumulative.append(total)
                return data_dict, list(zip(years, cumulative))
            return {}, []
        
        with col1:
            # Atıf zaman serisi
            cit_data, cit_cumulative = parse_yearly_data(researcher_data['yillik_atif'])
            
            if cit_cumulative:
                years, cumulative_cits = zip(*cit_cumulative)
                
                fig_cit_time = go.Figure()
                fig_cit_time.add_trace(go.Scatter(
                    x=years,
                    y=cumulative_cits,
                    mode='lines+markers',
                    name='Kümülatif Atıf',
                    line=dict(color='blue', width=2),
                    marker=dict(size=6)
                ))
                
                # Ödül yılı çizgisi
                if pd.notna(researcher_data['yili']):
                    award_year = int(researcher_data['yili'])
                    fig_cit_time.add_vline(
                        x=award_year,
                        line_dash="dash",
                        line_color="red",
                        annotation_text="Ödül Yılı",
                        annotation_position="top"
                    )
                
                fig_cit_time.update_layout(
                    title="Kümülatif Atıf Sayısı",
                    xaxis_title="Yıl",
                    yaxis_title="Kümülatif Atıf",
                    yaxis_type="log" if use_log_scale else "linear",
                    height=400,
                    xaxis=dict(title=dict(font=dict(size=14)), tickfont=dict(size=12)),
                    yaxis=dict(title=dict(font=dict(size=14)), tickfont=dict(size=12))
                )
                st.plotly_chart(fig_cit_time, use_container_width=True)
            else:
                st.info("Yıllık atıf verisi mevcut değil")
        
        with col2:
            # Yayın zaman serisi
            pub_data, pub_cumulative = parse_yearly_data(researcher_data['yillik_yayin'])
            
            if pub_cumulative:
                years, cumulative_pubs = zip(*pub_cumulative)
                
                fig_pub_time = go.Figure()
                fig_pub_time.add_trace(go.Scatter(
                    x=years,
                    y=cumulative_pubs,
                    mode='lines+markers',
                    name='Kümülatif Yayın',
                    line=dict(color='green', width=2),
                    marker=dict(size=6)
                ))
                
                # Ödül yılı çizgisi
                if pd.notna(researcher_data['yili']):
                    award_year = int(researcher_data['yili'])
                    fig_pub_time.add_vline(
                        x=award_year,
                        line_dash="dash",
                        line_color="red",
                        annotation_text="Ödül Yılı",
                        annotation_position="top"
                    )
                
                fig_pub_time.update_layout(
                    title="Kümülatif Yayın Sayısı",
                    xaxis_title="Yıl",
                    yaxis_title="Kümülatif Yayın",
                    yaxis_type="log" if use_log_scale else "linear",
                    height=400,
                    xaxis=dict(title=dict(font=dict(size=14)), tickfont=dict(size=12)),
                    yaxis=dict(title=dict(font=dict(size=14)), tickfont=dict(size=12))
                )
                st.plotly_chart(fig_pub_time, use_container_width=True)
            else:
                st.info("Yıllık yayın verisi mevcut değil")
        
        st.markdown("---")
        
        # Alan içi karşılaştırma
        st.subheader("📊 Alan İçi Karşılaştırma")
        
        # Aynı alandaki diğer araştırmacılar
        same_field = df_with_id[df_with_id['genel_alan'] == researcher_data['genel_alan']]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # H-indeksi sıralaması
            h_rank = (same_field['h_indeksi'] > researcher_data['h_indeksi']).sum() + 1
            h_percentile = (1 - h_rank / len(same_field)) * 100
            st.metric(
                f"H-İndeksi Sıralaması ({researcher_data['genel_alan']})",
                f"{h_rank} / {len(same_field)}",
                f"Üst %{h_percentile:.0f}",
                help=f"Aynı alanda {len(same_field)} araştırmacı var"
            )
        
        with col2:
            # Atıf sıralaması
            cit_rank = (same_field['toplam_atif'] > researcher_data['toplam_atif']).sum() + 1
            cit_percentile = (1 - cit_rank / len(same_field)) * 100
            st.metric(
                f"Atıf Sıralaması ({researcher_data['genel_alan']})",
                f"{cit_rank} / {len(same_field)}",
                f"Üst %{cit_percentile:.0f}"
            )
        
        with col3:
            # Yayın sıralaması
            pub_rank = (same_field['toplam_yayin'] > researcher_data['toplam_yayin']).sum() + 1
            pub_percentile = (1 - pub_rank / len(same_field)) * 100
            st.metric(
                f"Yayın Sıralaması ({researcher_data['genel_alan']})",
                f"{pub_rank} / {len(same_field)}",
                f"Üst %{pub_percentile:.0f}"
            )
        
        # İlgi alanları
        if pd.notna(researcher_data['ilgi_alanlari']) and researcher_data['ilgi_alanlari'] != '':
            st.markdown("---")
            st.subheader("🔬 İlgi Alanları")
            st.markdown(f"_{researcher_data['ilgi_alanlari']}_")
    
    else:
        st.info("Lütfen bir araştırmacı seçin")

with tab3:
    st.header("📊 Özet İstatistikler")
    
    # Sadece ID'si olanları kullan (Filtrelenmiş veri üzerinden)
    df_stats = df_filtered_stats.copy()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏛️ En Çok Ödül Alan Kurumlar")
        inst_counts = df_stats['calistigi_kurum'].value_counts().head(15).reset_index()
        inst_counts.columns = ['Kurum', 'Sayı']
        fig_inst = px.bar(
            inst_counts, 
            x='Sayı', 
            y='Kurum', 
            orientation='h', 
            title="Ödül Sayısına Göre İlk 15 Kurum"
        )
        fig_inst.update_traces(marker_color='#1f77b4')
        fig_inst.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_inst, use_container_width=True)
        
    with col2:
        st.subheader("🔬 Alan Dağılımı")
        field_counts = df_stats['genel_alan'].value_counts().reset_index()
        field_counts.columns = ['Genel Alan', 'Sayı']
        fig_field = px.pie(
            field_counts, 
            values='Sayı', 
            names='Genel Alan', 
            title="Genel Alana Göre Ödüller",
            hole=0.3
        )
        st.plotly_chart(fig_field, use_container_width=True)
    
    # Yıllara göre dağılım
    st.subheader("📅 Yıllara Göre Ödül Dağılımı")
    year_counts = df_stats['yili'].value_counts().sort_index().reset_index()
    year_counts.columns = ['Yıl', 'Sayı']
    fig_year = px.bar(
        year_counts, 
        x='Yıl', 
        y='Sayı', 
        title="Yıllara Göre Ödül Sayısı"
    )
    fig_year.update_traces(marker_color='#1f77b4')
    st.plotly_chart(fig_year, use_container_width=True)
    
    # En yüksek metrikler
    st.subheader("🏆 En Yüksek Metrikler")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**En Yüksek H-İndeksi**")
        top_h = df_stats.nlargest(5, 'h_indeksi')[['adi_soyadi', 'h_indeksi', 'yili']]
        st.dataframe(top_h, hide_index=True)
    
    with col2:
        st.markdown("**En Çok Atıf**")
        top_cit = df_stats.nlargest(5, 'toplam_atif')[['adi_soyadi', 'toplam_atif', 'yili']]
        st.dataframe(top_cit, hide_index=True)
    
    with col3:
        st.markdown("**En Çok Yayın**")
        top_pub = df_stats.nlargest(5, 'toplam_yayin')[['adi_soyadi', 'toplam_yayin', 'yili']]
        st.dataframe(top_pub, hide_index=True)

with tab4:
    st.header("🏆 Ödül Anı Analizi")
    st.markdown("Araştırmacıların ödül aldıkları andaki akademik performanslarını inceleyin.")
    
    df_award = df[df['scholar_id'] != 'no id found'].copy()
    
    # Kontroller
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        log_x_award = st.checkbox("Logaritmik X Ekseni", value=True, key="award_log_x")
    with col_c2:
        log_y_award = st.checkbox("Logaritmik Y Ekseni", value=True, key="award_log_y")
    with col_c3:
        all_researchers_sorted = sorted(df['adi_soyadi'].dropna().unique().tolist())
        highlight_award = st.selectbox("Araştırmacı Vurgula", ["Hiçbiri"] + all_researchers_sorted, key="award_highlight")

    # Ödül anı vs şu anki karşılaştırma
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Atıf Artışı")
        df_award['atif_artisi'] = df_award['toplam_atif'] - df_award['odul_aninda_atif']
        
        fig_cit_growth = px.scatter(
            df_award,
            x='odul_aninda_atif',
            y='toplam_atif',
            color='genel_alan',
            hover_name='adi_soyadi',
            hover_data=['yili', 'h_indeksi'],
            title="Ödül Anı vs Güncel Atıf Sayısı",
            log_x=log_x_award,
            log_y=log_y_award,
            labels={
                'odul_aninda_atif': 'Ödül Anında Atıf',
                'toplam_atif': 'Güncel Toplam Atıf',
                'genel_alan': 'Genel Alan'
            }
        )
        # Diagonal line (y=x)
        max_val_cit = max(df_award['toplam_atif'].max(), df_award['odul_aninda_atif'].max())
        fig_cit_growth.add_trace(
            go.Scatter(x=[0, max_val_cit], y=[0, max_val_cit], 
                      mode='lines', name='y=x', 
                      line=dict(dash='dash', color='gray'))
        )
        
        # Vurgulama
        if highlight_award and highlight_award != "Hiçbiri":
            highlighted_data = df_award[df_award['adi_soyadi'] == highlight_award]
            if not highlighted_data.empty:
                # Siyah çember
                fig_cit_growth.add_trace(
                    go.Scatter(
                        x=highlighted_data['odul_aninda_atif'],
                        y=highlighted_data['toplam_atif'],
                        mode='markers',
                        marker=dict(color='black', size=18, symbol='circle-open', line=dict(width=3, color='black')),
                        name="Vurgulanan",
                        showlegend=False
                    )
                )
                
                # Başlığa ismi ekle (Formatlı)
                fig_cit_growth.update_layout(
                    title={
                        'text': f"Ödül Anı vs Güncel Atıf Sayısı<br><span style='font-size: 75%; color: gray;'>({highlight_award} siyah çember ile işaretlenmiştir)</span>",
                        'y': 0.95,
                        'x': 0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'
                    }
                )

        # Remove legend for the first plot
        fig_cit_growth.update_layout(showlegend=False)


        st.plotly_chart(fig_cit_growth, use_container_width=True)
    
    with col2:
        st.subheader("📚 Yayın Artışı")
        df_award['yayin_artisi'] = df_award['toplam_yayin'] - df_award['odul_aninda_yayin']
        
        fig_pub_growth = px.scatter(
            df_award,
            x='odul_aninda_yayin',
            y='toplam_yayin',
            color='genel_alan',
            hover_name='adi_soyadi',
            hover_data=['yili', 'h_indeksi'],
            title="Ödül Anı vs Güncel Yayın Sayısı",
            log_x=log_x_award,
            log_y=log_y_award,
            labels={
                'odul_aninda_yayin': 'Ödül Anında Yayın',
                'toplam_yayin': 'Güncel Toplam Yayın',
                'genel_alan': 'Genel Alan'
            }
        )
        # Diagonal line (y=x)
        max_val_pub = max(df_award['toplam_yayin'].max(), df_award['odul_aninda_yayin'].max())
        fig_pub_growth.add_trace(
            go.Scatter(x=[0, max_val_pub], y=[0, max_val_pub], 
                      mode='lines', name='y=x', 
                      line=dict(dash='dash', color='gray'))
        )

        # Vurgulama
        if highlight_award and highlight_award != "Hiçbiri":
            highlighted_data = df_award[df_award['adi_soyadi'] == highlight_award]
            if not highlighted_data.empty:
                # Siyah çember
                fig_pub_growth.add_trace(
                    go.Scatter(
                        x=highlighted_data['odul_aninda_yayin'],
                        y=highlighted_data['toplam_yayin'],
                        mode='markers',
                        marker=dict(color='black', size=18, symbol='circle-open', line=dict(width=3, color='black')),
                        name="Vurgulanan",
                        showlegend=False
                    )
                )

                # Başlığa ismi ekle (Formatlı)
                fig_pub_growth.update_layout(
                    title={
                        'text': f"Ödül Anı vs Güncel Yayın Sayısı<br><span style='font-size: 75%; color: gray;'>({highlight_award} siyah çember ile işaretlenmiştir)</span>",
                        'y': 0.95,
                        'x': 0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'
                    }
                )


        st.plotly_chart(fig_pub_growth, use_container_width=True)
    
    # En çok büyüyenler
    st.subheader("🚀 En Hızlı Büyüyen Araştırmacılar")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Atıf Artışı (Mutlak)**")
        top_growth_cit = df_award.nlargest(10, 'atif_artisi')[['adi_soyadi', 'odul_aninda_atif', 'toplam_atif', 'atif_artisi', 'yili']]
        st.dataframe(top_growth_cit, hide_index=True)
    
    with col2:
        st.markdown("**Yayın Artışı (Mutlak)**")
        top_growth_pub = df_award.nlargest(10, 'yayin_artisi')[['adi_soyadi', 'odul_aninda_yayin', 'toplam_yayin', 'yayin_artisi', 'yili']]
        st.dataframe(top_growth_pub, hide_index=True)

with tab5:
    st.header("📋 Veri Tablosu")
    st.markdown("Tüm veriyi inceleyin ve arayın.")
    
    # Arama kutusu
    search = st.text_input("🔍 Araştırmacı Ara (Ad, Soyad, Kurum)", "")
    
    df_display = df.copy()
    
    if search:
        df_display = df_display[
            df_display['adi_soyadi'].str.contains(search, case=False, na=False) |
            df_display['calistigi_kurum'].str.contains(search, case=False, na=False)
        ]
    
    # Sütun seçimi
    all_cols = df_display.columns.tolist()
    default_cols = ['adi_soyadi', 'yili', 'alan', 'genel_alan', 'calistigi_kurum', 
                   'h_indeksi', 'toplam_atif', 'toplam_yayin', 
                   'odul_aninda_atif', 'odul_aninda_yayin']
    selected_cols = st.multiselect("Gösterilecek Sütunlar", options=all_cols, default=default_cols)
    
    if selected_cols:
        st.dataframe(df_display[selected_cols], use_container_width=True, height=600)
    else:
        st.dataframe(df_display, use_container_width=True, height=600)
    


# Tab 6: Hakkında (About)
with tab6:
    st.header("ℹ️ Veri Toplama Metodolojisi ve Açıklamalar")
    
    st.markdown("""
    ### 📚 Veri Nasıl Toplandı?
    
    Bu gösterge panelinde sunulan veriler, **Ocak 2026** tarihinde **Google Scholar** platformundan 
    kamuya açık olarak erişilebilen bilgiler kullanılarak toplanmıştır.
    
    #### Veri Toplama Süreci:
    
    1. **Araştırmacı Eşleştirme**: TÜBA GEBİP ödül sahiplerinin isimleri kullanılarak Google Scholar'da 
       profil araması yapılmıştır. İsim varyasyonları ve kurum bilgileri dikkate alınarak en uygun 
       profiller belirlenmiştir.
    
    2. **Metrik Çıkarımı**: Her araştırmacı için Google Scholar profilinden aşağıdaki metrikler çıkarılmıştır:
       - Toplam atıf sayısı
       - H-indeksi
       - i10-indeksi
       - Toplam yayın sayısı
       - Yıllık atıf ve yayın dağılımları
       - Ödül yılındaki atıf ve yayın sayıları (GoogleScholar veritabanında ödül yılına kadar olan verinin bulunması durumunda)
    
    3. **Eşleşme Doğrulaması**: Profil eşleştirmelerinin doğruluğunu sağlamak için en iyi çaba 
       gösterilmiştir, ancak bazı durumlarda isim benzerliği veya kurum değişiklikleri nedeniyle 
       eşleşme zorlukları yaşanmış olabilir.
    
    ---
    
    ### 📖 "Yayın" Tanımı
    
    Bu gösterge panelinde **"yayın"** terimi, **Google Scholar'ın tanımladığı tüm akademik çıktıları** 
    kapsamaktadır. Google Scholar, çeşitli kaynaklardan gelen akademik içerikleri indeksler ve bunlar 
    arasında şunlar bulunur:
    
    - 📄 Hakemli dergi makaleleri
    - 📘 Kitap ve kitap bölümleri
    - 🎓 Doktora ve yüksek lisans tezleri
    - 📝 Konferans bildirileri (proceedings)
    - 📊 Teknik raporlar
    - 🔬 Ön baskılar (preprints)
    - 💡 Patentler
    - 🌐 Diğer akademik belgeler
    
    **Önemli Not**: Bu çalışmada Google Scholar'ın yayın ve atıf tanımları olduğu gibi kullanılmıştır. 
    Farklı disiplinlerde yayın türlerinin dağılımı ve önemi değişiklik gösterebilir.
    
    ---
    
    ### 📏 Akademik Performans İndekslerinin Sınırlılıkları
    
    > **ÖNEMLİ**: Tüm akademik performans ölçüm indekslerinin önemli eksiklikleri vardır.
    
    **H-indeksi** ve **i10-indeksi** gibi metrikler, etkili araştırmacıları takip etmekte faydalı olabilir, 
    ancak **yapılan çalışmanın kalitesini veya önemini doğrudan temsil etmezler**. Bu indeksler hakkında 
    dikkat edilmesi gereken önemli noktalar:
    
    - 🕐 **Zaman Faktörü**: Bu indeksler zaman içinde birikir ve daha genç araştırmacıların doğal olarak 
      kıdemli araştırmacılara göre daha düşük indekslere sahip olması beklenir
    
    - 🎯 **Kalite vs. Miktar**: Yüksek atıf sayısı, çalışmanın bilimsel kalitesinin veya toplumsal 
      etkisinin tek göstergesi değildir
    
    - 🔬 **Disiplin Farklılıkları**: Farklı alanlarda atıf pratikleri büyük ölçüde değişir; bazı 
      alanlarda daha az atıf yapılması normaldir
    
    - 💡 **Yenilikçi Çalışmalar**: Çığır açan veya çok yenilikçi çalışmalar, anlaşılması ve kabul 
      görmesi zaman aldığı için başlangıçta düşük atıf alabilir
    
    - 📊 **Tek Başına Yetersiz**: Bu metrikler, araştırmacının bilimsel katkısını değerlendirmede 
      **tek başına kullanılmamalı**, diğer nitel ve nicel göstergelerle birlikte ele alınmalıdır
    
    ---
    
    ### ⚠️ Sorumluluk Reddi ve Sınırlamalar
    
    > **DİKKAT**: Bu veriler **"olduğu gibi" (as-is)** sunulmaktadır ve aşağıdaki sınırlamaları içerebilir:
    
    #### Veri Kaynağı Sınırlamaları:
    - ✅ Veriler **Google Scholar'ın kamuya açık verileri** kullanılarak toplanmıştır
    - 📅 Veriler **Ocak 2026** tarihinde toplanmıştır ve güncel olmayabilir
    - 🔄 Google Scholar verileri sürekli güncellenmektedir; bu nedenle mevcut değerler farklılık gösterebilir
    - 📊 Google Scholar'ın indeksleme politikaları ve kapsamı disiplinler arası farklılık gösterebilir
    
    #### Eşleşme ve Doğruluk:
    - 🎯 Araştırmacı isimleri ile Google Scholar profilleri arasında **en iyi çaba ile eşleştirme** yapılmıştır
    - ⚠️ İsim benzerliği, evlilik sonrası soyad değişiklikleri veya aynı isimli farklı araştırmacılar 
      nedeniyle hatalı eşleşmeler olabilir
    - 🏛️ Kurum değişiklikleri ve farklı kurum adı yazılımları eşleştirme zorluklarına yol açabilir
    - ❌ **Veri doğruluğu garanti edilmemektedir**
    
    #### Kullanım Uyarıları:
    - 📌 Bu veriler **bilgilendirme amaçlıdır** ve resmi değerlendirmelerde tek başına kullanılmamalıdır
    - 🔬 Farklı disiplinlerde atıf ve yayın pratikleri büyük farklılıklar gösterir
    - 📈 Metriklerin yorumlanmasında disiplin özellikleri, kariyer aşaması ve araştırma alanı dikkate alınmalıdır
    - 🤝 Şüpheli veya hatalı görünen veriler için ilgili araştırmacının Google Scholar profilinin 
      manuel olarak kontrol edilmesi önerilir
    
    ---
    
    ### 📧 İletişim ve Geri Bildirim
    
    Bu araç, TÜBA GEBİP ödül sahiplerinin akademik etkisini keşfetmek için bir başlangıç noktası 
    olarak tasarlanmıştır ve sürekli iyileştirmeye açıktır. Veri hataları, eşleşme sorunları veya önerileriniz için lütfen iletişime geçiniz: 
    **atakanekiz@iyte.edu.tr**
    
    📷 **[@dr_atakan_ekiz](https://www.instagram.com/dr_atakan_ekiz/)** 

    📷 **[@ekizlab](https://www.instagram.com/ekizlab/)**
    
    **www.atakanekiz.com**
    
    ---
    
    **Son Güncelleme**: Ocak 2026  
    **Veri Kaynağı**: Google Scholar (Kamuya Açık Veriler)
    """)

# Footer
st.markdown("---")
st.markdown("📊 **TÜBA GEBİP Akademik Performans Keşif Aracı** | Veri Kaynağı: Google Scholar")
