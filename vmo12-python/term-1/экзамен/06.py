def createDict(ls: list):
    regions = {}
    for i in ls:
        reg = i[:2]
        numb = i[2:]
        if reg not in regions:
            regions[reg] = []
        regions[reg].append(numb)
    return regions


def MinCountry(dictionary:dict):
    minimum_countries = []
    minimum = 10*10

    for country in dictionary:
        country_numbers_quantity = len(dictionary[country])
        if country_numbers_quantity < minimum:
            minimum = country_numbers_quantity

    for country in dictionary:
        country_numbers_quantity = len(dictionary[country])
        if country_numbers_quantity == minimum:
            minimum_countries.append(country)

    return minimum_countries


example_list = ['8840', '2314', '0959', '8800', '7173', '7114', '7199']
example_dict = createDict(example_list)
print(example_dict)
print(MinCountry(example_dict))
