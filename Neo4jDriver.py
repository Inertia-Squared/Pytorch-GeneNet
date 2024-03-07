import csv

from neo4j import GraphDatabase
import random


class Neo4jDriver:
    def __init__(self):
        self.uri = "bolt://pilgrim:7687"
        self.driver = GraphDatabase.driver(self.uri, auth=("neo4j", "neo4gene"))

    def close(self):
        self.driver.close()

    def run_query(self, query, parameters=None):
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return [record for record in result]

    def get_all_fb_ids(self):
        query = """
            MATCH (g:Gene)
            RETURN g.fb_id AS fb_id
            ORDER BY g.fb_id
            """
        return self.run_query(query)

    def get_random_fb_id(self):
        query = """
        MATCH (g:Gene)
        RETURN g.fb_id AS fb_id
        ORDER BY rand() LIMIT 1
        """
        return [record[0] for record in self.run_query(query)][0]

    def write_fb_ids_to_csv(self, filename):
        results = self.get_all_fb_ids()
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['fb_id'])  # header
            for record in results:
                writer.writerow([record['fb_id']])

    def get_fblc_properties(self, gene_name=None):
        if gene_name:
            query = f"""
            MATCH (g:Gene {{fb_id: "{gene_name}"}})
            WHERE ANY(prop IN keys(g) WHERE prop STARTS WITH "FBlc")
            RETURN properties(g) AS gene_properties
            LIMIT 1
            """
        else:
            query = f"""
            MATCH (g:Gene) 
            WHERE ANY(prop IN keys(g) WHERE prop STARTS WITH "FBlc")
            RETURN properties(g) AS gene_properties
            ORDER BY rand()
            LIMIT 1
            """
        return self.run_query(query)

    def get_fblc_property_and_expression(self, gene_name=None, property_name=None):
        results = self.get_fblc_properties(gene_name)
        for record in results:
            gene_properties = record['gene_properties']
            if gene_properties:
                selected_property = property_name if property_name else random.choice(
                    [prop for prop in gene_properties.keys() if prop.startswith("FBlc")])
                return selected_property, gene_properties[selected_property]
                # If gene is specified, this gives us a free query for its expression
        return None, None

    def fetch_all_genes_with_property(self, prop):
        query = f"""
        MATCH (g:Gene)
        WHERE (g.{prop}) IS NOT NULL
        RETURN g.{prop} AS gene_value, g.fb_id AS fb_id
        """

        results = self.run_query(query)
        return [record['fb_id'] for record in results], [record['gene_value'] for record in results]

    def test_fetch_specified_gene(self):
        gene_name = 'FBgn0000449'
        property_key, property_value = self.get_fblc_property_and_expression(gene_name)
        assert property_key is not None
        assert property_value is not None
        print(f"For gene {gene_name}, property key: {property_key}, property value: {property_value}")

    def test_fetch_random_gene(self):
        property_key, property_value = self.get_fblc_property_and_expression()
        assert property_key is not None
        assert property_value is not None
        print(f"Random gene property key: {property_key}, property value: {property_value}")

    def test_fetch_all_sample_genes(self):
        sample_genes = ['FBgn0000449', 'FBgn0000451', 'FBgn0000454']
        for gene_name in sample_genes:
            property_key, property_value = self.get_fblc_property_and_expression(gene_name)
            assert property_key is not None
            assert property_value is not None
            print(f"For gene {gene_name}, property key: {property_key}, property value: {property_value}")

    def test_fetch_related_genes(self):
        property_key, property_value = self.get_fblc_property_and_expression()
        result = self.fetch_all_genes_with_property(f"{property_key}")
        assert property_key is not None
        assert property_value is not None
        print(
            f"For random gene property key: {property_key}, "
            f"returned filled {len(result[0]) / 8461 * 100}% ({len(result[0])})")


validate = False
if validate:
    Neo4jDriver = Neo4jDriver()
    Neo4jDriver.test_fetch_specified_gene()
    Neo4jDriver.test_fetch_random_gene()
    Neo4jDriver.test_fetch_all_sample_genes()
    for i in range(1, 10):
        Neo4jDriver.test_fetch_related_genes()
