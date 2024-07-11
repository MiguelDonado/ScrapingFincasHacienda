x = [
    (["8878009FE0087N0001HJ", "3982302CD6038SQ"], 94683.45),
    (["8198006ED1789N0001MQ"], 59530.03),
    (["3982302CD6038S0008LQ"], 139645.44),
]
y = [{"referencias_catastrales": refs, "precio": price} for refs, price in x]
print(y)
