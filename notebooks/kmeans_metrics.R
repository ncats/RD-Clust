library(tidyverse)
library(ggplot2)

kmean_metrics <- read.csv("data/processed/kmeans_model_metrics.csv")






summary(lm(scattering_criteria ~ D_EMBED*L_WALKS*K_DIM*N_WALKS,data=kmean_metrics))

p <- ggplot(filter(kmean_metrics,K_DIM==10),aes(N_WALKS,scattering_criteria,color=as.factor(L_WALKS))) + geom_line() + geom_point()
p <- p + theme_bw() + xlab("Number of walks") + ylab("Scattering Score")
p <- p + facet_wrap(D_EMBED ~ . ,scales='free',nrow=3,ncol=4)
p


View(kmean_metrics %>% group_by(D_EMBED) %>% mutate(sh_rank=rank(-silhouette_euclidean),
                                               db_rank=rank(davies_bouldin),
                                               ch_rank=rank(-calinski_harabasz)) %>% 
  mutate(rank_sum = sh_rank + db_rank +ch_rank) %>%  mutate(best_rank = rank(rank_sum)) %>% filter(best_rank < 6))


dim_sum <- kmean_metrics %>% group_by(D_EMBED) %>% summarize(scattering = mean(scattering_criteria))

p <- ggplot(filter(kmean_metrics,D_EMBED==32), aes(N_WALKS,scattering_criteria, color=as.factor(K_DIM))) + geom_line() + geom_point()
p <- p + theme_bw() + xlab("Number of Walks") + ylab("Cluster Score (scattering)")
p <- p + facet_wrap(L_WALKS ~ . ,nrow=2,ncol=4)
p


p <- ggplot(filter(kmean_metrics,D_EMBED==512), aes(N_WALKS,davies_bouldin, color=as.factor(K_DIM))) + geom_line() + geom_point()
p <- p + theme_bw() + xlab("Number of Walks") + ylab("Cluster Score (C-H)")
p <- p + facet_wrap(L_WALKS ~ . ,nrow=2,ncol=4)
p



p <- ggplot(filter(kmean_metrics,N_WALKS==80), aes(log2(D_EMBED),scattering_criteria, color=as.factor(L_WALKS))) + geom_line() + geom_point()
p <- p + theme_bw() + xlab("Embedding dimension") + ylab("Cluster Score (scattering)")
p <- p + facet_grid(K_DIM ~ .)
p


p <- ggplot(filter(kmean_metrics,N_WALKS==80), aes(log2(D_EMBED),scattering_criteria, color=as.factor(L_WALKS))) + geom_line() + geom_point()
p <- p + theme_bw() + xlab("Embedding dimension") + ylab("Cluster Score (scattering)")
p <- p + facet_grid(K_DIM ~ .)
p


p <- ggplot(filter(kmean_metrics,N_WALKS==80), aes(log2(D_EMBED),calinski_harabasz, color=as.factor(L_WALKS))) + geom_line() + geom_point()
p <- p + theme_bw() + xlab("Embedding dimension") + ylab("Cluster Score (calinski-harabasz)")
p <- p + facet_grid(K_DIM ~ .)
p


#kmean_metrics <- filter(kmean_metrics,D_EMBED==16)

p <- ggplot(kmean_metrics %>% group_by(N_WALKS,D_EMBED) %>% summarise(`Cluster Score` = mean(silhouette_euclidean)),
            aes(N_WALKS,`Cluster Score`)) + geom_line() + geom_point()
p <- p + theme_bw() + xlab("Walks per Disease") + ylab("Cluster Score")
p <- p + facet_wrap(D_EMBED ~ . ,scales='free',nrow=3,ncol=4)
p
#ggsave("fig/nwalks_sensitivity.png",p,width = 6,height=4,units='in')


df_summ <- kmean_metrics %>% group_by(D_EMBED) %>% mutate(max_ch = max(calinski_harabasz)) %>% 
  group_by(N_WALKS,D_EMBED,L_WALKS,K_DIM) %>%
  summarise(scattering_criteria = mean(scattering_criteria),
            calinski_harabasz = mean(calinski_harabasz)/max_ch) 

p <- ggplot(filter(kmean_metrics,K_DIM==10),aes(N_WALKS,scattering_criteria,color=as.factor(L_WALKS))) + geom_line() + geom_point()
p <- p + theme_bw() + xlab("Number of walks") + ylab("Scattering Score")
p <- p + facet_wrap(D_EMBED ~ . ,scales='free',nrow=3,ncol=4)
p

p <- ggplot(filter(kmean_metrics,K_DIM==10),aes(N_WALKS,calinski_harabasz,color=as.factor(L_WALKS))) + geom_line() + geom_point()
p <- p + theme_bw() + xlab("Number of walks") + ylab("calinski_harabasz Score")
p <- p + facet_wrap(D_EMBED ~ . ,scales='free',nrow=3,ncol=4)
p
