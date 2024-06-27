from os import listdir
import torch
from torch.utils.data import Dataset
from PIL import Image
from transformers import ViTFeatureExtractor, AutoTokenizer, PreTrainedTokenizer
import ujson


class ImageDataset(Dataset):
    def __init__(
            self,
            images_path: str,
            image_text_pairs: dict[str, str],
            processor: ViTFeatureExtractor,
            tokenizer: PreTrainedTokenizer,
            max_target_length: int = 256
        ):
        self.images_path = images_path
        self.image_text_pairs = [(image, image_text_pairs[image]) for image in listdir(images_path)]
        self.processor = processor
        self.tokenizer = tokenizer
        self.max_target_length = max_target_length

    def __len__(self):
        return len(self.image_text_pairs)

    def __getitem__(self, idx: int):
        file_name, text = self.image_text_pairs[idx]
        # prepare image (i.e. resize + normalize)
        image = Image.open(f"{self.image_path}/{file_name}")
        pixel_values = self.processor(image, return_tensors="pt").pixel_values
        # add labels (input_ids) by encoding the text
        labels = self.tokenizer(
            text,
            padding="max_length",
            max_length=self.max_target_length
        ).input_ids
        # important: make sure that PAD tokens are ignored by the loss function
        labels = [label if label != self.processor.tokenizer.pad_token_id else -100 for label in labels]

        return {
            "pixel_values": pixel_values.squeeze(),
            "labels": torch.tensor(labels)
        } # the encoding


if __name__ == "__main__":
    with open("datasets/ocr/clean_10k/sentences.json", "r", encoding="utf-8") as f:
        image_text_pairs = ujson.load(f)

    processor = ViTFeatureExtractor.from_pretrained("google/vit-base-patch16-224-in21k")
    tokenizer = AutoTokenizer.from_pretrained("tohoku-nlp/bert-base-japanese-v3")

    train_dataset = ImageDataset(
        "datasets/ocr/clean_10k/train",
        image_text_pairs,
        processor,
        tokenizer
    )
    validation_dataset = ImageDataset(
        "datasets/ocr/clean_10k/valid",
        image_text_pairs,
        processor,
        tokenizer
    )

    print("Number of training examples:", len(train_dataset))
    print("Number of validation examples:", len(validation_dataset))
