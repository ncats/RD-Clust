library(tidyverse)
library(ggplot2)

kmean_metrics <- read.csv("data/processed/kmeans_model_metrics.csv")


formatted_data <- data.frame(scale(kmean_metrics[,c("scattering_criteria","D_EMBED","L_WALKS","K_DIM","N_WALKS")]))
formatted_data <- setNames(formatted_data,c("Scattering Score","Embedding Dimension","Walk Length","Context Window","Walks per Disease"))
s_rc <- coef(lm(`Scattering Score` ~ `Embedding Dimension`*`Walk Length`*`Context Window`*`Walks per Disease`,
           data=formatted_data))[2:11]

names(s_rc) <- gsub(':',' * ',gsub('`','',names(s_rc)))

src_data <- data.frame(par=names(s_rc),src=as.numeric(s_rc)) %>% arrange(src) %>% mutate(sign=ifelse(src>0,1,0))

src_data$par <- factor(src_data$par,levels=src_data$par[order(src_data$src)])

p <- ggplot(src_data,aes(par,src,fill=as.factor(sign))) +
  geom_col() + coord_flip() + scale_fill_manual(values=c("red","blue"))
p <- p + ylab("Standarized regression coefficient") + xlab("") 
p <- p + theme_classic() + guides(fill="none")
ggsave("fig/standardized_regression_coef.png",p,dpi=150,width=6,height=4,units = "in")

#Indices over dimension
p <- ggplot(filter(kmean_metrics,N_WALKS %in% c(20,40,60,80),K_DIM %in% c(8,12,16),L_WALKS %in% c(25,50,100,150,200)),
            aes(D_EMBED,(scattering_criteria),color=as.factor(L_WALKS))) + geom_line() + geom_point()
p <- p + scale_x_continuous(trans='log2',breaks=c(8,16,32,64,128,256,512),labels=c(8,16,32,64,128,256,512))
p <- p + theme_bw() + xlab("Embedding Dimension") + ylab("Scattering Score")
p <- p  + facet_grid(K_DIM ~ N_WALKS,labeller = label_both) + guides(color=guide_legend(title='Walk Length'))
ggsave("fig/scattering_score.png",p,dpi=300,width=10,height=6,units = "in")




p <- ggplot(filter(kmean_metrics,D_EMBED>=16,N_WALKS %in% c(20,40,60,80),K_DIM %in% c(8,12,16)),
            aes(log2(D_EMBED),(davies_bouldin),color=as.factor(L_WALKS))) + geom_line() + geom_point()
p <- p + theme_bw() + xlab("log2(d)") + ylab("Davies-Bouldin Score")
p  + facet_grid(K_DIM ~ N_WALKS)


p <- ggplot(filter(kmean_metrics,D_EMBED>=16,N_WALKS %in% c(20,40,60,80),K_DIM %in% c(8,12,16)),
            aes(log2(D_EMBED),(calinski_harabasz),color=as.factor(L_WALKS))) + geom_line() + geom_point()
p <- p + theme_bw() + xlab("log2(d)") + ylab("Calinksi-Harabasz Score")
p  + facet_grid(K_DIM ~ N_WALKS)


#Indices over number of walks
p <- ggplot(filter(kmean_metrics,D_EMBED>=16,D_EMBED %in% c(16,32,64,128,256),K_DIM %in% c(8,12,16)),
            aes((N_WALKS),(scattering_criteria),color=as.factor(L_WALKS))) + geom_line() + geom_point()
p <- p + theme_bw() + xlab("log2(d)") + ylab("Scattering Score")
p  + facet_grid(D_EMBED ~ K_DIM )


p <- ggplot(filter(kmean_metrics,D_EMBED>=16,N_WALKS %in% c(20,40,60,80),K_DIM %in% c(8,12,16)),
            aes(log2(D_EMBED),(davies_bouldin),color=as.factor(L_WALKS))) + geom_line() + geom_point()
p <- p + theme_bw() + xlab("log2(d)") + ylab("Davies-Bouldin Score")
p  + facet_grid(K_DIM ~ N_WALKS)


p <- ggplot(filter(kmean_metrics,D_EMBED>=16,N_WALKS %in% c(20,40,60,80),K_DIM %in% c(8,12,16)),
            aes(log2(D_EMBED),(calinski_harabasz),color=as.factor(L_WALKS))) + geom_line() + geom_point()
p <- p + theme_bw() + xlab("log2(d)") + ylab("Calinksi-Harabasz Score")
p  + facet_grid(K_DIM ~ N_WALKS)