from os import listdir
import torch
from torch.utils.data import Dataset
from PIL import Image
from transformers import (
    ViTImageProcessor,
    AutoTokenizer,
    PreTrainedTokenizer,
    VisionEncoderDecoderModel,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
    default_data_collator
)
from evaluate import load
import ujson


class ImageDataset(Dataset):
    def __init__(
            self,
            images_path: str,
            image_text_pairs: dict[str, str],
            processor: ViTImageProcessor,
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
        image = Image.open(f"{self.images_path}/{file_name}")
        # NOTE: CONVERT TO BLACK AND WHITE TO SAVE ON INPUTS
        pixel_values = self.processor(image, return_tensors="pt").pixel_values
        # add labels (input_ids) by encoding the text
        encoding = self.tokenizer(
            text,
            padding="max_length",
            max_length=self.max_target_length
        )
        labels = encoding.input_ids
        attention_mask = encoding.attention_mask
        # important: make sure that PAD tokens are ignored by the loss function
        labels = [label if label != self.tokenizer.pad_token_id else -100 for label in labels]

        return {
            "pixel_values": pixel_values.squeeze(),
            "labels": torch.tensor(labels),
            "attention_mask": attention_mask
        } # the encoding


def train():
    with open("manga_datasets/ocr/clean_10k/sentences.json", "r", encoding="utf-8") as f:
        image_text_pairs = ujson.load(f)

    processor = ViTImageProcessor.from_pretrained("google/vit-base-patch16-224-in21k")
    tokenizer = AutoTokenizer.from_pretrained("tohoku-nlp/bert-base-japanese-v3")

    train_dataset = ImageDataset(
        "manga_datasets/ocr/clean_10k/train",
        image_text_pairs,
        processor,
        tokenizer
    )
    validation_dataset = ImageDataset(
        "manga_datasets/ocr/clean_10k/valid",
        image_text_pairs,
        processor,
        tokenizer
    )

    model = VisionEncoderDecoderModel.from_encoder_decoder_pretrained(
        "google/vit-base-patch16-224-in21k",
        "tohoku-nlp/bert-base-japanese-v3"
    )

    # set special tokens used for creating the decoder_input_ids from the labels
    model.config.decoder_start_token_id = tokenizer.cls_token_id
    model.config.pad_token_id = tokenizer.pad_token_id
    # make sure vocab size is set correctly
    model.config.vocab_size = model.config.decoder.vocab_size

    # set beam search parameters
    model.config.eos_token_id = tokenizer.sep_token_id
    model.config.max_length = 256
    model.config.early_stopping = True
    model.config.no_repeat_ngram_size = 3
    model.config.length_penalty = 1.5
    model.config.num_beams = 4

    training_args = Seq2SeqTrainingArguments(
        num_train_epochs=20,
        predict_with_generate=True,
        eval_strategy="steps",
        per_device_train_batch_size=32,
        per_device_eval_batch_size=32,
        fp16=True, 
        output_dir="models/test_ocr_v2/",
        logging_steps=25,
        save_steps=500,
        eval_steps=200
    )

    cer_metric = load("cer")
    def compute_metrics(pred):
        labels_ids = pred.label_ids
        pred_ids = pred.predictions

        pred_str = tokenizer.batch_decode(pred_ids, skip_special_tokens=True)
        labels_ids[labels_ids == -100] = tokenizer.pad_token_id
        label_str = tokenizer.batch_decode(labels_ids, skip_special_tokens=True)

        cer = cer_metric.compute(predictions=pred_str, references=label_str)

        return {"cer": cer}

    trainer = Seq2SeqTrainer(
        model=model,
        tokenizer=tokenizer,
        args=training_args,
        compute_metrics=compute_metrics,
        train_dataset=train_dataset,
        eval_dataset=validation_dataset,
        data_collator=default_data_collator
    )
    trainer.train("models/test_ocr_v2/checkpoint-4000")


def test():
    model = VisionEncoderDecoderModel.from_pretrained("models/test_ocr_v2/checkpoint-4000")
    processor = ViTImageProcessor.from_pretrained("google/vit-base-patch16-224-in21k")
    tokenizer = AutoTokenizer.from_pretrained("tohoku-nlp/bert-base-japanese-v3")

    pixel_values = processor(Image.open("manga_datasets/ocr/clean_10k/test/f34b29ec44f54050923c48d0de3c5940.jpg"), return_tensors="pt").pixel_values

    generated_ids = model.generate(pixel_values)
    generated_text = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    print(generated_text)


if __name__ == "__main__":
    test()
