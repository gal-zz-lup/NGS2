#' Install packages that are required for this file 
#' Try use Utility.R file to maintain all the required packages
#' @author Anuradha Uduwage
#'##############################################################
list.of.packages <- c("dplyr", "missForest", "randomForest")
new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]
if(length(new.packages)) install.packages(new.packages, repos="http://cran.us.r-project.org",quiet=T)
lapply(list.of.packages, require, character.only = TRUE)

#' Read csv file
#' 
#' This function reads csv file and returns a data.fame.
#' @param filename name of the file
#' @param header boolean value to indicate header exist or not.
#' @param seperator column seperator of the file.
#' @return R data.frame
csv_file_reader <- function(filename, header, seperator) {
  cat("Loading", filename,"...", "\n")
  d <- read.csv(filename, header=header, sep = seperator, stringsAsFactors = FALSE, na.strings = c("", " ", "NA"))
  cat("Done!","\n")
  return(d)
}

#' Function take data.frame, column name, lookup table as list
#' @param d data.frame
#' @param regex column name to as regular expression
#' @param lookup list containing recording values
#' @return coloumn with recorded values
relabel_values <- function(d, regex, lookup) {
  return(apply(d[, grep(regex, names(d)),drop=F], 2, function(x) {
    do.call(c, ifelse(x %in% names(lookup), lookup[x], NA))
  }))
}

#' Function return column names that has NA values
#' @param df data.frame
#' @return columna names
nacols <- function(df) {
  colnames(df)[unlist(lapply(df, function(x) any(is.na(x))))]
}