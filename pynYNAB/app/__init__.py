from pynYNAB.Client import nYnabClient, BudgetNotFound
from pynYNAB.connection import nYnabConnection


def clientfromargs(args, reset=False):
    connection = nYnabConnection(args.email, args.password)
    try:
        client = nYnabClient(connection, budget_name=args.budgetname)
        if reset:
            # deletes the budget
            client.delete_budget(args.budgetname)
            client.create_budget(args.budgetname)
            client.select_budget(args.budgetname)
        return client
    except BudgetNotFound:
        print('No budget by this name found in nYNAB')
        exit(-1)