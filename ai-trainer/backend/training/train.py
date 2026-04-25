"""
Training Script
Train the Temporal Transformer model
"""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, random_split
import numpy as np
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from model import create_model


class ExerciseDataset(Dataset):
    """Dataset for exercise sequences"""
    
    def __init__(self, data_dir: str):
        """
        Load dataset from directory
        
        Expected files:
            sequences.npy: (N, T, F)
            phase_labels.npy: (N,)
            error_labels.npy: (N, 3)
            score_labels.npy: (N,)
        """
        data_dir = Path(data_dir)
        
        self.sequences = np.load(data_dir / "sequences.npy")
        self.phase_labels = np.load(data_dir / "phase_labels.npy")
        self.error_labels = np.load(data_dir / "error_labels.npy")
        self.score_labels = np.load(data_dir / "score_labels.npy")
        
        print(f"Loaded dataset:")
        print(f"  Sequences: {self.sequences.shape}")
        print(f"  Phase labels: {self.phase_labels.shape}")
        print(f"  Error labels: {self.error_labels.shape}")
        print(f"  Score labels: {self.score_labels.shape}")
    
    def __len__(self):
        return len(self.sequences)
    
    def __getitem__(self, idx):
        return {
            'sequence': torch.from_numpy(self.sequences[idx]).float(),
            'phase': torch.tensor(self.phase_labels[idx], dtype=torch.long),
            'errors': torch.from_numpy(self.error_labels[idx]).float(),
            'score': torch.tensor(self.score_labels[idx], dtype=torch.float32)
        }


class Trainer:
    """Model trainer"""
    
    def __init__(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        val_loader: DataLoader,
        device: str = 'cpu',
        lr: float = 1e-3
    ):
        self.model = model.to(device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.device = device
        
        self.optimizer = optim.Adam(model.parameters(), lr=lr)
        
        # Loss functions
        self.phase_criterion = nn.CrossEntropyLoss()
        self.error_criterion = nn.BCEWithLogitsLoss()
        self.score_criterion = nn.MSELoss()
        
        self.best_val_loss = float('inf')
    
    def train_epoch(self):
        """Train for one epoch"""
        self.model.train()
        total_loss = 0
        phase_loss_sum = 0
        error_loss_sum = 0
        score_loss_sum = 0
        
        for batch in self.train_loader:
            sequences = batch['sequence'].to(self.device)
            phase_labels = batch['phase'].to(self.device)
            error_labels = batch['errors'].to(self.device)
            score_labels = batch['score'].to(self.device).unsqueeze(1)
            
            # Forward pass
            phase_logits, error_logits, score_pred = self.model(sequences)
            
            # Compute losses
            phase_loss = self.phase_criterion(phase_logits, phase_labels)
            error_loss = self.error_criterion(error_logits, error_labels)
            score_loss = self.score_criterion(score_pred, score_labels)
            
            # Combined loss
            loss = phase_loss + error_loss + score_loss
            
            # Backward pass
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
            phase_loss_sum += phase_loss.item()
            error_loss_sum += error_loss.item()
            score_loss_sum += score_loss.item()
        
        n_batches = len(self.train_loader)
        return {
            'total': total_loss / n_batches,
            'phase': phase_loss_sum / n_batches,
            'error': error_loss_sum / n_batches,
            'score': score_loss_sum / n_batches
        }
    
    def validate(self):
        """Validate model"""
        self.model.eval()
        total_loss = 0
        phase_loss_sum = 0
        error_loss_sum = 0
        score_loss_sum = 0
        
        with torch.no_grad():
            for batch in self.val_loader:
                sequences = batch['sequence'].to(self.device)
                phase_labels = batch['phase'].to(self.device)
                error_labels = batch['errors'].to(self.device)
                score_labels = batch['score'].to(self.device).unsqueeze(1)
                
                # Forward pass
                phase_logits, error_logits, score_pred = self.model(sequences)
                
                # Compute losses
                phase_loss = self.phase_criterion(phase_logits, phase_labels)
                error_loss = self.error_criterion(error_logits, error_labels)
                score_loss = self.score_criterion(score_pred, score_labels)
                
                loss = phase_loss + error_loss + score_loss
                
                total_loss += loss.item()
                phase_loss_sum += phase_loss.item()
                error_loss_sum += error_loss.item()
                score_loss_sum += score_loss.item()
        
        n_batches = len(self.val_loader)
        return {
            'total': total_loss / n_batches,
            'phase': phase_loss_sum / n_batches,
            'error': error_loss_sum / n_batches,
            'score': score_loss_sum / n_batches
        }
    
    def train(self, num_epochs: int, save_path: str):
        """Train model for multiple epochs"""
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        for epoch in range(num_epochs):
            train_losses = self.train_epoch()
            val_losses = self.validate()
            
            print(f"Epoch {epoch+1}/{num_epochs}")
            print(f"  Train - Total: {train_losses['total']:.4f}, "
                  f"Phase: {train_losses['phase']:.4f}, "
                  f"Error: {train_losses['error']:.4f}, "
                  f"Score: {train_losses['score']:.4f}")
            print(f"  Val   - Total: {val_losses['total']:.4f}, "
                  f"Phase: {val_losses['phase']:.4f}, "
                  f"Error: {val_losses['error']:.4f}, "
                  f"Score: {val_losses['score']:.4f}")
            
            # Save best model
            if val_losses['total'] < self.best_val_loss:
                self.best_val_loss = val_losses['total']
                torch.save({
                    'epoch': epoch,
                    'model_state_dict': self.model.state_dict(),
                    'optimizer_state_dict': self.optimizer.state_dict(),
                    'val_loss': val_losses['total']
                }, save_path)
                print(f"  Saved best model to {save_path}")


def main():
    """Main training function"""
    # Configuration
    DATA_DIR = "data/processed"
    MODEL_SAVE_PATH = "../../models/model.pt"
    BATCH_SIZE = 32
    NUM_EPOCHS = 30
    LEARNING_RATE = 1e-3
    VAL_SPLIT = 0.2
    
    # Load dataset
    print("Loading dataset...")
    dataset = ExerciseDataset(DATA_DIR)
    
    # Split into train/val
    val_size = int(len(dataset) * VAL_SPLIT)
    train_size = len(dataset) - val_size
    train_dataset, val_dataset = random_split(dataset, [train_size, val_size])
    
    print(f"Train size: {train_size}, Val size: {val_size}")
    
    # Create dataloaders
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)
    
    # Get input dimension from first batch
    sample_batch = next(iter(train_loader))
    input_dim = sample_batch['sequence'].shape[-1]
    print(f"Input dimension: {input_dim}")
    
    # Create model
    print("Creating model...")
    model = create_model(input_dim)
    
    # Count parameters
    num_params = sum(p.numel() for p in model.parameters())
    print(f"Model parameters: {num_params:,}")
    
    # Device
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")
    
    # Create trainer
    trainer = Trainer(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        device=device,
        lr=LEARNING_RATE
    )
    
    # Train
    print("\nStarting training...")
    trainer.train(num_epochs=NUM_EPOCHS, save_path=MODEL_SAVE_PATH)
    
    print("\nTraining complete!")


if __name__ == "__main__":
    main()
