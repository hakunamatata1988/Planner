def per(lst: list, b : int) -> list:
    idx = 0

    while b>0 and idx < len(lst):
        # print('idx = ', idx)
        pos = pos_maks(lst,idx)
        # print('pos = ', pos)

        if pos != idx:
            # swap
            lst[idx], lst[pos] = lst[pos], lst[idx]
            b -= 1
            idx += 1
        else:
            # no swop, maks on idx position
            idx += 1

        # print(lst)
    return lst

def pos_maks(lst:list, start:int)->int:
    '''
    Returns the index with maksimum value (no repeted values in lst). len(lst) >= 1
    '''

    idx = start
    maks = lst[start]

    for k in range(start,len(lst)):
        if lst[k] > maks:
            idx = k
            maks = lst[k]

    return idx

# assert per([1,2,3,4], 0) == [1,2,3,4]
# assert per([1,2,3,4], 1) == [4,2,3,1]
# assert per([1,2,3,4], 2) == [4,3,2,1], f'resoult {per([1,2,3,4], 2)}'
# assert per([1,2,3,4], 3) == [4,3,2,1], f'resoult {per([1,2,3,4], 3)}'
# assert per([4,2,3,1,5], 2) == [5,4,3,1,2]

# print("Tested!")

def gas(A: list,B: list)-> int:


    for start in range(len(A)):
        gas = A[start]
        curent = start

        while gas - B[curent] > 0 :
            gas = gas - B[curent]
            curent += 1
            if curent == len(A):
                curent = 0
            gas += A[curent]

            if curent == start:
                return start
        
        

    return -1

A = [1,1,4,1]
B = [2,2,1,1]

print( gas(A,B) )






