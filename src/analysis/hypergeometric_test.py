import pandas as pd
from scipy import stats
from pathlib import Path
from joblib import Parallel, delayed


def hypergeom_p(row,walk_annotation_counts):
   M = walk_annotation_counts['Count'].sum()
   k = row['Count']
   N = walk_annotation_counts[walk_annotation_counts['Cluster']==row['Cluster']]['Count'].sum()
   n = walk_annotation_counts[walk_annotation_counts['Annotation']==row['Annotation']]['Count'].sum()
   row['M'] = M
   row['n'] = n
   row['N'] = N
   row['pv'] = stats.hypergeom.sf(k,M,n,N)
   return row

def main():
   project_dir = Path(__file__).resolve().parents[2]
   walk_annot_file = sys.argv[1]

   walk_annotations = pd.read_table(project_dir / walk_annot_file,index_col=None)
   walk_annotation_counts = walk_annotations.groupby(['Cluster','Annotation']).agg({'Count':sum}).reset_index()

   walk_results = Parallel(n_jobs=-1)(delayed(hypergeom_p)(row,walk_annotation_counts) for i,row in walk_annotation_counts.iterrows() )

   pd.DataFrame(walk_results).to_csv(project_dir / 'data/processed/walk_annotation_enrichment.csv',index=False)

if __name__=="__main__":
   main()
    