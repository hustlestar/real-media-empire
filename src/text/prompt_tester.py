prompt = """
Provide json having 6 fields:
        1. 50 actual quotes by %s in array field called quotes, each quote should appear only once,
        2. author of quote 
        3. 2-5 words description of author, if dead - years of living
        4. array with 1-3 funny facts about author
        5. array with 1-3 interesting facts about author
        6. array with 1-3 inspiring facts about author
in the following format:
{
    "quotes": [],
        "author": "",
        "author_description": "",
        "author_funny_facts": [],
        "author_interesting_facts": [],
        "author_inspiring_facts": []
}
Don't include row number in any of the array strings.
All json fields values must be in spanish.
Python should be able to parse and decode this json.
"""
for a in [
    "Mario Vargas Llosa",
    "Isabel Allende",
    "Federico García Lorca",
    "José Martí",
    "Miguel de Cervantes Saavedra",
    "Antonio Machado",
    "Julio Cortázar",
    'Ernesto "Che" Guevara',
    "Salvador Dalí",
    "Benito Juárez",
    "Juan Rulfo",
    "Sor Juana Inés de la Cruz",
    "Gabriel Mistral",
    "José Saramago",
    "Mario Benedetti",
    "Rafael Alberti",
    'Mario Moreno "Cantinflas"',
    "Jorge Ibargüengoitia",
    "Julio Iglesias",
    "Pablo Picasso",
    "José Ortega y Gasset",
    "Camilo José Cela",
    "Manuel Bandeira",
    "Juan Gelman",
    "Rubén Darío",
    "Horacio Quiroga",
    "Isabel de Castilla",
    "José Emilio Pacheco",
    "Rigoberta Menchú",
    "Carlos Fuentes",
    "Alfonso Reyes",
    "Juana Azurduy",
    "Gustavo Adolfo Bécquer",
    "Diego Rivera",
    "Manuel Scorza",
    "Francisco de Quevedo",
    "Juan Carlos Onetti",
    "Manuel Puig",
    "Carmen Laforet",
    "Rosario Castellanos",
    "Federico Andahazi",
    "Pedro Calderón de la Barca",
    "Alfonso X el Sabio",
    "Gonzalo Torrente Ballester",
    "Dulce María Loynaz",
]:
    print("-" * 100)
    print(prompt % a)
