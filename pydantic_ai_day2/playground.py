import pprint
import uuid


class BankAccount:
    def __init__(self, name : str, balance :float =0):
        self.name=name
        self.balance=balance
        self.history : list[dict[str,float]]=[]
        self.uuid=uuid


    def deposit(self, amount=0) -> str:
        self.balance = self.balance+amount
        self.history.append({"direction":"credit", "amount":amount})
        return(f"Amount deposited is : rs {amount} and the current balance is : rs {self.balance}")
    
    def withdrawal(self, amount)-> str:
        if amount>self.balance:
            return(f"Balance insufficient, withdrawal requested is : rs {amount} and balance available is : rs {self.balance}")
        self.balance=self.balance-amount
        self.history.append({"direction" : "debit", "amount":amount})
        return (f"Withdrawal amount is : rs {amount} and the balance available is : rs {self.balance}")
    

def main():
    sunj_data={"name":"Sunj", "balance": 500}
    sunjacc = BankAccount(**sunj_data)
    dmessage = sunjacc.deposit(500)
    pprint.pprint(dmessage)
    wmessage = sunjacc.withdrawal(100)
    pprint.pprint(wmessage)

    wmessage = sunjacc.withdrawal(1000)
    pprint.pprint(wmessage)
    
    pprint.pprint("done")
    
if __name__ == "__main__" :
    main()