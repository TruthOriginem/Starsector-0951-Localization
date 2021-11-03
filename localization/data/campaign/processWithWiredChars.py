import pandas as pd

with open('rules.csv', mode='rb') as f:
    line = b''.join(f.readlines())

    line = line.replace(b'\x94', b'""')
    line = line.replace(b'\x92', b"'")

    with open('rules2.csv', mode='wb') as f2:
        f2.write(line)


print('Done')
