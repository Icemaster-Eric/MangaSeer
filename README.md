# MangaSeer
Learn Japanese by reading manga! (Demo video coming soon)

## How it works
MangaSeer applies an overlay transparent to mouse and keyboard events to any selected region of your screen. It then uses an object detection model to locate both vertical and horizontal Japanese text, with or without furigana. By hovering over the Japanese text, it will display an unobtrusive popup next to the text with options such as text-to-speech, furigana, translation, and more.

## Why should I use MangaSeer?
MangaSeer aims to make raw manga a viable source for any Japanese learner. If you're ever unsure of the pronunciation or the meaning of a word, you can immediately get the answer by hovering over the text. This makes it easy to immerse yourself in manga without having to look up meanings of words or pronunciations.

## Installation
(you will need an nvidia gpu)

Git clone this repo, cd into the mangaseer folder, and install the required packages in requirements.txt. Run the app.py file, select the area for ocr, and press ctrl alt s to scan the area for Japanese text.
