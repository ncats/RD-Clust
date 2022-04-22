library(tidyverse)
library(ggplot2)
library(cowplot)

kmean_metrics <- read.csv("../data/processed/kmeans_model_metrics.csv") %>% filter(N_WALKS>20)

summary(kmean_metrics)


#not in perfect agreement
cor(kmean_metrics[,c('silhouette_euclidean','davies_bouldin','calinski_harabasz')])

kmean_metrics <- kmean_metrics %>% mutate(silhouette_rank = rank(-silhouette_euclidean),
                                          silhouette_scaled = scale(silhouette_euclidean),
                         db_rank = rank(davies_bouldin),
                         db_scaled = scale(-davies_bouldin),
                         ch_rank = rank(-calinski_harabasz),
                         ch_scaled= scale(calinski_harabasz)) %>% 
  mutate(rank_mean = (silhouette_rank + db_rank + ch_rank)/3,
         scaled_mean = (silhouette_scaled + db_scaled + ch_scaled)/3)

kmean_metrics_long <- kmean_metrics %>% 
  select(N_WALKS,L_WALKS,D_EMBED,K_DIM,silhouette_euclidean,davies_bouldin,calinski_harabasz) %>% 
  gather("metric","value",silhouette_euclidean:calinski_harabasz)

#Indices over dimension
p <- ggplot(filter(kmean_metrics_long,L_WALKS %in% c(25,100,200,250),K_DIM %in% c(6,10,16,20)),
            aes(N_WALKS,value,color=as.factor(L_WALKS))) + geom_line() + geom_point()
p <- p + theme_bw() + xlab("Walks per disease") + ylab("Clustering metric")
p <- p  + facet_grid(metric ~ K_DIM,labeller = label_both,scales='free_y') + guides(color=guide_legend(title='Walk Length'))
p
ggsave("../fig/metrics_nwalks.png",p,dpi=300,width=8.5,height=6,units = "in")

p <- ggplot(filter(kmean_metrics_long,N_WALKS %in% c(50,150,225,250),K_DIM %in% c(6,10,16,20)),
            aes(L_WALKS,value,color=as.factor(N_WALKS))) + geom_line() + geom_point()
p <- p + theme_bw() + xlab("Length of walk") + ylab("Clustering metric")
p <- p  + facet_grid(metric ~ K_DIM,labeller = label_both,scales='free_y') + guides(color=guide_legend(title='Walks per disease'))
p
ggsave("../fig/metrics_lwalks.png",p,dpi=300,width=8.5,height=6,units = "in")

p <- ggplot(filter(kmean_metrics_long,N_WALKS %in% c(50,150,250),L_WALKS %in% c(25,100,200,250)),
            aes(K_DIM,value,color=as.factor(N_WALKS))) + geom_line() + geom_point()
p <- p + theme_bw() + xlab("Embedding context window") + ylab("Clustering metric")
p <- p  + facet_grid(metric ~ L_WALKS,labeller = label_both,scales='free_y') + guides(color=guide_legend(title='Walks per disease'))
p
ggsave("../fig/metrics_kdim.png",p,dpi=300,width=8.5,height=6,units = "in")


n_walk_summ <- kmean_metrics %>% group_by(N_WALKS) %>% summarize(scaled_mean=mean(scaled_mean))

l_walk_summ <- kmean_metrics %>% group_by(L_WALKS) %>% summarize(scaled_mean=mean(scaled_mean))

k_dim_summ <- kmean_metrics %>% group_by(K_DIM) %>% summarize(scaled_mean=mean(scaled_mean))


A <- ggplot(n_walk_summ,aes(N_WALKS,scaled_mean)) + geom_line() + geom_point()
A <- A + theme_bw() + xlab("Walks per disease") + ylab("Average index z-score")

B <- ggplot(l_walk_summ,aes(L_WALKS,scaled_mean)) + geom_line() + geom_point()
B <- B + theme_bw() + xlab("Length of walks") + ylab("Average index z-score")

C <- ggplot(k_dim_summ,aes(K_DIM,scaled_mean)) + geom_line() + geom_point()
C <- C + theme_bw() + xlab("Embedding context window") + ylab("Average index z-score")


plot_grid(A,B,C,nrow = 1)

#Sensitivity analysis
formatted_data <- data.frame(scale(kmean_metrics[,c("scaled_mean","L_WALKS","K_DIM","N_WALKS")]))
formatted_data <- setNames(formatted_data,c("Average index z-score","Walk Length","Context Window","Walks per Disease"))

s_rc <- coef(lm(`Average index z-score` ~ `Walk Length`*`Context Window`*`Walks per Disease`,
                data=formatted_data))[-1]

names(s_rc) <- gsub(':',' * ',gsub('`','',names(s_rc)))

src_data <- data.frame(par=names(s_rc),src=as.numeric(s_rc)) %>% arrange(src) %>% mutate(sign=ifelse(src>0,1,0))

src_data$par <- factor(src_data$par,levels=src_data$par[order(src_data$src)])

p <- ggplot(src_data,aes(par,src,fill=as.factor(sign))) +
  geom_col() + coord_flip() + scale_fill_manual(values=c("red","blue"))
p <- p + ylab("Standarized regression coefficient") + xlab("") 
p <- p + theme_classic() + guides(fill="none")
p
ggsave("fig/standardized_regression_coef.png",p,dpi=150,width=6,height=4,units = "in")


