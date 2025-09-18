from faker import Faker
fake = Faker()

print(f"Nombre: {fake.name()}")
# 'John Doe'

print(f"Dirección: {fake.address()}")
# '1234 Elm St\nSpringfield, IL 62704'

print(f"Texto: {fake.text()}")
# 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.'