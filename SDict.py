def SDict(nim="160000000"):
    """ generate dictionary customised for each nim.\n
    dictionary generation took only < 0.01s so it is
    better to customise for each nim, instead of
    creating big dictionary at once """
    nim = str(nim)
    start_year = int(nim[:2]) + 81
    end_year = int(nim[:2]) + 84

    dictionary = []
    for yy in range(start_year, end_year):
        for mm in range(1, 13):
            for dd in range(1, 32):
                if mm == 2 and dd > 29:
                    continue
                if mm in [4, 6, 9, 11] and dd > 30:
                    continue
                date = {
                    'dd': str(dd).zfill(2),
                    'mm': str(mm).zfill(2),
                    'yy': str(yy)[-2:]
                }
                dictionary.append("{dd}{mm}{yy}".format(**date))
                dictionary.append("{yy}{mm}{dd}".format(**date))
    for n in range(1000):
        t = str(n)
        dictionary.append(t * int(6 / len(t)))
    for i in range(10):
        dictionary.append(str(i).zfill(2)*3)
        dictionary.append(str(i).zfill(3)*2)

    # put extra values here
    dictionary += [
        "123456",
        "654321",
    ]
    dictionary = sorted(list(set(dictionary)))

    return dictionary


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("nim", help="NIM to seed dictionary")
    args = parser.parse_args()

    data = SDict(args.nim)
    print("\n".join(data))
    print("Dictionary generated {} values".format(len(data)))