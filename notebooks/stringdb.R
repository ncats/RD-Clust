library(STRINGdb)
library(tidyverse)
library(ontologyIndex)

data(go)

gene_enrichment_resuts <- read_csv("../data/processed/gard_gene_enrichment_results.csv")
gene_enrichment_fdr <- gene_enrichment_resuts %>% 
  filter(perm_q<=0.01)

unique_genes_cluster <- gene_enrichment_fdr
  select(Gene_Symbol,HGNC,Gene_ID,Cluster,perm_p,perm_q) %>% 
  unique()


single_cluster_genes <- unique_genes_cluster %>% filter(Cluster==28)

string_db <- STRINGdb$new( version="11.5", species=9606,score_threshold=200, network_type="full")
string_db$plot_network( single_cluster_genes$Gene_Symbol )


observed_ppi_enrichment <- data.frame(do.call("rbind",
                                   lapply(unique(unique_genes_cluster$Cluster),function(i){
                                     
                                     single_cluster_genes <- unique_genes_cluster %>% filter(Cluster==i)
                                     ppi <- string_db$get_ppi_enrichment( single_cluster_genes$Gene_Symbol )
                                     ppi[['Cluster']] <-i
                                     return(ppi)
                                   })
))


observed_ppi_enrichment$enrichment[observed_ppi_enrichment$enrichment==0] = 5e-17

perm_unique_genes_cluster <- unique_genes_cluster

all_perm_ppi <- data.frame()

for (p in c(1:10)){
  
  perm_unique_genes_cluster$Cluster <- sample(perm_unique_genes_cluster$Cluster)
  
  perm_ppi_enrichment <- data.frame(do.call("rbind",
                                                lapply(unique(perm_unique_genes_cluster$Cluster),function(i){
                                                  
                                                  single_cluster_genes <- perm_unique_genes_cluster %>% filter(Cluster==i)
                                                  ppi <- string_db$get_ppi_enrichment( single_cluster_genes$Gene_Symbol )
                                                  ppi[['Cluster']] <-i
                                                  return(ppi)
                                                })
  ))
  all_perm_ppi <- rbind(all_perm_ppi,perm_ppi_enrichment)
}

all_perm_ppi$enrichment[all_perm_ppi$enrichment==0] = 5e-17


enrich_logp <- rbind(
  data.frame(logp = -log10(as.numeric(observed_ppi_enrichment$enrichment)),Cluster=as.numeric(observed_ppi_enrichment$Cluster),type='observed'),
  data.frame(logp = -log10(as.numeric(all_perm_ppi$enrichment)),Cluster=as.numeric(all_perm_ppi$Cluster),type='permuted')
)

scale_perc<- function(x){
  return(1 - scale(x,center=min(x,na.rm=TRUE),scale=diff(range(x,na.rm=TRUE))))
  }

enrich_logp <- enrich_logp %>% group_by(Cluster) %>% mutate(within_clust_percentile =scale_perc(logp))

enrich_logp %>% filter(type=='observed',logp==-log10(5e-17))


p <- ggplot(enrich_logp,aes(logp,fill=type)) + geom_histogram(aes(y = ..density..),position="dodge2") + theme_classic()
p
###
sig_ppi_cluster <- observed_ppi_enrichment$Cluster[observed_ppi_enrichment$enrichment==5e-17]

observed_go_enrichment <- data.frame(do.call("rbind",
                                              lapply(sig_ppi_cluster,function(i){
                                                
                                                single_cluster_genes <- unique_genes_cluster %>% filter(Cluster==i)
                                                go_enr <- string_db$get_enrichment( single_cluster_genes$Gene_Symbol )
                                                go_enr['Cluster'] <- i
                                                return(go_enr)
                                              })
))


write_csv(observed_go_enrichment,"../data/processed/stringdb_enriched_terms.csv")

###
interesting_clusters <- c(3,17,20,28,35)

interesting_cluster_go_terms <- observed_go_enrichment %>% 
  filter(Cluster %in% interesting_clusters,
         category %in% c("Function","Process"),
         fdr <=0.0001) %>% 
  group_by(Cluster) %>% 
  filter(term %in% minimal_set(go,term)) %>%
  summarize(GO_terms = str_c(unique(description),collapse='; '))

interesting_cluster_gene_disease <- gene_enrichment_fdr %>% 
  filter(Cluster %in% interesting_clusters) %>%
  group_by(Cluster) %>%
  summarize(Diseases = str_c(unique(GARD_Disease),collapse='; '),
            Genes = str_c(unique(Gene_Symbol),collapse='; '))


disease_gene_go <- merge(interesting_cluster_gene_disease,interesting_cluster_go_terms)

write_delim(disease_gene_go,"../data/processed/interesting_cluster_disease_gene_go_table.tsv",delim="\t",quote='all')

