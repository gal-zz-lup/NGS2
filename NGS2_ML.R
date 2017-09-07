#' Script to create a classification model to understand features that are important to predict the action of the user.
#' @author Anuradha Uduwage
#' At some point some of the code need to functionalized (once we have the proper data set)
source("NGS2_Util.R")

cooperation.exp.1 <- csv_file_reader("../cooperation_exp1.csv",TRUE, ",")
cooperation.exp.2 <- csv_file_reader("../cooperation_exp2.csv",TRUE, ",")
empanelment <- csv_file_reader("../empanelment_cleaned.csv", TRUE, ",")

class(cooperation.exp.1$empanel_id)
class(empanelment$ExternalReference)

# Merging the experiment1 data with empanelment
merged.empanel.exp1 <- merge(x = cooperation.exp.1[,c('empanel_id','action')], 
                                 y = empanelment, by.x = 'empanel_id', by.y = 'ExternalReference')
cat("Number of rows in merged.empanelment.exp1", nrow(merged.empanel.exp1))

# Merging the experiment2 data with empanelment
names(cooperation.exp.2)[names(cooperation.exp.2) == 'decision0d1c'] <- "action"
merged.empanel.exp2 <- merge(x = cooperation.exp.2[,c('empanel_id','action')], 
                             y = empanelment, by.x = 'empanel_id', by.y = 'ExternalReference')

# removing the duplicates
merged.empanel.exp1 <- subset(merged.empanel.exp1, !duplicated(empanel_id))

# Removing fields that are not important for ML process
# Note: We might use language when we combine all experiments together
not.important.vars <- c("StartDate", "EndDate", "EndDate", "Status","IPAddress",
                        "Progress", "Duration..in.seconds.", "Finished", "RecordedDate",
                        "ResponseId", "RecipientLastName","RecipientFirstName", "RecipientEmail",
                        "LocationLatitude","LocationLongitude","DistributionChannel", "UserLanguage",
                        "Q3_consent", "Q40_mobile_number")

# removing unnecessary columns
merged.empanel.exp1 <- merged.empanel.exp1[, -which(names(merged.empanel.exp1) %in% not.important.vars)]

merged.empanel.exp2 <- merged.empanel.exp2[, -which(names(merged.empanel.exp2) %in% not.important.vars)]


# Recoding the categorical variables
# We are still finalizing the final data set as a result of that current pipe line in not using the recorded
# Recording can take place once we know all the possible combinations for all the categorical variables.
Q13_education <- list('Post-graduate degree' = 1,
                      'High school' = 2,
                      'College degree' = 3,
                      'Some college' = 4)

# organizing data.frame, easy for rescaling
categorical.columns <- c("Q12_gender","Q13_education","Q16_employer_selfemployed",
                         "Q17_occupation","Q18_employ_situation","Q19_income_US","Q22_income_feeling",
                         "Q23_religion", "Q24_religion_freq","Q27_marital_status",
                         "Q32_1_smartphone", "Q32_2_computer", "Q32_3_tablet","Q33_internet_where")

# response and index
response.index.var <- c("empanel_id","action")

# getting the names of the none categorical columns
none.categorical.columns <- names(merged.empanel.exp1[,!(names(merged.empanel.exp1) %in% c(categorical.columns, response.index.var))])

final.order <- c(response.index.var,categorical.columns, none.categorical.columns)
merged.empanel.exp1 <- merged.empanel.exp1[c(final.order)]

# removing columsn that has all NA
merged.empanel.exp1 <- Filter(function(x)!all(is.na(x)), merged.empanel.exp1)

cat("Size of the data.frame after cleanup -", dim(merged.empanel.exp1))

# converting action into a factor
merged.empanel.exp1$action <- factor(as.numeric(as.logical(merged.empanel.exp1$action)))

# Imputing the non numerical columns - Later we can change for better imputation
Mode <- function(x) { 
  ux <- sort(unique(x))
  ux[which.max(tabulate(match(x, ux)))] 
}

merged.empanel.exp1[categorical.columns] <- lapply(merged.empanel.exp1[categorical.columns], function(x)
  replace(x, is.na(x), Mode(x[!is.na(x)])))

merged.empanel.exp1[, categorical.columns] <- lapply(merged.empanel.exp1[, categorical.columns], as.factor)

# This step is to replicate more data since we don't have data to run models
# Once real data come in we can re-evaluate this process and remove this line
merged.empanelment.exp1$empanel_id <- as.numeric(gsub("\\_","", merged.empanelment.exp1$empanel_id))

# replicating rows to generate more data to build
# We don't need this step once we have proper data.
merged.empanel.exp1 <- as.data.frame(lapply(merged.empanelment.exp1, rep, 1000))
merged.empanel.exp1 <- merged.empanel.exp1[sample(nrow(merged.empanel.exp1)),]

set.seed(901)

# creating sample size for training
sample.size <- floor(0.75 * nrow(merged.empanel.exp1))
train.index <- sample(seq_len(nrow(merged.empanel.exp1)), size=sample.size)

train.exp1 <- merged.empanel.exp1[train.index,]
test.exp1 <- merged.empanel.exp1[-train.index,]

rf.model <- randomForest(action ~., data=train.exp1, ntree=500, na.action = na.omit)

