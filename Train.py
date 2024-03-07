import torch
import torch.nn as nn
import torch.optim as optim


def train_model(model, dataloader, num_epochs=20):
    criterion = nn.CrossEntropyLoss()  # or another appropriate loss function
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    for epoch in range(num_epochs):
        for gene_data_batch, ontology_labels_batch in dataloader:
            optimizer.zero_grad()
            outputs = model(gene_data_batch)
            loss = sum(criterion(output, label) for output, label in zip(outputs, ontology_labels_batch))
            loss.backward()
            optimizer.step()
        # Optionally print loss, accuracy, etc.
        print(f'Epoch {epoch + 1}/{num_epochs}, Loss: {loss.item()}')

    return model  # Return the trained model
