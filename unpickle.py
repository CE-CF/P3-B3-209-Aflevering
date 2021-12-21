import pickle

filename = '/dev/shm/picklejar'

with open(filename, 'rb') as file_object:
	raw_data = file_object.read()

deserialize = pickle.loads(raw_data)

print(deserialize)
