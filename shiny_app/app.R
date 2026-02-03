# TÜBA GEBİP Akademik Performans Keşif Aracı - Shiny Dashboard
# Equivalent to the Streamlit dashboard

# Load required packages
library(shiny)
library(plotly)
library(DT)
library(dplyr)
library(tidyr)
library(readr)
library(stringr)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

# Parse yearly data format: "2018:10 | 2019:15 | 2020:20"
parse_yearly_data <- function(data_str) {
  if (is.na(data_str) || data_str == "") {
    return(list(data = data.frame(), cumulative = data.frame()))
  }

  pairs <- str_split(data_str, "\\|")[[1]]
  years <- c()
  counts <- c()

  for (pair in pairs) {
    pair <- str_trim(pair)
    if (str_detect(pair, ":")) {
      parts <- str_split(pair, ":")[[1]]
      year <- as.integer(str_trim(parts[1]))
      count <- as.integer(str_trim(parts[2]))
      if (!is.na(year) && !is.na(count)) {
        years <- c(years, year)
        counts <- c(counts, count)
      }
    }
  }

  if (length(years) > 0) {
    # Sort by year
    ord <- order(years)
    years <- years[ord]
    counts <- counts[ord]

    # Calculate cumulative
    cumulative <- cumsum(counts)

    return(list(
      data = data.frame(year = years, count = counts),
      cumulative = data.frame(year = years, cumulative = cumulative)
    ))
  }

  return(list(data = data.frame(), cumulative = data.frame()))
}

# ============================================================================
# DATA LOADING
# ============================================================================

# Load data with caching
load_data <- function() {
  df <- read_csv("../data/gebip_scholar_final.csv", show_col_types = FALSE)

  # Convert numeric columns
  numeric_cols <- c(
    "yili", "toplam_atif", "h_indeksi", "i10_indeksi",
    "toplam_yayin", "odul_aninda_atif", "odul_aninda_yayin"
  )

  for (col in numeric_cols) {
    if (col %in% names(df)) {
      df[[col]] <- as.numeric(df[[col]])
    }
  }

  # Clean and order genel_alan
  if ("genel_alan" %in% names(df)) {
    # Get unique values excluding NA
    fields <- sort(unique(df$genel_alan[!is.na(df$genel_alan)]))

    # Move "Diğer" to the end if it exists
    if ("Diğer" %in% fields) {
      fields <- c(fields[fields != "Diğer"], "Diğer")
    }

    # Convert to factor with specific order
    df$genel_alan <- factor(df$genel_alan, levels = fields)
  }

  return(df)
}

# Define custom color palette for genel_alan (distinct, accessible colors)
genel_alan_colors <- c(
  "Fen Bilimleri" = "#1f77b4", # Blue
  "Mühendislik" = "#ff7f0e", # Orange
  "Sağlık Bilimleri" = "#2ca02c", # Green
  "Sosyal Bilimler" = "#d62728", # Red
  "Tarım Bilimleri" = "#9467bd", # Purple
  "Veteriner" = "#8c564b", # Brown
  "Eğitim" = "#e377c2", # Pink
  "Güzel Sanatlar" = "#7f7f7f", # Gray
  "Hukuk" = "#bcbd22", # Olive
  "Diğer" = "#17becf" # Cyan
)

# ============================================================================
# UI DEFINITION
# ============================================================================

ui <- fluidPage(
  # Custom CSS
  tags$head(
    tags$link(rel = "stylesheet", type = "text/css", href = "custom.css"),
    tags$style(HTML("
      .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        text-align: center;
      }
      .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #1f77b4;
      }
      .metric-label {
        font-size: 14px;
        color: #666;
        margin-top: 5px;
      }
      .info-box {
        background-color: #e7f3ff;
        border-left: 4px solid #1f77b4;
        padding: 15px;
        margin: 15px 0;
      }
    "))
  ),

  # Title
  titlePanel("📊 TÜBA GEBİP Akademik Performans Keşif Aracı"),
  p("TÜBA GEBİP ödül sahiplerinin akademik metriklerini keşfedin. Görselleştirmeyi yapılandırmak için yan paneli kullanın."),

  # Main tabs
  tabsetPanel(
    id = "main_tabs",

    # TAB 1: Exploration Tool
    tabPanel(
      "📈 Keşif Aracı",
      sidebarLayout(
        sidebarPanel(
          width = 3,
          h4("🎨 Görselleştirme Ayarları"),
          h5("Eksenler"),
          selectInput("x_axis", "X Ekseni",
            choices = c(
              "Ödül Yılı" = "yili",
              "Toplam Atıf" = "toplam_atif",
              "H-İndeksi" = "h_indeksi",
              "i10-İndeksi" = "i10_indeksi",
              "Toplam Yayın" = "toplam_yayin",
              "Ödül Anında Atıf" = "odul_aninda_atif",
              "Ödül Anında Yayın" = "odul_aninda_yayin"
            ),
            selected = "yili"
          ),
          selectInput("y_axis", "Y Ekseni",
            choices = c(
              "Ödül Yılı" = "yili",
              "Toplam Atıf" = "toplam_atif",
              "H-İndeksi" = "h_indeksi",
              "i10-İndeksi" = "i10_indeksi",
              "Toplam Yayın" = "toplam_yayin",
              "Ödül Anında Atıf" = "odul_aninda_atif",
              "Ödül Anında Yayın" = "odul_aninda_yayin"
            ),
            selected = "toplam_atif"
          ),
          h5("📍 Vurgula"),
          uiOutput("highlight_selector_ui"),
          hr(),
          h5("🔍 Filtreler"),
          uiOutput("year_slider_ui"),
          uiOutput("field_filter_ui"),
          checkboxInput("only_with_id", "Sadece Scholar ID'si Olanlar", value = TRUE),
          hr(),
          h5("🎨 Stil"),
          selectInput("color_by", "Renklendir",
            choices = c(
              "Hiçbiri" = "none",
              "Genel Alan" = "genel_alan",
              "Detaylı Alan" = "alan",
              "Kurum" = "calistigi_kurum",
              "Ödül Yılı" = "yili"
            ),
            selected = "genel_alan"
          ),
          selectInput("size_by", "Boyutlandır",
            choices = c(
              "Hiçbiri" = "none",
              "H-İndeksi" = "h_indeksi",
              "Toplam Atıf" = "toplam_atif",
              "Toplam Yayın" = "toplam_yayin"
            ),
            selected = "h_indeksi"
          ),
          sliderInput("opacity", "Nokta Opaklığı",
            min = 0.1, max = 1.0, value = 0.7, step = 0.1
          ),
          checkboxInput("log_scale_y", "Y Ekseni Logaritmik Ölçek", value = FALSE)
        ),
        mainPanel(
          width = 9,
          plotlyOutput("exploration_plot", height = "650px"),
          br(),
          fluidRow(
            column(3, uiOutput("metric_total")),
            column(3, uiOutput("metric_h_index")),
            column(3, uiOutput("metric_citations")),
            column(3, uiOutput("metric_publications"))
          ),
          br(),
        )
      )
    ),

    # TAB 2: Summary Statistics (Swapped)
    tabPanel(
      "📊 Özet İstatistikler",
      h3("📊 Özet İstatistikler"),
      br(),
      fluidRow(
        column(6, plotlyOutput("inst_plot", height = "500px")),
        column(6, plotlyOutput("field_plot", height = "500px"))
      ),
      br(),
      plotlyOutput("year_plot", height = "400px"),
      br(),
      h4("🏆 En Yüksek Metrikler"),
      fluidRow(
        column(
          4,
          h5("En Yüksek H-İndeksi"),
          DTOutput("top_h_table")
        ),
        column(
          4,
          h5("En Çok Atıf"),
          DTOutput("top_cit_table")
        ),
        column(
          4,
          h5("En Çok Yayın"),
          DTOutput("top_pub_table")
        )
      )
    ),

    # TAB 3: Researcher Profile (Swapped)
    tabPanel(
      "👤 Araştırmacı Profili",
      h3("👤 Araştırmacı Profili"),
      p("Bireysel araştırmacıların detaylı akademik profillerini inceleyin."),
      br(),
      uiOutput("researcher_selector_ui"),
      uiOutput("researcher_profile_content")
    ),

    # TAB 4: Award Analysis
    tabPanel(
      "🏆 Ödül Anı Analizi",
      h3("🏆 Ödül Anı Analizi"),
      p("Araştırmacıların ödül aldıkları andaki akademik performanslarını inceleyin."),
      br(),
      fluidRow(
        column(3, checkboxInput("award_log_x", "Logaritmik X Ekseni", TRUE)),
        column(3, checkboxInput("award_log_y", "Logaritmik Y Ekseni", TRUE)),
        column(6, uiOutput("award_highlight_ui"))
      ),
      br(),
      fluidRow(
        column(
          6,
          h4("📈 Atıf Artışı"),
          plotlyOutput("award_cit_plot", height = "500px")
        ),
        column(
          6,
          h4("📚 Yayın Artışı"),
          plotlyOutput("award_pub_plot", height = "500px")
        )
      ),
      br(),
      h4("🚀 En Hızlı Büyüyen Araştırmacılar"),
      fluidRow(
        column(
          6,
          h5("Atıf Artışı (Mutlak)"),
          DTOutput("top_growth_cit_table")
        ),
        column(
          6,
          h5("Yayın Artışı (Mutlak)"),
          DTOutput("top_growth_pub_table")
        )
      )
    ),

    # TAB 5: Data Table
    tabPanel(
      "📋 Veri Tablosu",
      h3("📋 Veri Tablosu"),
      p("Tüm veriyi inceleyin ve arayın."),
      br(),
      textInput("search_text", "🔍 Araştırmacı Ara (Ad, Soyad, Kurum)", ""),
      br(),
      DTOutput("data_table")
    ),

    # TAB 6: About
    tabPanel(
      "ℹ️ Hakkında",
      h3("ℹ️ Veri Toplama Metodolojisi ve Açıklamalar"),
      div(
        class = "info-box",
        h4("📚 Veri Nasıl Toplandı?"),
        p(
          "Bu gösterge panelinde sunulan veriler, ", strong("Ocak 2026"), " tarihinde ",
          strong("Google Scholar"), " platformundan kamuya açık olarak erişilebilen bilgiler kullanılarak toplanmıştır."
        )
      ),
      h4("Veri Toplama Süreci:"),
      tags$ol(
        tags$li(strong("Araştırmacı Eşleştirme:"), " TÜBA GEBİP ödül sahiplerinin isimleri kullanılarak Google Scholar'da profil araması yapılmıştır."),
        tags$li(strong("Metrik Çıkarımı:"), " Her araştırmacı için toplam atıf, h-indeksi, i10-indeksi, toplam yayın sayısı ve yıllık dağılımlar çıkarılmıştır. Google Scholar veritabanında ödül yılına kadar olan yayın/atıf verisinin bulunması durumunda ödül anındaki metrikler de gösterilmiştir"),
        tags$li(strong("Eşleşme Doğrulaması:"), " Profil eşleştirmelerinin doğruluğunu sağlamak için en iyi çaba gösterilmiştir.")
      ),
      hr(),
      div(
        class = "info-box",
        h4("📖 \"Yayın\" Tanımı"),
        p(
          "Bu gösterge panelinde ", strong("\"yayın\""), " terimi, ",
          strong("Google Scholar'ın tanımladığı tüm akademik çıktıları"), " kapsamaktadır:"
        )
      ),
      tags$ul(
        tags$li("📄 Hakemli dergi makaleleri"),
        tags$li("📘 Kitap ve kitap bölümleri"),
        tags$li("🎓 Doktora ve yüksek lisans tezleri"),
        tags$li("📝 Konferans bildirileri"),
        tags$li("📊 Teknik raporlar"),
        tags$li("🔬 Ön baskılar (preprints)"),
        tags$li("💡 Patentler")
      ),
      hr(),
      div(
        class = "info-box",
        h4("📏 Akademik Performans İndekslerinin Sınırlılıkları"),
        p(strong("ÖNEMLİ:"), " Tüm akademik performans ölçüm indekslerinin önemli eksiklikleri vardır."),
        tags$ul(
          tags$li("🕐 ", strong("Zaman Faktörü:"), " Bu indeksler zaman içinde birikir"),
          tags$li("🎯 ", strong("Kalite vs. Miktar:"), " Yüksek atıf sayısı tek gösterge değildir"),
          tags$li("🔬 ", strong("Disiplin Farklılıkları:"), " Farklı alanlarda atıf pratikleri değişir"),
          tags$li("💡 ", strong("Yenilikçi Çalışmalar:"), " Çığır açan çalışmalar başlangıçta düşük atıf alabilir")
        )
      ),
      hr(),
      h4("⚠️ Sorumluluk Reddi ve Sınırlamalar"),
      p(strong("DİKKAT:"), " Bu veriler ", strong("\"olduğu gibi\" (as-is)"), " sunulmaktadır."),
      tags$ul(
        tags$li("✅ Veriler Google Scholar'ın kamuya açık verileri kullanılarak toplanmıştır"),
        tags$li("📅 Veriler Ocak 2026 tarihinde toplanmıştır ve güncel olmayabilir"),
        tags$li("🎯 En iyi çaba ile eşleştirme yapılmıştır ancak hatalar olabilir"),
        tags$li("❌ Veri doğruluğu garanti edilmemektedir")
      ),
      hr(),
      h4("📧 İletişim ve Geri Bildirim"),
      p("Veri hataları, eşleşme sorunları veya önerileriniz için lütfen iletişime geçiniz:"),
      p(strong("atakanekiz@iyte.edu.tr")),
      p("📷 ", tags$a(href = "https://www.instagram.com/dr_atakan_ekiz/", target = "_blank", "@dr_atakan_ekiz"), " | ", tags$a(href = "https://www.instagram.com/ekizlab/", target = "_blank", "@ekizlab")),
      p(tags$a(href = "https://www.atakanekiz.com", target = "_blank", "www.atakanekiz.com")),
      hr(),
      p(strong("Son Güncelleme:"), " Ocak 2026"),
      p(strong("Veri Kaynağı:"), " Google Scholar (Kamuya Açık Veriler)")
    )
  )
)

# ============================================================================
# SERVER LOGIC
# ============================================================================

server <- function(input, output, session) {
  # Load data
  df <- load_data()

  # Reactive filtered data
  # Reactive filtered data (Base - Year/Field/ID)
  filtered_data_base_raw <- reactive({
    data <- df

    # Year filter
    if (!is.null(input$year_range)) {
      data <- data %>%
        filter(yili >= input$year_range[1] & yili <= input$year_range[2])
    }

    # Field filter
    if (!is.null(input$field_filter) && length(input$field_filter) > 0) {
      data <- data %>%
        filter(genel_alan %in% input$field_filter)
    }

    # Scholar ID filter
    if (!is.null(input$only_with_id) && input$only_with_id) {
      data <- data %>%
        filter(scholar_id != "no id found" & !is.na(scholar_id))
    }

    return(data)
  })

  # Reactive filtered data (Plot specific - Add Axis NA)
  filtered_data_plot_raw <- reactive({
    data <- filtered_data_base_raw()

    # Remove rows with NA in selected axes
    if (!is.null(input$x_axis) && !is.null(input$y_axis)) {
      data <- data %>%
        filter(!is.na(.data[[input$x_axis]]) & !is.na(.data[[input$y_axis]]))
    }

    return(data)
  })

  # Debounced filtered data
  filtered_data_base <- filtered_data_base_raw %>% debounce(1000)
  filtered_data <- filtered_data_plot_raw %>% debounce(1000)

  # Dynamic UI elements
  output$year_slider_ui <- renderUI({
    min_year <- min(df$yili, na.rm = TRUE)
    max_year <- max(df$yili, na.rm = TRUE)
    sliderInput("year_range", "Yıl Aralığı",
      min = min_year, max = max_year,
      value = c(min_year, max_year),
      step = 1, sep = ""
    )
  })

  output$field_filter_ui <- renderUI({
    all_fields <- sort(unique(df$genel_alan[!is.na(df$genel_alan)]))
    tagList(
      div(
        style = "display: flex; gap: 10px; margin-bottom: 5px;",
        actionButton("select_all_fields", "Tümünü Seç", size = "xs"),
        actionButton("deselect_all_fields", "Temizle", size = "xs")
      ),
      selectizeInput("field_filter", "Genel Alana Göre Filtrele",
        choices = all_fields,
        selected = all_fields,
        multiple = TRUE
      )
    )
  })

  observeEvent(input$select_all_fields, {
    all_fields <- sort(unique(df$genel_alan[!is.na(df$genel_alan)]))
    updateSelectizeInput(session, "field_filter", selected = all_fields)
  })

  observeEvent(input$deselect_all_fields, {
    updateSelectizeInput(session, "field_filter", selected = character(0))
  })

  output$highlight_selector_ui <- renderUI({
    # Use all names from loaded dataframe
    all_names <- sort(unique(df$adi_soyadi))
    selectizeInput("highlight_researcher", "Araştırmacı Vurgula",
      choices = c("Seçiniz..." = "", all_names),
      selected = NULL,
      multiple = FALSE,
      options = list(placeholder = "İsim arayın...")
    )
  })

  output$award_highlight_ui <- renderUI({
    # Use all names from loaded dataframe
    all_names <- sort(unique(df$adi_soyadi))
    selectizeInput("award_highlight_researcher", "Araştırmacı Vurgula",
      choices = c("Seçiniz..." = "", all_names),
      selected = NULL,
      multiple = FALSE,
      options = list(placeholder = "İsim arayın...")
    )
  })

  # TAB 1: Exploration plot
  output$exploration_plot <- renderPlotly({
    data <- filtered_data()

    if (nrow(data) == 0) {
      return(plotly_empty() %>%
        layout(title = "⚠️ Seçilen filtreler için veri bulunmuyor"))
    }

    # Prepare plot parameters
    color_var <- if (input$color_by != "none") input$color_by else NULL
    size_var <- if (input$size_by != "none") input$size_by else NULL

    # Clean size variable to avoid issues with NA
    if (!is.null(size_var)) {
      data <- data %>% filter(!is.na(.data[[size_var]]))
    }

    # Axis labels
    axis_labels <- c(
      "yili" = "Ödül Yılı",
      "toplam_atif" = "Toplam Atıf",
      "h_indeksi" = "H-İndeksi",
      "i10_indeksi" = "i10-İndeksi",
      "toplam_yayin" = "Toplam Yayın",
      "odul_aninda_atif" = "Ödül Anında Atıf",
      "odul_aninda_yayin" = "Ödül Anında Yayın"
    )

    # Create hover text
    data$hover_text <- paste0(
      "<b>", data$adi_soyadi, "</b><br>",
      "Kurum: ", data$calistigi_kurum, "<br>",
      "Genel Alan: ", data$genel_alan, "<br>",
      "Detaylı Alan: ", data$alan, "<br>",
      "Ödül Yılı: ", data$yili, "<br>",
      "H-İndeksi: ", data$h_indeksi, "<br>",
      "Toplam Atıf: ", format(data$toplam_atif, big.mark = ","), "<br>",
      "Toplam Yayın: ", data$toplam_yayin
    )

    # Create plot with proper parameters to avoid "trace 0" in legend
    if (!is.null(color_var) && !is.null(size_var)) {
      # Both color and size - use standard mapping with explicit diameter scaling
      p <- plot_ly(data,
        x = ~ get(input$x_axis),
        y = ~ get(input$y_axis),
        color = ~ get(color_var),
        size = ~ get(size_var),
        sizes = c(10, 50),
        text = ~hover_text,
        hoverinfo = "text",
        type = "scatter",
        mode = "markers",
        marker = list(
          sizemode = "diameter",
          opacity = input$opacity
        )
      )
    } else if (!is.null(color_var)) {
      # Only color
      p <- plot_ly(data,
        x = ~ get(input$x_axis),
        y = ~ get(input$y_axis),
        color = ~ get(color_var),
        text = ~hover_text,
        hoverinfo = "text",
        type = "scatter",
        mode = "markers",
        marker = list(opacity = input$opacity)
      )
    } else if (!is.null(size_var)) {
      # Only size
      p <- plot_ly(data,
        x = ~ get(input$x_axis),
        y = ~ get(input$y_axis),
        size = ~ get(size_var),
        sizes = c(10, 50),
        text = ~hover_text,
        hoverinfo = "text",
        type = "scatter",
        mode = "markers",
        marker = list(
          sizemode = "diameter",
          opacity = input$opacity,
          color = "#1f77b4"
        ),
        showlegend = FALSE
      )
    } else {
      # No color or size
      p <- plot_ly(data,
        x = ~ get(input$x_axis),
        y = ~ get(input$y_axis),
        text = ~hover_text,
        hoverinfo = "text",
        type = "scatter",
        mode = "markers",
        marker = list(opacity = input$opacity, color = "#1f77b4"),
        showlegend = FALSE
      )
    }

    # Layout with custom colors for genel_alan and log scale
    y_axis_config <- list(title = axis_labels[input$y_axis])
    if (!is.null(input$log_scale_y) && input$log_scale_y) {
      y_axis_config$type <- "log"
    }

    p <- p %>% layout(
      title = paste(axis_labels[input$y_axis], "vs.", axis_labels[input$x_axis]),
      xaxis = list(title = axis_labels[input$x_axis]),
      yaxis = y_axis_config,
      font = list(size = 12)
    )

    # Apply custom color palette if genel_alan is selected
    if (!is.null(color_var) && color_var == "genel_alan") {
      unique_fields <- unique(data$genel_alan[!is.na(data$genel_alan)])
      colors_to_use <- genel_alan_colors[unique_fields]
      colors_to_use[is.na(colors_to_use)] <- "#cccccc" # Gray for unknown

      p <- p %>% layout(colorway = unname(colors_to_use))
    }

    # HIGHLIGHT LOGIC
    if (!is.null(input$highlight_researcher) && input$highlight_researcher != "") {
      highlight_data <- data %>% filter(adi_soyadi == input$highlight_researcher)

      if (nrow(highlight_data) > 0) {
        # Create highlighting hover text
        hl_hover <- paste0(
          "<b>📍 ", highlight_data$adi_soyadi, "</b><br>",
          "Kurum: ", highlight_data$calistigi_kurum, "<br>",
          "Genel Alan: ", highlight_data$genel_alan, "<br>",
          "Detaylı Alan: ", highlight_data$alan, "<br>",
          "Ödül Yılı: ", highlight_data$yili, "<br>",
          "H-İndeksi: ", highlight_data$h_indeksi, "<br>",
          "Toplam Atıf: ", format(highlight_data$toplam_atif, big.mark = ","), "<br>",
          "Toplam Yayın: ", highlight_data$toplam_yayin
        )

        p <- p %>%
          add_trace(
            data = highlight_data,
            x = ~ get(input$x_axis),
            y = ~ get(input$y_axis),
            type = "scatter",
            mode = "markers",
            marker = list(
              size = 20,
              color = "#d62728", # Red
              line = list(color = "black", width = 2),
              opacity = 1
            ),
            text = hl_hover,
            hoverinfo = "text",
            name = "Vurgulanan",
            showlegend = FALSE,
            inherit = FALSE
          ) %>%
          add_annotations(
            x = highlight_data[[input$x_axis]],
            y = highlight_data[[input$y_axis]],
            text = highlight_data$adi_soyadi,
            xref = "x",
            yref = "y",
            showarrow = TRUE,
            arrowhead = 2,
            arrowsize = 1,
            ax = 0,
            ay = -30,
            font = list(color = "black", size = 12, family = "Arial"),
            bgcolor = "rgba(255, 255, 255, 0.75)",
            bordercolor = "red"
          )
      }
    }

    return(p)
  })

  # Metrics
  output$metric_total <- renderUI({
    data <- filtered_data()
    div(
      class = "metric-card",
      div(class = "metric-value", nrow(data)),
      div(class = "metric-label", "Toplam Araştırmacı")
    )
  })

  output$metric_h_index <- renderUI({
    data <- filtered_data()
    avg_h <- mean(data$h_indeksi, na.rm = TRUE)
    div(
      class = "metric-card",
      div(class = "metric-value", sprintf("%.1f", avg_h)),
      div(class = "metric-label", "Ortalama H-İndeksi")
    )
  })

  output$metric_citations <- renderUI({
    data <- filtered_data()
    avg_cit <- mean(data$toplam_atif, na.rm = TRUE)
    div(
      class = "metric-card",
      div(class = "metric-value", format(round(avg_cit), big.mark = ",")),
      div(class = "metric-label", "Ortalama Toplam Atıf")
    )
  })

  output$metric_publications <- renderUI({
    data <- filtered_data()
    avg_pub <- mean(data$toplam_yayin, na.rm = TRUE)
    div(
      class = "metric-card",
      div(class = "metric-value", format(round(avg_pub), big.mark = ",")),
      div(class = "metric-label", "Ortalama Toplam Yayın")
    )
  })

  # TAB 2: Researcher Profile
  output$researcher_selector_ui <- renderUI({
    df_with_id <- df %>%
      filter(scholar_id != "no id found" & !is.na(scholar_id))

    researcher_names <- sort(df_with_id$adi_soyadi)

    selectInput("selected_researcher", "🔍 Araştırmacı Seçin",
      choices = researcher_names,
      selected = researcher_names[1]
    )
  })

  output$researcher_profile_content <- renderUI({
    req(input$selected_researcher)

    # Add error handling
    tryCatch(
      {
        researcher_data <- df %>%
          filter(adi_soyadi == input$selected_researcher) %>%
          slice(1)

        if (nrow(researcher_data) == 0) {
          return(p("Araştırmacı bulunamadı"))
        }

        # Create profile UI
        tagList(
          h2(researcher_data$adi_soyadi),
          fluidRow(
            column(
              4,
              p(strong("🏛️ Kurum: "), researcher_data$calistigi_kurum),
              p(strong("🔬 Alan: "), researcher_data$genel_alan)
            ),
            column(
              4,
              p(strong("🏆 Ödül Yılı: "), researcher_data$yili),
              p(strong("📚 Detaylı Alan: "), researcher_data$alan)
            ),
            column(
              4,
              if (!is.na(researcher_data$scholar_id) && researcher_data$scholar_id != "no id found") {
                scholar_url <- paste0("https://scholar.google.com/citations?user=", researcher_data$scholar_id)
                tags$a(href = scholar_url, target = "_blank", "🔗 Google Scholar Profili")
              }
            )
          ),
          hr(),
          h4("📊 Temel Akademik Metrikler"),
          fluidRow(
            column(
              2,
              div(
                class = "metric-card",
                div(class = "metric-value", researcher_data$h_indeksi),
                div(class = "metric-label", "H-İndeksi")
              )
            ),
            column(
              2,
              div(
                class = "metric-card",
                div(class = "metric-value", researcher_data$i10_indeksi),
                div(class = "metric-label", "i10-İndeksi")
              )
            ),
            column(
              3,
              div(
                class = "metric-card",
                div(class = "metric-value", format(researcher_data$toplam_atif, big.mark = ",")),
                div(class = "metric-label", "Toplam Atıf")
              )
            ),
            column(
              2,
              div(
                class = "metric-card",
                div(class = "metric-value", researcher_data$toplam_yayin),
                div(class = "metric-label", "Toplam Yayın")
              )
            ),
            column(
              3,
              div(
                class = "metric-card",
                div(
                  class = "metric-value",
                  if (!is.na(researcher_data$toplam_yayin) && researcher_data$toplam_yayin > 0) {
                    sprintf("%.1f", researcher_data$toplam_atif / researcher_data$toplam_yayin)
                  } else {
                    "N/A"
                  }
                ),
                div(class = "metric-label", "Atıf/Yayın")
              )
            )
          ),
          hr(),
          h4("📈 Zaman İçinde Gelişim"),
          fluidRow(
            column(6, plotlyOutput("researcher_cit_time", height = "400px")),
            column(6, plotlyOutput("researcher_pub_time", height = "400px"))
          )
        ) # Close tagList
      },
      error = function(e) {
        return(div(
          class = "alert alert-danger",
          p("Profil yüklenirken bir hata oluştu:"),
          p(as.character(e))
        ))
      }
    )
  })

  # Researcher time series plots
  output$researcher_cit_time <- renderPlotly({
    req(input$selected_researcher)

    researcher_data <- df %>%
      filter(adi_soyadi == input$selected_researcher) %>%
      slice(1)

    if (nrow(researcher_data) == 0) {
      return(plotly_empty() %>% layout(title = "Veri bulunamadı"))
    }

    yearly_data <- parse_yearly_data(researcher_data$yillik_atif)

    if (nrow(yearly_data$cumulative) > 0) {
      p <- plot_ly(yearly_data$cumulative,
        x = ~year,
        y = ~cumulative,
        type = "scatter",
        mode = "lines+markers",
        line = list(color = "#1f77b4", width = 3),
        marker = list(size = 8, color = "#1f77b4"),
        name = "Kümülatif Atıf",
        hovertemplate = "<b>Yıl:</b> %{x}<br><b>Kümülatif Atıf:</b> %{y:,}<extra></extra>"
      )

      # Add award year line
      if (!is.na(researcher_data$yili)) {
        max_val <- max(yearly_data$cumulative$cumulative, na.rm = TRUE)
        p <- p %>% add_trace(
          x = c(researcher_data$yili, researcher_data$yili),
          y = c(0, max_val),
          mode = "lines",
          line = list(color = "#d62728", width = 2, dash = "dash"),
          name = "Ödül Yılı",
          showlegend = FALSE,
          hoverinfo = "skip",
          inherit = FALSE
        )
      }

      p %>% layout(
        title = "Kümülatif Atıf Sayısı",
        xaxis = list(title = "Yıl"),
        yaxis = list(title = "Kümülatif Atıf"),
        hovermode = "x unified"
      )
    } else {
      plotly_empty() %>% layout(title = "Yıllık atıf verisi mevcut değil")
    }
  })

  output$researcher_pub_time <- renderPlotly({
    req(input$selected_researcher)

    researcher_data <- df %>%
      filter(adi_soyadi == input$selected_researcher) %>%
      slice(1)

    if (nrow(researcher_data) == 0) {
      return(plotly_empty() %>% layout(title = "Veri bulunamadı"))
    }

    yearly_data <- parse_yearly_data(researcher_data$yillik_yayin)

    if (nrow(yearly_data$cumulative) > 0) {
      p <- plot_ly(yearly_data$cumulative,
        x = ~year,
        y = ~cumulative,
        type = "scatter",
        mode = "lines+markers",
        line = list(color = "#2ca02c", width = 3),
        marker = list(size = 8, color = "#2ca02c"),
        name = "Kümülatif Yayın",
        hovertemplate = "<b>Yıl:</b> %{x}<br><b>Kümülatif Yayın:</b> %{y:,}<extra></extra>"
      )

      # Add award year line
      if (!is.na(researcher_data$yili)) {
        max_val <- max(yearly_data$cumulative$cumulative, na.rm = TRUE)
        p <- p %>% add_trace(
          x = c(researcher_data$yili, researcher_data$yili),
          y = c(0, max_val),
          mode = "lines",
          line = list(color = "#d62728", width = 2, dash = "dash"),
          name = "Ödül Yılı",
          showlegend = FALSE,
          hoverinfo = "skip",
          inherit = FALSE
        )
      }

      p %>% layout(
        title = "Kümülatif Yayın Sayısı",
        xaxis = list(title = "Yıl"),
        yaxis = list(title = "Kümülatif Yayın"),
        hovermode = "x unified"
      )
    } else {
      plotly_empty() %>% layout(title = "Yıllık yayın verisi mevcut değil")
    }
  })

  # TAB 3: Summary Statistics
  output$inst_plot <- renderPlotly({
    inst_counts <- filtered_data_base() %>%
      count(calistigi_kurum, sort = TRUE) %>%
      head(15)

    plot_ly(inst_counts,
      y = ~ reorder(calistigi_kurum, n), x = ~n,
      type = "bar", orientation = "h",
      marker = list(color = "#1f77b4")
    ) %>%
      layout(
        title = "Ödül Sayısına Göre İlk 15 Kurum",
        xaxis = list(title = "Sayı"),
        yaxis = list(title = "")
      )
  })

  output$field_plot <- renderPlotly({
    field_counts <- filtered_data_base() %>%
      count(genel_alan) %>%
      filter(!is.na(genel_alan))

    plot_ly(field_counts,
      labels = ~genel_alan, values = ~n,
      type = "pie", hole = 0.3
    ) %>%
      layout(title = "Genel Alana Göre Ödüller")
  })

  output$year_plot <- renderPlotly({
    year_counts <- filtered_data_base() %>%
      count(yili) %>%
      arrange(yili)

    plot_ly(year_counts,
      x = ~yili, y = ~n,
      type = "bar",
      marker = list(color = "#1f77b4")
    ) %>%
      layout(
        title = "Yıllara Göre Ödül Sayısı",
        xaxis = list(title = "Yıl"),
        yaxis = list(title = "Sayı")
      )
  })

  # Top tables
  df_stats <- reactive({
    filtered_data_base()
  })

  output$top_h_table <- renderDT({
    df_stats() %>%
      select(adi_soyadi, h_indeksi, yili) %>%
      arrange(desc(h_indeksi)) %>%
      head(5) %>%
      datatable(
        options = list(dom = "t", pageLength = 5),
        rownames = FALSE,
        colnames = c("Adı Soyadı", "H-İndeksi", "Yıl")
      )
  })

  output$top_cit_table <- renderDT({
    df_stats() %>%
      select(adi_soyadi, toplam_atif, yili) %>%
      arrange(desc(toplam_atif)) %>%
      head(5) %>%
      datatable(
        options = list(dom = "t", pageLength = 5),
        rownames = FALSE,
        colnames = c("Adı Soyadı", "Toplam Atıf", "Yıl")
      )
  })

  output$top_pub_table <- renderDT({
    df_stats() %>%
      select(adi_soyadi, toplam_yayin, yili) %>%
      arrange(desc(toplam_yayin)) %>%
      head(5) %>%
      datatable(
        options = list(dom = "t", pageLength = 5),
        rownames = FALSE,
        colnames = c("Adı Soyadı", "Toplam Yayın", "Yıl")
      )
  })

  # TAB 4: Award Analysis
  df_award <- reactive({
    df %>%
      filter(scholar_id != "no id found" & !is.na(scholar_id)) %>%
      mutate(
        atif_artisi = toplam_atif - odul_aninda_atif,
        yayin_artisi = toplam_yayin - odul_aninda_yayin
      )
  })

  output$award_cit_plot <- renderPlotly({
    data <- df_award()

    # Create scatter plot
    p <- plot_ly(data,
      x = ~odul_aninda_atif, y = ~toplam_atif,
      color = ~genel_alan,
      text = ~ paste0(
        "<b>", adi_soyadi, "</b><br>",
        "Ödül Yılı: ", yili, "<br>",
        "H-İndeksi: ", h_indeksi
      ),
      hoverinfo = "text",
      type = "scatter", mode = "markers",
      name = ~genel_alan
    )

    # Add diagonal line
    max_val <- max(data$toplam_atif, na.rm = TRUE)
    p <- p %>% add_trace(
      x = c(0, max_val),
      y = c(0, max_val),
      mode = "lines",
      line = list(dash = "dash", color = "gray", width = 1),
      name = "y=x",
      showlegend = FALSE,
      hoverinfo = "skip",
      inherit = FALSE
    )

    # Apply custom color palette
    unique_fields <- unique(data$genel_alan[!is.na(data$genel_alan)])
    colors_to_use <- genel_alan_colors[unique_fields]
    colors_to_use[is.na(colors_to_use)] <- "#cccccc"

    # Axes config
    xaxis_config <- list(title = "Ödül Anında Atıf")
    if (!is.null(input$award_log_x) && input$award_log_x) {
      xaxis_config$type <- "log"
    }

    yaxis_config <- list(title = "Güncel Toplam Atıf")
    if (!is.null(input$award_log_y) && input$award_log_y) {
      yaxis_config$type <- "log"
    }

    p <- p %>% layout(
      title = "Ödül Anı vs Güncel Atıf Sayısı",
      xaxis = xaxis_config,
      yaxis = yaxis_config,
      colorway = unname(colors_to_use)
    )

    # Highlight Logic
    if (!is.null(input$award_highlight_researcher) && input$award_highlight_researcher != "") {
      highlight_data <- data %>% filter(adi_soyadi == input$award_highlight_researcher)

      if (nrow(highlight_data) > 0) {
        p <- p %>% add_trace(
          data = highlight_data,
          x = ~odul_aninda_atif,
          y = ~toplam_atif,
          type = "scatter",
          mode = "markers+text",
          marker = list(
            size = 20,
            color = "#d62728", # Red
            symbol = "circle-open",
            line = list(color = "#d62728", width = 3)
          ),
          text = ~adi_soyadi,
          textposition = "top center",
          name = "Vurgulanan",
          showlegend = FALSE,
          hoverinfo = "skip",
          inherit = FALSE
        )
      }
    }

    return(p)
  })

  output$award_pub_plot <- renderPlotly({
    data <- df_award()

    # Create scatter plot
    p <- plot_ly(data,
      x = ~odul_aninda_yayin, y = ~toplam_yayin,
      color = ~genel_alan,
      text = ~ paste0(
        "<b>", adi_soyadi, "</b><br>",
        "Ödül Yılı: ", yili, "<br>",
        "H-İndeksi: ", h_indeksi
      ),
      hoverinfo = "text",
      type = "scatter", mode = "markers",
      name = ~genel_alan
    )

    # Add diagonal line
    max_val <- max(data$toplam_yayin, na.rm = TRUE)
    p <- p %>% add_trace(
      x = c(0, max_val),
      y = c(0, max_val),
      mode = "lines",
      line = list(dash = "dash", color = "gray", width = 1),
      name = "y=x",
      showlegend = FALSE,
      hoverinfo = "skip",
      inherit = FALSE
    )

    # Apply custom color palette
    unique_fields <- unique(data$genel_alan[!is.na(data$genel_alan)])
    colors_to_use <- genel_alan_colors[unique_fields]
    colors_to_use[is.na(colors_to_use)] <- "#cccccc"

    # Axes config
    xaxis_config <- list(title = "Ödül Anında Yayın")
    if (!is.null(input$award_log_x) && input$award_log_x) {
      xaxis_config$type <- "log"
    }

    yaxis_config <- list(title = "Güncel Toplam Yayın")
    if (!is.null(input$award_log_y) && input$award_log_y) {
      yaxis_config$type <- "log"
    }

    p <- p %>% layout(
      title = "Ödül Anı vs Güncel Yayın Sayısı",
      xaxis = xaxis_config,
      yaxis = yaxis_config,
      colorway = unname(colors_to_use)
    )

    # Highlight Logic
    if (!is.null(input$award_highlight_researcher) && input$award_highlight_researcher != "") {
      highlight_data <- data %>% filter(adi_soyadi == input$award_highlight_researcher)

      if (nrow(highlight_data) > 0) {
        p <- p %>% add_trace(
          data = highlight_data,
          x = ~odul_aninda_yayin,
          y = ~toplam_yayin,
          type = "scatter",
          mode = "markers+text",
          marker = list(
            size = 20,
            color = "#d62728", # Red
            symbol = "circle-open",
            line = list(color = "#d62728", width = 3)
          ),
          text = ~adi_soyadi,
          textposition = "top center",
          name = "Vurgulanan",
          showlegend = FALSE,
          hoverinfo = "skip",
          inherit = FALSE
        )
      }
    }

    return(p)
  })

  output$top_growth_cit_table <- renderDT({
    df_award() %>%
      select(adi_soyadi, odul_aninda_atif, toplam_atif, atif_artisi, yili) %>%
      arrange(desc(atif_artisi)) %>%
      head(10) %>%
      datatable(
        options = list(pageLength = 10),
        rownames = FALSE
      )
  })

  output$top_growth_pub_table <- renderDT({
    df_award() %>%
      select(adi_soyadi, odul_aninda_yayin, toplam_yayin, yayin_artisi, yili) %>%
      arrange(desc(yayin_artisi)) %>%
      head(10) %>%
      datatable(
        options = list(pageLength = 10),
        rownames = FALSE
      )
  })

  # TAB 5: Data Table
  data_table_filtered <- reactive({
    data <- df

    if (!is.null(input$search_text) && input$search_text != "") {
      search_term <- tolower(input$search_text)
      data <- data %>%
        filter(
          grepl(search_term, tolower(adi_soyadi)) |
            grepl(search_term, tolower(calistigi_kurum))
        )
    }

    return(data)
  })

  output$data_table <- renderDT({
    default_cols <- c(
      "adi_soyadi", "yili", "genel_alan", "calistigi_kurum",
      "h_indeksi", "toplam_atif", "toplam_yayin",
      "odul_aninda_atif", "odul_aninda_yayin"
    )

    data_table_filtered() %>%
      select(any_of(default_cols)) %>%
      datatable(
        options = list(
          pageLength = 25,
          scrollX = TRUE,
          language = list(
            search = "Ara:",
            lengthMenu = "Göster _MENU_ kayıt",
            info = "_TOTAL_ kayıttan _START_ - _END_ arası gösteriliyor",
            paginate = list(
              first = "İlk",
              last = "Son",
              `next` = "Sonraki",
              previous = "Önceki"
            )
          )
        ),
        rownames = FALSE
      )
  })

  # Download handlers
}

# ============================================================================
# RUN APP
# ============================================================================

shinyApp(ui = ui, server = server)
