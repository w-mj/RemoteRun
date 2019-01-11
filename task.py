if __name__ == '__main__':
    print("input two numbers")
    while True:
        try :
            a = input()
            b = a.split()
            try:
                b[0] = int(b[0])
                b[1] = int(b[1])
            except ValueError as v:
                print(v)
            except IndexError:
                b.append(0)
                b.append(0)
            print(b[0] + b[1])
        except EOFError:
            print("exit")
            exit(0)
        except Exception as e:
            print("exit2")
            print(e)
