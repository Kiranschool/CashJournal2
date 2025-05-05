import fasttext
import json
import os
from django.conf import settings

def train_fasttext_model():
    """Train a FastText model on the transaction dataset"""
    # Load dataset
    dataset_path = os.path.join(settings.BASE_DIR, 'core', 'data', 'transaction_dataset.json')
    with open(dataset_path, 'r') as f:
        data = json.load(f)
    
    # Prepare training data
    train_data = []
    for transaction in data['transactions']:
        # Add the main description
        train_data.append(f"__label__{transaction['category']} {transaction['description']}")
        
        # Add variations with keywords
        for keyword in transaction['keywords']:
            train_data.append(f"__label__{transaction['category']} {keyword}")
    
    # Save training data to file
    train_file = os.path.join(settings.BASE_DIR, 'core', 'models', 'train.txt')
    os.makedirs(os.path.dirname(train_file), exist_ok=True)
    with open(train_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(train_data))
    
    # Train the model
    model = fasttext.train_supervised(
        input=train_file,
        lr=0.1,
        epoch=25,
        wordNgrams=2,
        verbose=2,
        minCount=1,
        loss='softmax'
    )
    
    # Save the model
    model_path = os.path.join(settings.BASE_DIR, 'core', 'models', 'transaction_model.bin')
    model.save_model(model_path)
    
    return model

if __name__ == '__main__':
    train_fasttext_model() 