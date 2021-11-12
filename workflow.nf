#!/usr/bin/env nextflow

project_dir = projectDir

ontologies = Channel.from('go','hp')

process get_ontologies {

    
    //executor 'slurm'
    //memory '8 GB'   

    input:
    val ont from ontologies

    output:
    file 'reasoned.obo'
    val true into got_ont

    publishDir 'data', saveAs: {filename -> "$ont-reasoned.obo"}

    script:
    """
    ${project_dir}/third_party/bin/robot reason --reasoner ELK --annotate-inferred-axioms true --input ${project_dir}/data/${ont}.owl --output reasoned.owl
    ${project_dir}/third_party/bin/robot convert --check false --input reasoned.owl --format obo --output reasoned.obo
    """
}

process contruct_graph {
   
    //executor 'slurm'
    //memory '16 GB'

    input:
    val flag from got_ont.collect()

    output:
    val true into built_graph
    
    script:
    """
    python ${project_dir}/src/data/construct_graph.py data/go-reasoned.obo data/hp-reasoned.obo 
    """

}


walk_lengths = Channel.from()

process generate_walks {
    //executor 'slurm'
    //memory '8 GB'

    input:
    val flag from built_graph

    script:
    """
    python ${project_dir}/src/model/generate_walks.py \
    ${project_dir}/data/disease_ontograph.pkl \

    """

}


