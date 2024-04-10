from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableLambda


def _get_open_ai_chain():
    with open('prompt_template_it_expert.txt', 'r') as file:
        prompt_template_it_expert = file.read()
    openai_chain = (PromptTemplate.from_template(prompt_template_it_expert) 
                    | ChatOpenAI(model="gpt-3.5-turbo-1106")
                    | StrOutputParser())    
    return openai_chain


def _get_it_check_chain():
    with open('prompt_template_it_check.txt', 'r') as file:
        prompt_template_it_check = file.read()
    it_check_chain = (
        PromptTemplate.from_template(prompt_template_it_check)
        | ChatOpenAI(model="gpt-3.5-turbo-1106")
        | StrOutputParser()
    )
    return it_check_chain

def get_full_chain():
    openai_chain = _get_open_ai_chain()
    it_check_chain = _get_it_check_chain()
    def route(info):
        if "YES" in info["topic"].upper():
            return openai_chain
        return "This is not really what I was trained for, therefore I cannot answer. Try again."
    full_chain = {"topic": it_check_chain, "question": lambda x: x["question"]} | RunnableLambda(
        route
    )
    return full_chain