import argparse
import json
import random
from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, models, transforms

DATA_DIR = Path('data/skin_types')
MODEL_SAVE_PATH = Path('app/static/models/skin_classifier.pth')
CLASS_NAMES = ['oily', 'dry', 'normal', 'acne']
DEFAULT_ARCHITECTURE = 'efficientnet_v2_s'
IMAGE_SIZE = 224


def seed_everything(seed=42):
    random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def build_model(architecture=DEFAULT_ARCHITECTURE, num_classes=len(CLASS_NAMES), pretrained=True):
    architecture = (architecture or DEFAULT_ARCHITECTURE).lower()

    if architecture == 'mobilenet_v3_large':
        weights = models.MobileNet_V3_Large_Weights.DEFAULT if pretrained else None
        model = models.mobilenet_v3_large(weights=weights)
        for param in model.features.parameters():
            param.requires_grad = False
        in_features = model.classifier[-1].in_features
        model.classifier[-1] = nn.Sequential(
            nn.Linear(in_features, 256),
            nn.Hardswish(),
            nn.Dropout(0.2),
            nn.Linear(256, num_classes),
        )
        return model

    if architecture == 'mobilenet_v2':
        weights = models.MobileNet_V2_Weights.DEFAULT if pretrained else None
        model = models.mobilenet_v2(weights=weights)
        for param in model.features.parameters():
            param.requires_grad = False
        model.classifier[1] = nn.Sequential(
            nn.Linear(model.last_channel, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, num_classes),
        )
        return model

    weights = models.EfficientNet_V2_S_Weights.DEFAULT if pretrained else None
    model = models.efficientnet_v2_s(weights=weights)
    for param in model.features.parameters():
        param.requires_grad = False
    in_features = model.classifier[-1].in_features
    model.classifier[-1] = nn.Sequential(
        nn.Linear(in_features, 256),
        nn.SiLU(),
        nn.Dropout(0.25),
        nn.Linear(256, num_classes),
    )
    return model


def build_transforms():
    train_transform = transforms.Compose([
        transforms.RandomResizedCrop(IMAGE_SIZE, scale=(0.80, 1.0)),
        transforms.RandomHorizontalFlip(),
        transforms.ColorJitter(brightness=0.12, contrast=0.12, saturation=0.08),
        transforms.RandomAffine(degrees=8, translate=(0.03, 0.03), scale=(0.97, 1.03)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    eval_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(IMAGE_SIZE),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    return {'train': train_transform, 'val': eval_transform, 'test': eval_transform}


def expected_structure(root):
    return {
        split: [str(root / split / label) for label in CLASS_NAMES]
        for split in ('train', 'val', 'test')
    }


def save_checkpoint(model, class_names, save_path, architecture, metrics, dataset_root):
    save_path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint = {
        'architecture': architecture,
        'class_names': [name.replace('_', ' ').title() for name in class_names],
        'image_size': IMAGE_SIZE,
        'model_state_dict': model.state_dict(),
        'metadata': {
            'status': 'trained' if metrics.get('history') else 'bootstrap',
            'dataset_root': str(dataset_root),
            'best_val_acc': metrics.get('best_val_acc'),
            'best_val_loss': metrics.get('best_val_loss'),
            'test_acc': metrics.get('test_acc'),
            'epochs': metrics.get('epochs'),
            'history': metrics.get('history', []),
            'expected_structure': expected_structure(Path(dataset_root)),
        },
    }
    torch.save(checkpoint, save_path)


def bootstrap_model(save_path, architecture, dataset_root):
    model = build_model(architecture=architecture, pretrained=True)
    save_checkpoint(
        model=model.cpu(),
        class_names=CLASS_NAMES,
        save_path=save_path,
        architecture=architecture,
        metrics={'history': [], 'epochs': 0},
        dataset_root=dataset_root,
    )
    print(f"Saved bootstrap checkpoint to {save_path}")


def split_exists(data_dir, split):
    return (data_dir / split).exists()


def create_dataloaders(data_dir, batch_size):
    transforms_map = build_transforms()
    active_splits = ['train', 'val']
    if split_exists(data_dir, 'test'):
        active_splits.append('test')

    image_datasets = {
        split: datasets.ImageFolder(data_dir / split, transforms_map[split])
        for split in active_splits
    }
    dataloaders = {
        split: torch.utils.data.DataLoader(
            image_datasets[split],
            batch_size=batch_size,
            shuffle=(split == 'train'),
            num_workers=0,
        )
        for split in active_splits
    }
    return image_datasets, dataloaders


def run_epoch(model, dataloader, criterion, optimizer, device, train_mode):
    model.train(mode=train_mode)
    running_loss = 0.0
    running_corrects = 0
    sample_count = 0

    for inputs, labels in dataloader:
        inputs = inputs.to(device)
        labels = labels.to(device)
        optimizer.zero_grad()

        with torch.set_grad_enabled(train_mode):
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            _, preds = torch.max(outputs, 1)
            if train_mode:
                loss.backward()
                optimizer.step()

        batch_size = inputs.size(0)
        running_loss += loss.item() * batch_size
        running_corrects += torch.sum(preds == labels.data).item()
        sample_count += batch_size

    return (
        running_loss / max(sample_count, 1),
        running_corrects / max(sample_count, 1),
    )


def evaluate_model(model, dataloader, device):
    model.eval()
    running_corrects = 0
    sample_count = 0
    with torch.no_grad():
        for inputs, labels in dataloader:
            inputs = inputs.to(device)
            labels = labels.to(device)
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            running_corrects += torch.sum(preds == labels.data).item()
            sample_count += inputs.size(0)
    return running_corrects / max(sample_count, 1)


def validate_dataset_labels(class_names):
    missing = sorted(set(CLASS_NAMES) - set(class_names))
    extra = sorted(set(class_names) - set(CLASS_NAMES))
    return missing, extra


def train_model(data_dir, save_path, architecture=DEFAULT_ARCHITECTURE, epochs=12, batch_size=24, lr=1e-3):
    if not split_exists(data_dir, 'train') or not split_exists(data_dir, 'val'):
        print(f"Training data not found under {data_dir}.")
        bootstrap_model(save_path, architecture, data_dir)
        return

    image_datasets, dataloaders = create_dataloaders(data_dir, batch_size)
    class_names = image_datasets['train'].classes
    missing, extra = validate_dataset_labels(class_names)
    if missing or extra:
        print(json.dumps({'missing_labels': missing, 'extra_labels': extra}))

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = build_model(architecture=architecture, num_classes=len(class_names), pretrained=True).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=max(epochs, 1))

    history = []
    best_val_acc = -1.0
    best_val_loss = float('inf')
    best_state = None

    print(json.dumps({'device': str(device), 'architecture': architecture, 'epochs': epochs}))

    for epoch in range(epochs):
        train_loss, train_acc = run_epoch(model, dataloaders['train'], criterion, optimizer, device, True)
        val_loss, val_acc = run_epoch(model, dataloaders['val'], criterion, optimizer, device, False)
        scheduler.step()

        metrics = {
            'epoch': epoch + 1,
            'train_loss': round(train_loss, 4),
            'train_acc': round(train_acc, 4),
            'val_loss': round(val_loss, 4),
            'val_acc': round(val_acc, 4),
        }
        history.append(metrics)
        print(json.dumps(metrics))

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_val_loss = val_loss
            best_state = {key: value.detach().cpu() for key, value in model.state_dict().items()}

    if best_state is not None:
        model.load_state_dict(best_state)

    test_acc = None
    if 'test' in dataloaders:
        test_acc = round(evaluate_model(model, dataloaders['test'], device), 4)
        print(json.dumps({'test_acc': test_acc}))

    save_checkpoint(
        model=model.cpu(),
        class_names=class_names,
        save_path=save_path,
        architecture=architecture,
        metrics={
            'best_val_acc': round(best_val_acc, 4),
            'best_val_loss': round(best_val_loss, 4),
            'test_acc': test_acc,
            'epochs': epochs,
            'history': history,
        },
        dataset_root=data_dir,
    )
    print(f"Model saved to {save_path}")


def main():
    parser = argparse.ArgumentParser(description='Train or bootstrap the DermaAura hybrid skin scanner.')
    parser.add_argument('--data-dir', default=str(DATA_DIR), help='Dataset root containing train/ and val/ directories')
    parser.add_argument('--save-path', default=str(MODEL_SAVE_PATH), help='Output checkpoint path')
    parser.add_argument('--architecture', default=DEFAULT_ARCHITECTURE,
                        choices=['efficientnet_v2_s', 'mobilenet_v3_large', 'mobilenet_v2'],
                        help='Backbone architecture for the classifier head')
    parser.add_argument('--epochs', type=int, default=12, help='Number of fine-tuning epochs')
    parser.add_argument('--batch-size', type=int, default=24, help='Batch size')
    parser.add_argument('--lr', type=float, default=1e-3, help='Learning rate')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    parser.add_argument('--bootstrap-only', action='store_true', help='Save a base checkpoint without training')
    args = parser.parse_args()

    seed_everything(args.seed)
    data_dir = Path(args.data_dir)
    save_path = Path(args.save_path)

    if args.bootstrap_only:
        bootstrap_model(save_path, args.architecture, data_dir)
        return

    train_model(
        data_dir=data_dir,
        save_path=save_path,
        architecture=args.architecture,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
    )


if __name__ == '__main__':
    main()
