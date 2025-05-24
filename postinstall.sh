#!/bin/bash
echo "⏳ Downloading spaCy models..."
python -m spacy download en_core_web_sm
python -m spacy download fr_core_news_sm
echo "✅ spaCy models downloaded"