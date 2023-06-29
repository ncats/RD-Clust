#!/usr/bin/env python3

import sys
import os
from pathlib import Path
import gensim


def main():
    
    walk_file = sys.argv[1]
    vector_size = int(sys.argv[2])
    context_size = int(sys.argv[3])
    model_file_path = sys.argv[4]
    project_dir = Path(__file__).resolve().parents[2]

    sentences=gensim.models.word2vec.LineSentence(project_dir / walk_file)
    model=gensim.models.Word2Vec(sentences,sg=1, 
                                    min_count=1, 
                                    vector_size=vector_size, 
                                    window=context_size,
                                    epochs=15,
                                    workers=4)
    model.save(model_file_path) 

if __name__=="__main__":
    main()
