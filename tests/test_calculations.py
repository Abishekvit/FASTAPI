#name of function shold also start with test_


## pytest will run by simply typing pytest -v -s
#anytime there is some pritn statement in function ot see that add -s
## for identification file should start with name test_
import pytest
from app.calculations import add, BankAccount,InsufficientFunds

@pytest.fixture
def zero_bank_account():
    return BankAccount()

@pytest.fixture
def bank_account():
    return BankAccount(50)
#pytest fixture allows us to initialize classes in one place and use them again and again

@pytest.mark.parametrize("num1, num2, expected", [
    (3, 2, 5),
    (7, 1, 8),
    (12, 4, 16)
])
def test_add(num1,num2,expected):
    # assert throws error if false
    assert add(num1,num2) == expected

#to test  mnay

def test_bank_set_initial_amount(bank_account):
    assert bank_account.balance == 50

def test_bank_default_amount(zero_bank_account):
    assert zero_bank_account.balance == 0

@pytest.mark.parametrize("wd, bal",[
    (20,30),
    (40,10)
])
def test_withdraw(bank_account,wd,bal):
    bank_account.withdraw(wd)
    assert bank_account.balance == bal

def test_insufficient_funds(bank_account):
    with pytest.raises(InsufficientFunds):
        bank_account.withdraw(200)

def test_collect_interest(bank_account):
    bank_account.collect_interest()
    assert round(bank_account.balance,5) == 55