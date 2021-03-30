def transfer(dom, sender, reciever, amount):
    if not dom.hasAccount(sender):
        return "Sender does not have an Ugly Coin account. Enlist in UGLY to get an account."
    elif not dom.hasAccount(reciever):
        return "Reciever does not have an Ugly Coin account. Enlist in UGLY to get an account."
    elif(dom.balance(sender) < amount):
        return "Sender account balance to low. Sender only has."
    else:
        dom.transfer(sender, reciever, amount)
        return f"Successfully transfered {amount} UGLY coin."

def balance(dom, username):
    if dom.hasAccount(username):
        return dom.balance(username)
    else:
        return f"User{username} does not have an account yet"

def award(dom, reciever, amount):
    if not dom.hasAccount(reciever):
        return f"Reciever {reciever} does not have an Ugly Coin account. Enlist in UGLY to get an account."
    else:
        return dom.deltaBalance(reciever, amount)
    