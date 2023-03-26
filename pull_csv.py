import sys
import subprocess as su

if len(sys.argv) != 3:
    print(
            'Помилка, невірна кількість параметрів\n'
            'Потрібно ввести 2 параметри, в форматі: \n'
            '\tdd_mm_yy -flag\n\n'
            '-flag - або "-p", для минулих матчів  або "-f", для майбутніх'
            )
    exit()

if '-p' == sys.argv[2]:
    su.run([
        'scp',
        f'q@192.168.0.106:/home/q/papka/lang/python/parser/csv/past/{sys.argv[1]}_p.csv',
        f'/home/q/papka/languages/python/parser/csv/past/',
        ])
elif '-f' == sys.argv[2]:
    su.run([
        'scp',
        f'q@192.168.0.106:/home/q/papka/lang/python/parser/csv/future/{sys.argv[1]}_f.csv',
        f'/home/q/papka/languages/python/parser/csv/future/',
        ])
else:
    su.run(['echo', 'some shit'])
