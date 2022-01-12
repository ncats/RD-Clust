library(tidyverse)
library(ggplot2)

kmean_metrics <- read.csv("data/processed/kmeans_model_metrics.csv")

kmean_metrics <- filter(kmean_metrics,D_EMBED==16)

p <- ggplot(kmean_metrics %>% group_by(N_WALKS) %>% summarise(`Cluster Score` = mean(sdbw_euclidean)),
            aes(N_WALKS,`Cluster Score`)) + geom_line() + geom_point()
p <- p + theme_bw() + xlab("Walks per Disease") + ylab("Cluster Score (SDB-w)")
ggsave("fig/nwalks_sensitivity.png",p,width = 6,height=4,units='in')

p <- ggplot(kmean_metrics %>% group_by(L_WALKS) %>% summarise(`Cluster Score` = mean(sdbw_euclidean)),
            aes(L_WALKS,`Cluster Score`)) + geom_line() + geom_point()
p <- p + theme_bw() + xlab("Walk Length") + ylab("Cluster Score (SDB-w)")
ggsave("fig/lwalks_sensitivity.png",p,width = 6,height=4,units='in')

p <- ggplot(kmean_metrics %>% group_by(K_DIM) %>% summarise(`Cluster Score` = mean(sdbw_euclidean)),
            aes(K_DIM,`Cluster Score`)) + geom_line() + geom_point()
p <- p + theme_bw() + xlab("Context Window") + ylab("Cluster Score (SDB-w)")
ggsave("fig/kdim_sensitivity.png",p,width = 6,height=4,units='in')
