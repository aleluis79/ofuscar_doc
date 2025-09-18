from mimesis import Person
from mimesis.locales import Locale
from mimesis.enums import Gender
person = Person(Locale.EN)

print(f"Nombre femenino: {person.full_name(gender=Gender.FEMALE)}")
# Output: 'Antonetta Garrison'

print(f"Nombre masculino: {person.full_name(gender=Gender.MALE)}")
# Output: 'Jordon Hall'