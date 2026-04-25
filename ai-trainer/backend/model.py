"""
Temporal Transformer Model
Analyzes motion sequences for exercise classification and form analysis
"""
import torch
import torch.nn as nn
import math


class PositionalEncoding(nn.Module):
    """Positional encoding for temporal sequences"""
    
    def __init__(self, d_model: int, max_len: int = 5000):
        super().__init__()
        
        position = torch.arange(max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * (-math.log(10000.0) / d_model))
        
        pe = torch.zeros(max_len, 1, d_model)
        pe[:, 0, 0::2] = torch.sin(position * div_term)
        pe[:, 0, 1::2] = torch.cos(position * div_term)
        
        self.register_buffer('pe', pe)
    
    def forward(self, x):
        """
        Args:
            x: Tensor of shape (seq_len, batch_size, d_model)
        """
        x = x + self.pe[:x.size(0)]
        return x


class TemporalTransformer(nn.Module):
    """
    Temporal Transformer for exercise analysis
    
    Outputs:
        - Phase classification (4 classes: top, down, bottom, up)
        - Form errors (multi-label: knees_inward, insufficient_depth, back_bending)
        - Score regression (0-1)
    """
    
    def __init__(
        self,
        input_dim: int,
        d_model: int = 128,
        n_heads: int = 4,
        n_layers: int = 3,
        feedforward_dim: int = 256,
        num_phases: int = 4,
        num_errors: int = 3,
        dropout: float = 0.1
    ):
        super().__init__()
        
        self.input_dim = input_dim
        self.d_model = d_model
        
        # Input projection
        self.input_projection = nn.Linear(input_dim, d_model)
        
        # Positional encoding
        self.pos_encoder = PositionalEncoding(d_model)
        
        # Transformer encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=n_heads,
            dim_feedforward=feedforward_dim,
            dropout=dropout,
            batch_first=False
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=n_layers)
        
        # Output heads
        self.phase_head = nn.Sequential(
            nn.Linear(d_model, d_model // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(d_model // 2, num_phases)
        )
        
        self.error_head = nn.Sequential(
            nn.Linear(d_model, d_model // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(d_model // 2, num_errors)
        )
        
        self.score_head = nn.Sequential(
            nn.Linear(d_model, d_model // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(d_model // 2, 1),
            nn.Sigmoid()
        )
        
    def forward(self, x):
        """
        Args:
            x: Tensor of shape (batch_size, seq_len, input_dim)
            
        Returns:
            phase_logits: (batch_size, num_phases)
            error_logits: (batch_size, num_errors)
            score: (batch_size, 1)
        """
        # x: (batch, seq_len, input_dim)
        batch_size, seq_len, _ = x.shape
        
        # Project input
        x = self.input_projection(x)  # (batch, seq_len, d_model)
        
        # Transpose for transformer: (seq_len, batch, d_model)
        x = x.transpose(0, 1)
        
        # Add positional encoding
        x = self.pos_encoder(x)
        
        # Transformer encoding
        x = self.transformer_encoder(x)  # (seq_len, batch, d_model)
        
        # Global average pooling over time
        x = x.mean(dim=0)  # (batch, d_model)
        
        # Output heads
        phase_logits = self.phase_head(x)
        error_logits = self.error_head(x)
        score = self.score_head(x)
        
        return phase_logits, error_logits, score


def create_model(input_dim: int) -> TemporalTransformer:
    """Create model with default configuration"""
    return TemporalTransformer(
        input_dim=input_dim,
        d_model=128,
        n_heads=4,
        n_layers=3,
        feedforward_dim=256,
        num_phases=4,
        num_errors=3,
        dropout=0.1
    )
