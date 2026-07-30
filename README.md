# Data Analyst Portfolio

A collection of data analysis projects following the [roadmap.sh data analyst roadmap](https://roadmap.sh/data-analyst).

## Projects

| # | Project | Skills | Path |
|---|---------|--------|------|
| 1 | [Titanic EDA](src/titanic_eda.py) | Pandas, Matplotlib, Seaborn | `src/titanic_eda.py` |
| 2 | [Iris EDA](src/iris_eda.py) | EDA, visualization, sklearn | `src/iris_eda.py` |
| 3 | [Stock Price Analysis](src/stock_price_analysis.py) | Time series, yfinance | `src/stock_price_analysis.py` |
| 4 | [SQL + Python Analysis](src/sql_python_analysis.py) | SQLite, SQL queries | `src/sql_python_analysis.py` |
| 5 | [Netflix Data Cleaning](src/netflix_cleaning.py) | Data cleaning workflow | `src/netflix_cleaning.py` |
| 6 | [Pharma Sales Analysis](src/pharma_sales_analysis.py) | Business metrics, KPIs | `src/pharma_sales_analysis.py` |
| 7 | [Titanic ML Model](src/titanic_ml_model.py) | Logistic Regression, Random Forest | `src/titanic_ml_model.py` |
| 8 | [Streamlit Dashboard](src/streamlit_dashboard.py) | Interactive viz | `src/streamlit_dashboard.py` |
| 9 | [GitHub Trends Pipeline](src/pipeline.py) | API, SQLite, scheduler | `src/pipeline.py` |
| 10 | [Amazon Sentiment (Rule-based)](src/amazon_sentiment_analysis.py) | NLP, lexicon analysis | `src/amazon_sentiment_analysis.py` |
| 11 | [Amazon Sentiment (ML)](src/amazon_ml_classifier.py) | TF-IDF, classification | `src/amazon_ml_classifier.py` |

## Installation

```bash
pip install pandas numpy matplotlib seaborn scikit-learn yfinance streamlit plotly requests schedule datasets
```

## Usage

```bash
# Run individual analysis
python src/titanic_eda.py

# Launch dashboard
streamlit run src/streamlit_dashboard.py

# Start real-time pipeline
python src/pipeline.py        # one-time fetch
python src/scheduler.py       # continuous refresh
```

## Project Structure

```
data_analyst_practice/
├── data/           # Datasets and SQLite databases
├── outputs/        # Generated visualizations
└── src/            # All analysis scripts
```

## Technologies

- **Languages:** Python, SQL
- **Libraries:** Pandas, NumPy, Scikit-learn, Matplotlib, Seaborn, Plotly, Streamlit
- **Tools:** SQLite, GitHub API, HuggingFace Datasets
- **ML:** Logistic Regression, Random Forest, Naive Bayes, Linear SVC, TF-IDF

## License

MIT