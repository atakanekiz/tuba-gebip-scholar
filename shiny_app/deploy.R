# Deploy to shinyapps.io
# This script helps you deploy the TÜBA GEBİP dashboard to shinyapps.io

cat("=================================================\n")
cat("TÜBA GEBİP Dashboard - Deploy to shinyapps.io\n")
cat("=================================================\n\n")

# Check if rsconnect is installed
if (!require("rsconnect", quietly = TRUE)) {
  cat("rsconnect package not found. Installing...\n")
  install.packages("rsconnect")
  library(rsconnect)
}

# Check if account is configured
accounts <- rsconnect::accounts()

if (nrow(accounts) == 0) {
  cat("\n⚠️  No shinyapps.io account configured!\n\n")
  cat("Please follow these steps:\n")
  cat("1. Go to https://www.shinyapps.io/ and create a free account\n")
  cat("2. Log in and go to Account > Tokens\n")
  cat("3. Click 'Show' and then 'Show Secret'\n")
  cat("4. Copy the entire code block\n")
  cat("5. Run it in your R console\n\n")
  cat("Example:\n")
  cat("rsconnect::setAccountInfo(\n")
  cat("  name='your_account_name',\n")
  cat("  token='your_token',\n")
  cat("  secret='your_secret'\n")
  cat(")\n\n")
  
  response <- readline(prompt = "Have you configured your account? (y/n): ")
  
  if (tolower(response) != "y") {
    cat("\nPlease configure your account first and run this script again.\n")
    quit(save = "no")
  }
}

# Show configured accounts
cat("\nConfigured accounts:\n")
print(accounts)

# Ask for app name
cat("\n")
app_name <- readline(prompt = "Enter app name (default: gebip-dashboard): ")
if (app_name == "") {
  app_name <- "gebip-dashboard"
}

# Confirm deployment
cat("\n=================================================\n")
cat("Ready to deploy!\n")
cat("=================================================\n")
cat(paste0("App name: ", app_name, "\n"))
cat(paste0("Account: ", accounts$name[1], "\n"))
cat(paste0("URL: https://", accounts$name[1], ".shinyapps.io/", app_name, "/\n"))
cat("=================================================\n\n")

response <- readline(prompt = "Proceed with deployment? (y/n): ")

if (tolower(response) != "y") {
  cat("\nDeployment cancelled.\n")
  quit(save = "no")
}

# Deploy
cat("\nDeploying application...\n")
cat("This may take a few minutes...\n\n")

tryCatch({
  rsconnect::deployApp(
    appName = app_name,
    appTitle = "TÜBA GEBİP Akademik Performans Keşif Aracı",
    launch.browser = TRUE,
    forceUpdate = TRUE
  )
  
  cat("\n=================================================\n")
  cat("✓ Deployment successful!\n")
  cat("=================================================\n\n")
  cat(paste0("Your app is now live at:\n"))
  cat(paste0("https://", accounts$name[1], ".shinyapps.io/", app_name, "/\n\n"))
  
  cat("To embed in your website, use this HTML:\n\n")
  cat("<iframe\n")
  cat(paste0("  src=\"https://", accounts$name[1], ".shinyapps.io/", app_name, "/\"\n"))
  cat("  width=\"100%\"\n")
  cat("  height=\"900px\"\n")
  cat("  style=\"border: none; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);\">\n")
  cat("</iframe>\n\n")
  
  cat("=================================================\n")
  
}, error = function(e) {
  cat("\n=================================================\n")
  cat("✗ Deployment failed!\n")
  cat("=================================================\n\n")
  cat("Error message:\n")
  cat(as.character(e), "\n\n")
  
  cat("Common solutions:\n")
  cat("1. Make sure all required packages are installed\n")
  cat("2. Check that data file exists: ../data/gebip_scholar_final.csv\n")
  cat("3. Verify your shinyapps.io account has available hours\n")
  cat("4. Try running: rsconnect::showLogs() for detailed error logs\n\n")
})

cat("\nDone!\n")
