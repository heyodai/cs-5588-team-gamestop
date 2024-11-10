# CS5588 Capstone - Team GameStop

Please ensure you read on how to contribute to this repo under the `/.github` folder before making any changes or PRs.

## Table of Contents

- [Project Description](#project-description)
- [Datasets](#datasets)
- [Team Members](#team-members)
- [Running the Simulation](#running-the-simulation)

## Project Description

In today's digital age, where information is abundant and easily accessible, financial markets have grown increasingly interconnected and complex. Traditional financial analysis methods often struggle to fully capture this intricate market behavior, highlighting the need for a more advanced, multidimensional approach. 

Leveraging modern technology to extract actionable insights from the vast array of financial data has become essential. Predicting the stock market has important applications for managing investments as well as larger scale sociopolitical implications. Analyzing historical data and incorporating social media and financial news can help provide important information in prediction.

## Datasets

We're using the datasets from the [LLMFactor](https://arxiv.org/abs/2406.10811) paper:

- [StockNet](https://github.com/yumoxu/stocknet-dataset)
- [EDT](https://github.com/Zhihan1996/TradeTheEvent)
- [CMIN](https://github.com/BigRoddy/CMIN-Dataset)

## Team Members
     
1. **Odai Athamneh**
    - Role: ML engineer / UI developer
    - GitHub: [https://github.com/heyodai](https://github.com/heyodai) 
2. **Devin Cline**
    - Role: Product architect/ Data engineer
    - GitHub: [https://github.com/devin-cline](https://github.com/devin-cline) 
3. **Semir Hot**
    - Role: Project manager / Full stack developer
    - GitHub: [https://github.com/SemirHot](https://github.com/SemirHot) 
4. **Namuun Lkhagvadorj**
    - Role: Financial analyst / Data scientist
    - GitHub:[https://github.com/Nami1217](https://github.com/Nami1217)

## Running the Simulation

The steps below detail how to run the simulation. We do have [a ticket](https://github.com/heyodai/cs-5588-team-gamestop/issues/47) to simplify this process in the future.

Steps:

1. Clone the repository
2. Create Python virtual environment:
    ```bash
    python3 -m venv .venv   
    source .venv/bin/activate
    pip install -r requirements.txt
    ```
3. Run a local Ollama server in your terminal: `ollama run llama3.2:3b`
4. Run the FastAPI which serves the dataset: `uvicorn api:app --reload`
5. Run the Streamlit interface: `streamlit run dashboard.py`
6. Open the browser and navigate to `http://localhost:8501/`
