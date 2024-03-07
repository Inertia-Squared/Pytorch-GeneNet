import numpy as np

from Neo4jDriver import Neo4jDriver
from neo4j import GraphDatabase
import csv

import psycopg2


# Sample possible values in the fixed order
TAGS = {
    "derived_biosample_lc11mtype": [
        "INTACT nuclei isolation",
        "TAPIN nuclei isolation",
        "biotic treatment",
        "cell cycle synchronized cells",
        "cell isolation",
        "chemical cell dissociation",
        "chemical treatment",
        "culture supernatant",
        "enzymatic cell dissociation",
        "gene perturbation",
        "light-dark cycle",
        "multi-individual sample",
        "physical treatment",
        "stably transfected cell line",
        "starvation",
        "targeted cell labeling",
        "tissue dissection",
        "transiently transfected cell line"
    ],
    "derived_biosample_lc2btype": [
        "immortalized cell line",
        "isolated cells",
        "isolated nuclei",
        "tissue",
        "whole organism"
    ],
    "derived_stage": [
        "adult stage",
        "blastoderm stage",
        "dorsal closure stage",
        "early extended germ band stage",
        "gastrula stage",
        "larval stage",
        "late embryonic stage",
        "late extended germ band stage",
        "oogenesis",
        "pharate adult stage",
        "pre-blastoderm stage",
        "prepupal stage",
        "pupal stage"
    ],
    "lc2btype": [
        "CAGE-Seq", "ChIP-Seq", "ChIP-chip", "DNase-Seq", "DamID-chip", "FAIRE-Seq",
        "RAMPAGE-Seq", "RIP-Seq", "RNA expression microarray", "RNA tiling array",
        "RNA-Seq", "RNA-protein interaction", "RNA-seq profile", "RNAi construct collection",
        "TSS identification", "aberration stock collection",
        "affinity purification and mass spectrometry", "allele collection", "analysis",
        "binding site identification", "cDNA library", "cell clustering analysis",
        "cell type-specific gene expression profile", "comparative genomic hybridization by array",
        "construct collection", "dsRNA amplicon collection", "editing site identification",
        "exon junction identification", "expression cluster", "expression clustering",
        "fly strain collection", "gene expression profile", "genome", "genome binding",
        "genome variation", "genomic clone collection", "immortalized cell line",
        "interactome", "isolated cells", "isolated nuclei", "microarray library",
        "poly(A) site identification", "protein mass spectrometry", "protein-protein interaction",
        "proteome", "reagent", "short RNA-Seq", "single-cell RNA-Seq",
        "single-nucleus RNA-Seq", "tissue", "transcriptional cell cluster",
        "transcriptome", "transgenic insertion collection", "umbrella project", "whole organism"
    ]
}


TOTAL_VALUES = 91


def calculate_pearson_correlation(primary_gene_expression, other_gene_expression):
    return np.corrcoef(primary_gene_expression, other_gene_expression)[0, 1]


# def construct_coexpression_network(primary_gene_array, random_sample_array):
#     coexpression_network = {}
#
#     for gene_value in :
#         correlation = calculate_pearson_correlation(primary_gene_value, gene_value)
#         coexpression_network[gene_value] = correlation
#
#     return coexpression_network

def get_metadata_from_postgresql(dataset):

    # Set up the connection
    conn = psycopg2.connect(
        dbname="FB2023_05",
        user="20724926",
        password=input(),
        host="lazebnik",
        port="5433"
    )

    # Create a cursor to execute SQL commands
    cur = conn.cursor()

    # Formulate the SQL query using the dataset
    query = f"""
    SELECT type.name AS type, c.name AS value 
    FROM library_cvterm AS lc 
    JOIN cvterm AS c ON lc.cvterm_id = c.cvterm_id 
    JOIN cv ON cv.cv_id = c.cv_id 
    JOIN library_cvtermprop AS lcp ON lc.library_cvterm_id = lcp.library_cvterm_id 
    JOIN cvterm AS type ON lcp.type_id = type.cvterm_id 
    WHERE type.name IN ('derived_stage', 'derived_biosample_lc2btype', 'lc2btype', 'derived_biosample_lc11mtype') 
    AND library_id = (
        SELECT library_id 
        FROM library_dbxref 
        WHERE dbxref_id = (
            SELECT dbxref_id 
            FROM dbxref 
            WHERE accession IN ('{dataset}')
        )
    );
    """
    cur.execute(query)
    results = cur.fetchall()

    # Close the connection
    conn.close()

    return results


def create_gene_dictionary_from_csv(csv_filename, primary_experiment_name, random_experiment_name):
    # Read the genes from the CSV
    with open(csv_filename, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header
        master_genes = {row[0]: {primary_experiment_name: None, random_experiment_name: None} for row in reader}

    # Query genes and values
    neo4j_driver_temp = Neo4jDriver()
    primary_experiment_data = neo4j_driver_temp.fetch_all_genes_with_property(primary_experiment_name)
    random_experiment_data = neo4j_driver_temp.fetch_all_genes_with_property(random_experiment_name)
    neo4j_driver_temp.close()

    # Create dictionaries for faster lookups
    primary_experiment_dict = dict(zip(primary_experiment_data[0], primary_experiment_data[1]))
    random_experiment_dict = dict(zip(random_experiment_data[0], random_experiment_data[1]))

    # Fill in the master_genes dictionary
    for gene in master_genes.keys():
        master_genes[gene][primary_experiment_name] = primary_experiment_dict.get(gene, None)
        master_genes[gene][random_experiment_name] = random_experiment_dict.get(gene, None)

    return master_genes


def one_hot_encode(tags_output):
    # Initialize encoding with zeros
    encoding = []

    for tag_name, possible_values in TAGS.items():
        tag_vector = [0] * len(possible_values)
        value = tags_output.get(tag_name)

        # Check if value is not in the list of possible values
        if value and value not in possible_values:
            raise ValueError(f"Unexpected value '{value}' for tag '{tag_name}'.")

        if value:
            index = possible_values.index(value)
            tag_vector[index] = 1

        encoding.extend(tag_vector)

    if len(encoding) != TOTAL_VALUES:
        raise ValueError(f"Incorrect encoding length. Expected {TOTAL_VALUES}, got {len(encoding)}.")

    return encoding


# # Test
tags_output = {
    "lc2btype": "RNA-seq profile",
    "derived_biosample_lc2btype": "whole organism",
    "derived_stage": "larval stage"
}
# print(one_hot_encode(tags_output))

neo4j_driver = Neo4jDriver()
neo4j_driver.write_fb_ids_to_csv('fb_ids.csv')

# Usage:
gene = neo4j_driver.get_random_fb_id()
print(gene)
sample1 = neo4j_driver.get_fblc_property_and_expression(gene, 'FBlc0000102')
sample2 = neo4j_driver.get_fblc_property_and_expression(gene, 'FBlc0003725')
print(sample1)
print(sample2)

metadata = get_metadata_from_postgresql('FBlc0000102')
print(metadata)
tags = {key: value for key, value in metadata}
# print(tags)
encoding = one_hot_encode(tags)
print(encoding)


sample1 = sample1[0]
sample2 = sample2[0]
dictionary = create_gene_dictionary_from_csv('fb_ids.csv', sample1, sample2)
# print(dictionary)


# print(all_genes_with_prop, all_genes_with_prop_exp)

neo4j_driver.close()
