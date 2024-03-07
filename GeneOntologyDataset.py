from torch.utils.data import Dataset

class GeneOntologyDataset(Dataset):
    def __init__(self, gene_data, ontology_labels):
        self.gene_data = gene_data
        self.ontology_labels = ontology_labels

    def __len__(self):
        return len(self.gene_data)

    def __getitem__(self, idx):
        return self.gene_data[idx], self.ontology_labels[idx]
