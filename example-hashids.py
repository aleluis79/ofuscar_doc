from hashids import Hashids
hashids = Hashids()

hashid = hashids.encode(123) # 'Mj3'
print(hashid)
number = hashids.decode(hashid) # (123,)