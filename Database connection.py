import psycopg2

conn = psycopg2.connect(database="ZasadaciPoriadok",
                        user="postgres",
                        host='localhost',
                        port=5432)

cur = conn.cursor()

# TODO Urobit subory vsetkych ziakov na skole

triedaInput: str = input("Trieda: ").capitalize()

subor = open("{}.tssl".format(triedaInput), 'r')

Nriadok = 0
zahranicie = False
meno = ''
trieda = ''
for riadok in subor:
    if Nriadok == 0:
        trieda = riadok.strip()[3:]
    else:
        if not " -info" in riadok:
            meno = riadok.strip()
        elif 'Z' in riadok:
            zahranicie = True
        else:
            cur.execute("""INSERT INTO public."ZoznamZiakov"(
                        "Meno a Priezvisko", "Skupina", "Zahranicie", "Trieda")
                        VALUES('{}','{}',{},'{}');""".format(meno, riadok.strip()[:-6], zahranicie, trieda))
            if zahranicie:
                zahranicie = False
    Nriadok += 1
conn.commit()

cur.close()
conn.close()
