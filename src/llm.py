# %%
from string import Template
import ollama

# # Local imports
# from market import Market
# from portfolio import Portfolio

# %%
DATASET_FP = "/Users/odai/repos/cs-5588-team-gamestop/datasets/CMIN-US"
STARTING_FUNDS = 10_000  # USD
LLM_MODEL = "llama3.2:3b"

DATE = "2021-01-01"

# %%
class LanguageModel:
    def __init__(self, model_name, template_fp):
        self.model = model_name
        with open(template_fp, "r") as f:
            self.prompt_template = Template(f.read())

    def get_prompt(
        self, date, market_json, funds, portfolio_makeup, market_factors, world_factors
    ):
        return self.prompt_template.substitute(
            date=date,
            market_json=market_json,  # TODO: Add statistical model inputs
            funds=funds,
            portfolio=portfolio_makeup,
            market_factors="",  # TODO: Add market factors
            world_factors="",  # TODO: Add world factors
        )
        
    def execute_prompt(self, prompt):
        response = ollama.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )
        
        return response["message"]["content"]

# %%
# market = Market(DATASET_FP)
# portfolio = Portfolio()
# portfolio.add_funds(STARTING_FUNDS)

# llm = LanguageModel(LLM_MODEL)
# prompt = llm.get_prompt(
#     DATE,
#     market.get_info(date=DATE),
#     portfolio.funds,
#     portfolio.get_makeup(),
#     market_factors=None,
#     world_factors=None,
# )

# resp = llm.execute_prompt(prompt)
# print(resp)


