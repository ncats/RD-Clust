#!/usr/bin/env python3

import sys
import os
from pathlib import Path
import gensim


def main():
    
    walk_dir = sys.argv[1]
    vector_size = int(sys.argv[2])
    context_size = int(sys.argv[3])
    project_dir = Path(__file__).resolve().parents[2]

    walk_files = os.listdir(project_dir / walk_dir)

    for wfile in walk_files:
        walks_per_disease = wfile.strip('.txt').split('_')[1]
        walk_len = wfile.strip('.txt').split('_')[2]
        model_file_path = str(project_dir / 'data/embeddings/ontograph_embed_{0}_{1}_D{2}_K{3}.model'.format(walks_per_disease,walk_len,vector_size,context_size))
        print(model_file_path)
        sentences=gensim.models.word2vec.LineSentence(project_dir / walk_dir / wfile)
        model=gensim.models.Word2Vec(sentences,sg=1, 
                                     min_count=1, 
                                     vector_size=vector_size, 
                                     window=context_size,
                                     epochs=10,
                                     workers=4)
        model.save(model_file_path) 

if __name__=="__main__":
    main()
