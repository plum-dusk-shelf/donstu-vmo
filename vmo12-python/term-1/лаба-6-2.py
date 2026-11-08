text = 'стекллянный оловянный коованый '
counter = 0
buff = 0

for i in range(len(text) - 1):
    if text[i] == text[i + 1]:
        buff += 1

    if text[i + 1] == ' ' and buff > 0:
        counter += 1
        buff = 0

print(counter)
