class EmployeeSystem:
    def __init__(self):
        # Fördefinierade arbetstitlar. Varje titel har en dictionary med arbetsmoment och dess vikt i %.
        self.roles = {
            "Junior konsult": {},
            "Handläggare": {},
            "Senior konsult": {},
            "Specialist": {},
            "Senior specialist": {}
        }
        # Databas för anställda
        self.employees = {}

    def run(self):
        while True:
            print("\n" + "="*40)
            print(" SYSTEM FÖR LÖNEREVISION OCH UTVÄRDERING")
            print("="*40)
            print("1. Lägg till ny anställd")
            print("2. Redigera befintlig anställd")
            print("3. Hantera arbetstitlar och arbetsmoment (%)")
            print("4. Utvärdera anställd (sätt poäng)")
            print("5. Visa utvärderingsrapport (Lönerevisionsunderlag)")
            print("6. Avsluta")
            
            choice = input("Välj ett alternativ (1-6): ")
            
            if choice == '1':
                self.add_employee()
            elif choice == '2':
                self.edit_employee()
            elif choice == '3':
                self.manage_roles()
            elif choice == '4':
                self.evaluate_employee()
            elif choice == '5':
                self.show_reports()
            elif choice == '6':
                print("Avslutar programmet...")
                break
            else:
                print("Ogiltigt val, försök igen.")

    def add_employee(self):
        print("\n--- LÄGG TILL ANSTÄLLD ---")
        name = input("Namn: ")
        address = input("Adress: ")
        try:
            edu_years = float(input("Utbildning (antal år): "))
            exp_years = float(input("Erfarenhet (antal år): "))
        except ValueError:
            print("Fel: Utbildning och erfarenhet måste vara siffror. Avbryter...")
            return

        print("\nTillgängliga arbetstitlar:")
        titles = list(self.roles.keys())
        for i, title in enumerate(titles, 1):
            print(f"{i}. {title}")
        
        try:
            title_choice = int(input("Välj titel (siffra): "))
            title = titles[title_choice - 1]
        except (ValueError, IndexError):
            print("Ogiltigt val. Sätter titel till 'Okänd'. Du kan ändra detta senare.")
            title = "Okänd"

        self.employees[name] = {
            "Namn": name,
            "Adress": address,
            "Utbildning (år)": edu_years,
            "Erfarenhet (år)": exp_years,
            "Titel": title,
            "Poäng": {} # Sparar poäng per arbetsmoment
        }
        print(f"Anställd {name} har lagts till!")

    def edit_employee(self):
        print("\n--- REDIGERA ANSTÄLLD ---")
        if not self.employees:
            print("Inga anställda inlagda ännu.")
            return
            
        name = input("Ange namnet på den anställda du vill redigera: ")
        if name not in self.employees:
            print("Hittade ingen anställd med det namnet.")
            return

        emp = self.employees[name]
        print(f"Nuvarande information för {name}:")
        for key, value in emp.items():
            if key != "Poäng":
                print(f"{key}: {value}")
        
        print("\nVad vill du ändra?")
        print("1. Adress")
        print("2. Utbildning (år)")
        print("3. Erfarenhet (år)")
        print("4. Titel")
        
        choice = input("Välj (1-4): ")
        if choice == '1':
            emp["Adress"] = input("Ny adress: ")
        elif choice == '2':
            emp["Utbildning (år)"] = float(input("Ny utbildning (år): "))
        elif choice == '3':
            emp["Erfarenhet (år)"] = float(input("Ny erfarenhet (år): "))
        elif choice == '4':
            titles = list(self.roles.keys())
            for i, t in enumerate(titles, 1):
                print(f"{i}. {t}")
            t_choice = int(input("Välj ny titel (siffra): "))
            emp["Titel"] = titles[t_choice - 1]
            emp["Poäng"] = {} # Nollställ poäng eftersom titeln (och momenten) ändras
            
        print("Ändringarna har sparats!")

    def manage_roles(self):
        print("\n--- HANTERA ARBETSTITLAR & MOMENT ---")
        titles = list(self.roles.keys())
        for i, title in enumerate(titles, 1):
            print(f"{i}. {title}")
            
        try:
            choice = int(input("Vilken titel vill du redigera arbetsmoment för? (siffra): "))
            selected_title = titles[choice - 1]
        except (ValueError, IndexError):
            print("Ogiltigt val.")
            return

        print(f"\nArbetstitel: {selected_title}")
        print("Nuvarande moment och viktning:")
        if not self.roles[selected_title]:
            print("- Inga moment inlagda.")
        else:
            for task, weight in self.roles[selected_title].items():
                print(f"- {task}: {weight}%")

        print("\n1. Lägg till/Uppdatera ett moment")
        print("2. Rensa alla moment för denna titel")
        action = input("Välj åtgärd (1-2): ")

        if action == '1':
            task_name = input("Namn på arbetsmomentet: ")
            try:
                weight = float(input("Vikt i procent (t.ex. 25 för 25%): "))
                self.roles[selected_title][task_name] = weight
                
                # Kontrollera total procent
                total = sum(self.roles[selected_title].values())
                print(f"Moment tillagt! Total viktning för {selected_title} är nu {total}%.")
                if total != 100:
                    print("OBS: För en korrekt utvärdering bör den totala summan av alla moment bli exakt 100%.")
            except ValueError:
                print("Ogiltig siffra.")
        elif action == '2':
            self.roles[selected_title] = {}
            print("Alla moment rensade för denna titel.")

    def evaluate_employee(self):
        print("\n--- UTVÄRDERA ANSTÄLLD ---")
        if not self.employees:
            print("Inga anställda inlagda.")
            return
            
        name = input("Ange namnet på den anställda du vill utvärdera: ")
        if name not in self.employees:
            print("Hittade ingen anställd med det namnet.")
            return

        emp = self.employees[name]
        title = emp["Titel"]
        tasks = self.roles.get(title, {})

        if not tasks:
            print(f"Det finns inga arbetsmoment definierade för titeln '{title}'.")
            print("Gå till huvudmenyn val 3 för att lägga till moment först.")
            return

        print(f"Utvärderar {name} ({title}). Ange poäng (t.ex. 1-10) för varje moment.")
        for task in tasks.keys():
            try:
                score = float(input(f"Poäng för '{task}': "))
                emp["Poäng"][task] = score
            except ValueError:
                print("Ogiltig poäng, hoppar över detta moment.")
                
        print(f"Utvärdering för {name} är sparad!")

    def show_reports(self):
        print("\n" + "="*40)
        print(" LÖNEREVISIONSUTVÄRDERING (SAMMANSTÄLLNING)")
        print("="*40)
        
        if not self.employees:
            print("Ingen data tillgänglig.")
            return

        for name, emp in self.employees.items():
            print(f"\nAnställd: {name}")
            print(f"Titel: {emp['Titel']}")
            print(f"Erfarenhet: {emp['Erfarenhet (år)']} år | Utbildning: {emp['Utbildning (år)']} år")
            
            tasks = self.roles.get(emp["Titel"], {})
            if not tasks:
                print("Resultat: Saknar definierade arbetsmoment.")
                continue
                
            if not emp["Poäng"]:
                print("Resultat: Har inte utvärderats ännu.")
                continue

            total_weighted_score = 0
            total_weight_possible = sum(tasks.values())
            
            print("Detaljer:")
            for task, weight in tasks.items():
                score = emp["Poäng"].get(task, 0)
                # Räkna ut viktad poäng: (poäng * vikt i procent)
                weighted = score * (weight / 100)
                total_weighted_score += weighted
                print(f"  - {task} ({weight}% vikt): Fick {score} poäng -> Bidrar med {weighted:.2f} till totalen")

            print(f"> Total Viktad Utvärderingspoäng: {total_weighted_score:.2f}")
            if total_weight_possible != 100:
                print(f"> (Varning: Momenten för denna roll summerar till {total_weight_possible}%, inte 100%)")

# Starta programmet
if __name__ == "__main__":
    app = EmployeeSystem()
    app.run()