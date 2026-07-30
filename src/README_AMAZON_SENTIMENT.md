# Amazon Reviews Sentiment Analysis

NLP project analyzing 5,000 Amazon product reviews with rule-based and machine learning approaches to classify sentiment as positive or negative.

## Problem

Automatically classify customer reviews by sentiment to enable large-scale feedback analysis for product teams.

## Approach

Two-stage analysis:

**Stage 1 — Rule-based baseline:**
- Custom positive/negative lexicons
- Word frequency analysis
- Baseline accuracy: 54.9%

**Stage 2 — Machine learning classifier:**
- TF-IDF vectorization with bigrams (1, 2)
- 4 models compared: Logistic Regression, Naive Bayes, Linear SVC, Random Forest
- Best accuracy: 83.8% (Logistic Regression)

## Files

- `amazon_sentiment_analysis.py` — Rule-based analysis, word frequency
- `amazon_ml_classifier.py` — ML models, feature importance, ROC curves

## Dataset

5,000 reviews from [Amazon Polarity dataset](https://huggingface.co/datasets/amazon_polarity) (HuggingFace)

## Key Findings

- Negative reviews are 5.9 words longer on average
- Top positive indicators: "great", "excellent", "love", "highly recommend"
- Top negative indicators: "disappointed", "waste", "worst", "waste money"
- ML model improved accuracy by 30 percentage points over lexicon baseline

## How to Run

```bash
python src/amazon_sentiment_analysis.py
python src/amazon_ml_classifier.py
```

## Technologies

Python, Pandas, Scikit-learn, TF-IDF, Matplotlib, Seaborn