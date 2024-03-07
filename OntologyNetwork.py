import torch
import torch.nn as nn

class OntologyNetwork(nn.Module):
    def __init__(self, gene_expression_size, gene_coexpression_size, metadata_size, hidden_size):
        super(OntologyNetwork, self).__init__()

        self.input_size = gene_expression_size + gene_coexpression_size + metadata_size

        # Level 1: Top-level classes
        self.level1 = nn.Sequential(
            nn.Linear(self.input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, 151),  # 151 top-level classes
            nn.Softmax(dim=1)
        )

        # Level 2: Second-level classes
        self.level2 = nn.Sequential(
            nn.Linear(151 + self.input_size, hidden_size),  # Input from previous level + original input
            nn.ReLU(),
            nn.Linear(hidden_size, 21),  # 21 second-level classes
            nn.Softmax(dim=1)
        )

        # Level 3: Third-level classes
        self.level3 = nn.Sequential(
            nn.Linear(21 + self.input_size, hidden_size),  # Input from previous level + original input
            nn.ReLU(),
            nn.Linear(hidden_size, 1),  # 1 third-level class
            nn.Sigmoid()  # Since there's only one class, we use Sigmoid here
        )

    def forward(self, x):
        gene_expression = x[:, :1]  # Assuming gene expression is the first feature
        gene_coexpression = x[:, 1:]  # Assuming gene coexpression features follow

        # Combine gene expression and gene coexpression for processing
        combined_input = torch.cat((gene_expression, gene_coexpression), dim=1)

        x1 = self.level1(combined_input)
        x2 = self.level2(torch.cat((x1, combined_input), dim=1))  # Concatenating output from previous level with original input
        x3 = self.level3(torch.cat((x2, combined_input), dim=1))  # Concatenating output from previous level with original input

        return x1, x2, x3
