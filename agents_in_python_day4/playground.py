import pprint

def ai_model(question : str)->str :
    return (f"stub for prediction {question}")

class ChatModel:
    def __init__(self):
        self.__history :list[dict] = []

    def ask(self, question: str)->str:
        self.__history.append({"role":"user","content":question})
        result=ai_model(question)
        self.__history.append({"role":"AI","content":result})
        return result
    
    def get_history(self)->list[dict]:
        history:list[dict]=self.__history
        return history
    
class Agent:
    def __init__(self, tools : dict[str, callable]):
        self.__history : list[dict]= []
        self.tools: dict[str, callable]=tools

    def decide_tools(self, question: str)->str|None:
        for name in self.tools :
            if name in question.lower():
                return name
        return None

    def ask(self, question: str)-> str|None:
        self.__history.append({"role":"user", "content":"question"})
        toolname=self.decide_tools(question)
        if toolname is not None:
            result=self.tools[toolname]()
            self.__history.append({"role":"tool","toolname":toolname,"content":result})
        else :    
            result=ai_model(question)
            self.__history.append({"role":"AI","content":result})

        return result
    
    def get_history(self)->list[dict]|None:
        history : list[dict] = self.__history
        return history


def weather()-> str|None:
        return "22c partly cloudy"


def main() -> None:
    result=ai_model("what is the capital of France?")    
    print(result)
    chat= ChatModel()
    print(chat.ask("what is the capital of Japan"))
    print(chat.ask("What is the capital of India"))
    
    # chat.__history.append({"role":"Eve", "content":"Attack"})
    #history is immutable private object encapsulation
    history=chat.get_history()
    pprint.pprint(history)
  
    tools={"weather":weather}

    agent= Agent(tools)
    agent.ask("What is the capital of france?")
    agent.ask("Weather in France?")
    pprint.pprint(agent.get_history())

    print("done")


if __name__=="__main__":
    main()
    
