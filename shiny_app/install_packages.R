# Install Required Packages for TÜBA GEBİP Shiny Dashboard
# Run this script once to install all dependencies

cat("Installing required packages for TÜBA GEBİP Shiny Dashboard...\n\n")

# List of required packages
required_packages <- c(
  "shiny",        # Core Shiny framework
  "plotly",       # Interactive plots
  "DT",           # Interactive tables
  "dplyr",        # Data manipulation
  "tidyr",        # Data tidying
  "readr",        # CSV reading
  "stringr",      # String manipulation
  "scales"        # Formatting
)

# Function to install packages if not already installed
install_if_missing <- function(package) {
  if (!require(package, character.only = TRUE, quietly = TRUE)) {
    cat(paste0("Installing ", package, "...\n"))
    install.packages(package, repos = "https://cloud.r-project.org/", 
                     dependencies = TRUE, quiet = FALSE)
    cat(paste0(package, " installed successfully!\n\n"))
  } else {
    cat(paste0(package, " is already installed.\n"))
  }
}

# Install all required packages
cat("Checking and installing packages...\n")
cat("=====================================\n\n")

for (pkg in required_packages) {
  install_if_missing(pkg)
}

cat("\n=====================================\n")
cat("All required packages are installed!\n\n")

# Verify installations
cat("Verifying installations...\n")
cat("=====================================\n\n")

all_installed <- TRUE
for (pkg in required_packages) {
  if (require(pkg, character.only = TRUE, quietly = TRUE)) {
    cat(paste0("✓ ", pkg, " - OK\n"))
  } else {
    cat(paste0("✗ ", pkg, " - FAILED\n"))
    all_installed <- FALSE
  }
}

cat("\n=====================================\n")

if (all_installed) {
  cat("✓ All packages verified successfully!\n")
  cat("\nYou can now run the Shiny app with:\n")
  cat("  shiny::runApp()\n\n")
} else {
  cat("✗ Some packages failed to install.\n")
  cat("Please check the error messages above and try again.\n\n")
}

# Optional: Install rsconnect for deployment to shinyapps.io
cat("\nOptional: Install rsconnect for deployment?\n")
cat("This is needed only if you want to deploy to shinyapps.io\n")
response <- readline(prompt = "Install rsconnect? (y/n): ")

if (tolower(response) == "y") {
  install_if_missing("rsconnect")
  cat("\nrsconnect installed! You can now deploy to shinyapps.io\n")
}

cat("\nSetup complete!\n")
