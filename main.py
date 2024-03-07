import torch
from torch.utils.data import DataLoader

from DataPreprocessing import one_hot_encode
from OntologyNetwork import OntologyNetwork
from GeneOntologyDataset import GeneOntologyDataset
from Train import train_model  # Importing the training function from Train.py


def load_data():
    gene_data, ontology_labels = ..., ...

    # Fetch metadata for each sample
    metadata = ...  # Code to fetch metadata for each sample
    encoded_metadata = [one_hot_encode(m) for m in metadata]  # Use the one_hot_encode function

    # Concatenate one-hot encoded metadata to gene_data
    gene_data = [torch.cat((gd, torch.tensor(em))) for gd, em in zip(gene_data, encoded_metadata)]

    return gene_data, ontology_labels


def create_dataloaders(gene_data, ontology_labels):
    dataset = GeneOntologyDataset(gene_data, ontology_labels)
    dataloader = DataLoader(dataset, batch_size=32, shuffle=True)
    return dataloader


def evaluate_model(model):
    # Blackbox: replace with your model evaluation code
    pass


def main():
    gene_data, ontology_labels = load_data()
    dataloader = create_dataloaders(gene_data, ontology_labels)

    # Assume n is the size of gene coexpression data
    n = ...  # Set your value for n
    metadata_size = 91
    model = OntologyNetwork(gene_expression_size=1, gene_coexpression_size=n, metadata_size=metadata_size,
                            hidden_size=128)

    trained_model = train_model(model, dataloader)  # Training the model
    evaluate_model(trained_model)  # Evaluating the model

    # Model Saving/Loading
    torch.save(trained_model.state_dict(), 'model.pth')  # Save model parameters to file
    trained_model.load_state_dict(torch.load('model.pth'))  # Load model parameters from file


if __name__ == "__main__":
    main()
