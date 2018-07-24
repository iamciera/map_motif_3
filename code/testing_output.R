## Map_motif output

library(tidyverse)
test <- read_tsv("../code/map_motifalign_outlier_rm_with_length_VT11145.fa-bcd_FlyReg.fm.csv")

## clean

speciesSplit  <- data.frame(do.call('rbind', 
                                    strsplit(as.character(test$species), 
                                             split = "|", fixed = TRUE)))

test$species <- speciesSplit[,3]

colnames(test)

test <- test[,-c(1,4)]


unique(test$species)


test %>% 
  group_by(species, strand) %>%
  add_count(raw_position) %>%
  arrange(species, raw_position) %>%
  filter(species == "MEMB008C")
  
  
