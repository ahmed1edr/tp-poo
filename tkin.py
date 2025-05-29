import tkinter as tk
from tkinter import messagebox, simpledialog
from abc import ABC, abstractmethod

class Vehicule(ABC):
    def __init__(self, marque, modele, immatriculation):
        self._marque = marque
        self._modele = modele
        self._immatriculation = immatriculation

    @abstractmethod
    def livrer(self, commande):
        pass

    def __str__(self):
        return f"Marque: {self._marque}, Modèle: {self._modele}, Immatriculation: {self._immatriculation}"

class Camion(Vehicule):
    def __init__(self, marque, modele, immatriculation, capacite_tonnes):
        super().__init__(marque, modele, immatriculation)
        self.capacite_tonnes = capacite_tonnes

    def livrer(self, commande):
        if commande.poids <= self.capacite_tonnes * 1000:
            return f"Le camion {self._marque} {self._modele} (capacité {self.capacite_tonnes} tonnes) livre la commande {commande.id}."
        else:
            return f"Le camion {self._marque} {self._modele} (capacité {self.capacite_tonnes} tonnes) ne peut pas livrer la commande {commande.id} en raison du poids excessif."

    def __str__(self):
        return super().__str__() + f", Capacité: {self.capacite_tonnes} tonnes"

class Moto(Vehicule):
    def __init__(self, marque, modele, immatriculation, vitesse_maximale):
        super().__init__(marque, modele, immatriculation)
        self.vitesse_maximale = vitesse_maximale

    def livrer(self, commande):
        if commande.poids < 50:
            return f"La moto {self._marque} {self._modele} (vitesse {self.vitesse_maximale} km/h) livre la commande {commande.id}."
        else:
            return f"La moto {self._marque} {self._modele} (vitesse {self.vitesse_maximale} km/h) ne peut pas livrer la commande {commande.id} en raison du poids."

    def __str__(self):
        return super().__str__() + f", Vitesse Max: {self.vitesse_maximale} km/h"

class Commande:
    def __init__(self, id_commande, destination, poids):
        self.id = id_commande
        self.destination = destination
        self.poids = poids
        self.statut = "en attente"

    def marquer_livree(self):
        self.statut = "livrée"

    @staticmethod
    def valider_poids(poids):
        return 0 < poids <= 100

    def __str__(self):
        return f"Commande ID: {self.id}, Destination: {self.destination}, Poids: {self.poids} kg, Statut: {self.statut}"

class Livreur:
    def __init__(self, nom, vehicule=None):
        self.nom = nom
        self.vehicule = vehicule
        self.commandes_en_cours = []

    def ajouter_commande(self, commande):
        self.commandes_en_cours.append(commande)

    def effectuer_livraison(self):
        if not self.vehicule:
            return f"{self.nom} n'a pas de véhicule pour effectuer la livraison."
        if not self.commandes_en_cours:
            return f"{self.nom} n'a pas de commandes en cours."

        rapport = []
        for commande in self.commandes_en_cours:
            message = self.vehicule.livrer(commande)
            if "ne peut pas livrer" not in message:
                commande.marquer_livree()
            rapport.append(f"{message} - Statut de la commande: {commande.statut}")
        self.commandes_en_cours = []
        return "\n".join(rapport)

    @staticmethod
    def verifier_nom(nom):
        return nom.isalpha()

    @classmethod
    def depuis_dictionnaire(cls, data):
        nom = data.get("nom")
        vehicule_data = data.get("vehicule")
        vehicule = None
        if vehicule_data:
            if vehicule_data["type"] == "Camion":
                vehicule = Camion(vehicule_data["marque"], vehicule_data["modele"], vehicule_data["immatriculation"], vehicule_data["capacite_tonnes"])
            elif vehicule_data["type"] == "Moto":
                vehicule = Moto(vehicule_data["marque"], vehicule_data["modele"], vehicule_data["immatriculation"], vehicule_data["vitesse_maximale"])
        return cls(nom, vehicule)

    def __str__(self):
        vehicule_info = str(self.vehicule) if self.vehicule else "Aucun véhicule"
        return f"Livreur: {self.nom}, Véhicule: [{vehicule_info}], Commandes en cours: {len(self.commandes_en_cours)}"

class Depot:
    def __init__(self):
        self.vehicules_disponibles = []
        self.livreurs_disponibles = []
        self.commandes_en_attente = []

    def ajouter_vehicule(self, vehicule):
        self.vehicules_disponibles.append(vehicule)

    def ajouter_livreur(self, livreur):
        self.livreurs_disponibles.append(livreur)

    def ajouter_commande_depot(self, commande):
        self.commandes_en_attente.append(commande)

    def attribuer_vehicule(self, livreur, vehicule):
        if livreur in self.livreurs_disponibles and vehicule in self.vehicules_disponibles:
            if livreur.vehicule is None:
                livreur.vehicule = vehicule
                self.vehicules_disponibles.remove(vehicule)
                return True
            else:
                return False
        return False

    def afficher_etat(self):
        etat = "--- État du Dépôt ---\n"
        etat += "Véhicules disponibles:\n"
        if not self.vehicules_disponibles:
            etat += "Aucun véhicule disponible.\n"
        for v in self.vehicules_disponibles:
            etat += f"- {v}\n"

        etat += "\nLivreurs disponibles:\n"
        if not self.livreurs_disponibles:
            etat += "Aucun livreur disponible.\n"
        for l in self.livreurs_disponibles:
            etat += f"- {l}\n"
        
        etat += "\nCommandes en attente de distribution:\n"
        if not self.commandes_en_attente:
            etat += "Aucune commande en attente de distribution.\n"
        for c in self.commandes_en_attente:
            etat += f"- {c}\n"

        return etat

class DeliveryApp:
    def __init__(self, master):
        self.master = master
        master.title("Système de Simulation d'Entreprise de Livraison")
        master.geometry("1000x700")
        master.config(bg="#E0F2F7")

        self.depot = Depot()

        self.main_frame = tk.Frame(master, bg="#E0F2F7", bd=5, relief="groove")
        self.main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        self.create_widgets()
        self.update_status_display()

    def create_widgets(self):
        button_font = ("Helvetica", 10, "bold")
        label_font = ("Helvetica", 12)
        title_font = ("Helvetica", 14, "bold")

        button_colors = ["#4CAF50", "#2196F3", "#FFC107", "#9C27B0", "#FF5722", "#009688"]
        button_texts = [
            "Ajouter un véhicule", "Ajouter un livreur", "Créer une commande",
            "Attribuer véhicule au livreur", "Attribuer commande au livreur", "Effectuer une livraison"
        ]
        button_commands = [
            self.open_add_vehicule_window, self.open_add_livreur_window, self.open_create_commande_window,
            self.open_assign_vehicule_window, self.open_assign_commande_window, self.open_perform_delivery_window
        ]

        for i, text in enumerate(button_texts):
            tk.Button(
                self.main_frame,
                text=text,
                command=button_commands[i],
                font=button_font,
                bg=button_colors[i],
                fg="white",
                padx=15, pady=10,
                relief="raised",
                bd=3,
                cursor="hand2"
            ).grid(row=0, column=i, padx=5, pady=10)

        tk.Label(
            self.main_frame,
            text="État du Dépôt:",
            font=title_font,
            bg="#E0F2F7",
            fg="#2C3E50"
        ).grid(row=1, column=0, columnspan=6, pady=15)
        
        self.status_text = tk.Text(
            self.main_frame,
            height=20, width=80,
            state='disabled',
            bg="#FFFFFF",
            fg="#333333",
            font=("Consolas", 10),
            bd=2, relief="sunken"
        )
        self.status_text.grid(row=2, column=0, columnspan=6, padx=10, pady=10)

    def update_status_display(self):
        self.status_text.config(state='normal')
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(tk.END, self.depot.afficher_etat())
        self.status_text.config(state='disabled')

    def open_add_vehicule_window(self):
        add_vehicule_window = tk.Toplevel(self.master)
        add_vehicule_window.title("Ajouter un véhicule")
        add_vehicule_window.config(bg="#F0F8FF")
        add_vehicule_window.transient(self.master)
        add_vehicule_window.grab_set()

        label_font = ("Helvetica", 10)
        entry_font = ("Helvetica", 10)
        button_font = ("Helvetica", 10, "bold")

        tk.Label(add_vehicule_window, text="Type:", bg="#F0F8FF", font=label_font).grid(row=0, column=0, padx=5, pady=5)
        vehicule_type = tk.StringVar(add_vehicule_window)
        vehicule_type.set("Moto")
        tk.OptionMenu(add_vehicule_window, vehicule_type, "Moto", "Camion").grid(row=0, column=1, padx=5, pady=5)

        labels = ["Marque:", "Modèle:", "Immatriculation:"]
        entries = {}
        for i, text in enumerate(labels):
            tk.Label(add_vehicule_window, text=text, bg="#F0F8FF", font=label_font).grid(row=i+1, column=0, padx=5, pady=5)
            entry = tk.Entry(add_vehicule_window, font=entry_font)
            entry.grid(row=i+1, column=1, padx=5, pady=5)
            entries[text] = entry
        
        tk.Label(add_vehicule_window, text="Vitesse Maximale (pour Moto):", bg="#F0F8FF", font=label_font).grid(row=4, column=0, padx=5, pady=5)
        vitesse_entry = tk.Entry(add_vehicule_window, font=entry_font)
        vitesse_entry.grid(row=4, column=1, padx=5, pady=5)
        
        tk.Label(add_vehicule_window, text="Capacité en tonnes (pour Camion):", bg="#F0F8FF", font=label_font).grid(row=5, column=0, padx=5, pady=5)
        capacite_entry = tk.Entry(add_vehicule_window, font=entry_font)
        capacite_entry.grid(row=5, column=1, padx=5, pady=5)

        def add_vehicule():
            marque = entries["Marque:"].get()
            modele = entries["Modèle:"].get()
            immatriculation = entries["Immatriculation:"].get()
            
            if not (marque and modele and immatriculation):
                messagebox.showerror("Erreur", "Veuillez remplir tous les champs obligatoires du véhicule.")
                return

            try:
                if vehicule_type.get() == "Moto":
                    vitesse = float(vitesse_entry.get())
                    new_vehicule = Moto(marque, modele, immatriculation, vitesse)
                elif vehicule_type.get() == "Camion":
                    capacite = float(capacite_entry.get())
                    new_vehicule = Camion(marque, modele, immatriculation, capacite)
                
                self.depot.ajouter_vehicule(new_vehicule)
                messagebox.showinfo("Succès", "Véhicule ajouté avec succès !")
                self.update_status_display()
                add_vehicule_window.destroy()
            except ValueError:
                messagebox.showerror("Erreur", "Veuillez entrer des nombres valides pour la vitesse/capacité.")
            except Exception as e:
                messagebox.showerror("Erreur", f"Une erreur est survenue: {e}")

        tk.Button(add_vehicule_window, text="Ajouter", command=add_vehicule, bg="#4CAF50", fg="white", font=button_font, relief="raised", bd=3, cursor="hand2").grid(row=6, column=0, columnspan=2, pady=10, padx=5)

    def open_add_livreur_window(self):
        add_livreur_window = tk.Toplevel(self.master)
        add_livreur_window.title("Ajouter un livreur")
        add_livreur_window.config(bg="#F0F8FF")
        add_livreur_window.transient(self.master)
        add_livreur_window.grab_set()

        label_font = ("Helvetica", 10)
        entry_font = ("Helvetica", 10)
        button_font = ("Helvetica", 10, "bold")

        tk.Label(add_livreur_window, text="Nom:", bg="#F0F8FF", font=label_font).grid(row=0, column=0, padx=5, pady=5)
        nom_entry = tk.Entry(add_livreur_window, font=entry_font)
        nom_entry.grid(row=0, column=1, padx=5, pady=5)

        def add_livreur():
            nom = nom_entry.get()
            if Livreur.verifier_nom(nom):
                new_livreur = Livreur(nom)
                self.depot.ajouter_livreur(new_livreur)
                messagebox.showinfo("Succès", "Livreur ajouté avec succès !")
                self.update_status_display()
                add_livreur_window.destroy()
            else:
                messagebox.showerror("Erreur", "Veuillez entrer un nom alphabétique valide.")

        tk.Button(add_livreur_window, text="Ajouter", command=add_livreur, bg="#2196F3", fg="white", font=button_font, relief="raised", bd=3, cursor="hand2").grid(row=1, column=0, columnspan=2, pady=10, padx=5)

    def open_create_commande_window(self):
        create_commande_window = tk.Toplevel(self.master)
        create_commande_window.title("Créer une commande")
        create_commande_window.config(bg="#F0F8FF")
        create_commande_window.transient(self.master)
        create_commande_window.grab_set()

        label_font = ("Helvetica", 10)
        entry_font = ("Helvetica", 10)
        button_font = ("Helvetica", 10, "bold")

        tk.Label(create_commande_window, text="ID Commande:", bg="#F0F8FF", font=label_font).grid(row=0, column=0, padx=5, pady=5)
        id_entry = tk.Entry(create_commande_window, font=entry_font)
        id_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(create_commande_window, text="Destination:", bg="#F0F8FF", font=label_font).grid(row=1, column=0, padx=5, pady=5)
        destination_entry = tk.Entry(create_commande_window, font=entry_font)
        destination_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(create_commande_window, text="Poids (kg):", bg="#F0F8FF", font=label_font).grid(row=2, column=0, padx=5, pady=5)
        poids_entry = tk.Entry(create_commande_window, font=entry_font)
        poids_entry.grid(row=2, column=1, padx=5, pady=5)

        def create_commande():
            id_commande = id_entry.get()
            destination = destination_entry.get()
            try:
                poids = float(poids_entry.get())
                if not (id_commande and destination):
                    messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
                    return
                if Commande.valider_poids(poids):
                    new_commande = Commande(id_commande, destination, poids)
                    self.depot.ajouter_commande_depot(new_commande)
                    messagebox.showinfo("Succès", "Commande créée avec succès !")
                    self.update_status_display()
                    create_commande_window.destroy()
                else:
                    messagebox.showerror("Erreur", "Poids invalide. Doit être entre 0 et 100 kg.")
            except ValueError:
                messagebox.showerror("Erreur", "Veuillez entrer une valeur numérique pour le poids.")

        tk.Button(create_commande_window, text="Créer", command=create_commande, bg="#FFC107", fg="white", font=button_font, relief="raised", bd=3, cursor="hand2").grid(row=3, column=0, columnspan=2, pady=10, padx=5)

    def open_assign_vehicule_window(self):
        assign_window = tk.Toplevel(self.master)
        assign_window.title("Attribuer un véhicule")
        assign_window.config(bg="#F0F8FF")
        assign_window.transient(self.master)
        assign_window.grab_set()

        label_font = ("Helvetica", 10)
        listbox_font = ("Helvetica", 9)
        button_font = ("Helvetica", 10, "bold")

        tk.Label(assign_window, text="Sélectionner le livreur:", bg="#F0F8FF", font=label_font).grid(row=0, column=0, padx=5, pady=5)
        livreur_listbox = tk.Listbox(assign_window, height=5, font=listbox_font, bg="#E8F5E9", fg="#1B5E20")
        
        for livreur in self.depot.livreurs_disponibles:
            if livreur.vehicule is None:
                livreur_listbox.insert(tk.END, livreur.nom)
        livreur_listbox.grid(row=1, column=0, padx=5, pady=5)

        tk.Label(assign_window, text="Sélectionner le véhicule:", bg="#F0F8FF", font=label_font).grid(row=0, column=1, padx=5, pady=5)
        vehicule_listbox = tk.Listbox(assign_window, height=5, font=listbox_font, bg="#E3F2FD", fg="#0D47A1")
        
        for vehicule in self.depot.vehicules_disponibles:
            vehicule_listbox.insert(tk.END, str(vehicule))
        vehicule_listbox.grid(row=1, column=1, padx=5, pady=5)

        def assign():
            selected_livreur_index = livreur_listbox.curselection()
            selected_vehicule_index = vehicule_listbox.curselection()

            if not selected_livreur_index or not selected_vehicule_index:
                messagebox.showerror("Erreur", "Veuillez sélectionner un livreur et un véhicule.")
                return

            livreur = self.depot.livreurs_disponibles[selected_livreur_index[0]]
            vehicule = self.depot.vehicules_disponibles[selected_vehicule_index[0]]

            if self.depot.attribuer_vehicule(livreur, vehicule):
                messagebox.showinfo("Succès", f"Véhicule {vehicule._immatriculation} attribué à {livreur.nom} avec succès !")
                self.update_status_display()
                assign_window.destroy()
            else:
                messagebox.showerror("Erreur", "Impossible d'attribuer le véhicule. Le livreur a peut-être déjà un véhicule ou les données sont incorrectes.")

        tk.Button(assign_window, text="Attribuer", command=assign, bg="#9C27B0", fg="white", font=button_font, relief="raised", bd=3, cursor="hand2").grid(row=2, column=0, columnspan=2, pady=10, padx=5)

    def open_assign_commande_window(self):
        assign_commande_window = tk.Toplevel(self.master)
        assign_commande_window.title("Attribuer une commande à un livreur")
        assign_commande_window.config(bg="#F0F8FF")
        assign_commande_window.transient(self.master)
        assign_commande_window.grab_set()

        label_font = ("Helvetica", 10)
        listbox_font = ("Helvetica", 9)
        button_font = ("Helvetica", 10, "bold")

        tk.Label(assign_commande_window, text="Sélectionner le livreur:", bg="#F0F8FF", font=label_font).grid(row=0, column=0, padx=5, pady=5)
        livreur_listbox = tk.Listbox(assign_commande_window, height=5, font=listbox_font, bg="#FFF3E0", fg="#E65100")
        
        self.available_drivers_for_assignment = [l for l in self.depot.livreurs_disponibles if l.vehicule is not None]
        for i, livreur in enumerate(self.available_drivers_for_assignment):
            livreur_listbox.insert(tk.END, livreur.nom)
        livreur_listbox.grid(row=1, column=0, padx=5, pady=5)

        tk.Label(assign_commande_window, text="Sélectionner la commande:", bg="#F0F8FF", font=label_font).grid(row=0, column=1, padx=5, pady=5)
        commande_listbox = tk.Listbox(assign_commande_window, height=5, font=listbox_font, bg="#FCE4EC", fg="#AD1457")
        
        for commande in self.depot.commandes_en_attente:
            commande_listbox.insert(tk.END, str(commande))
        commande_listbox.grid(row=1, column=1, padx=5, pady=5)

        def assign_commande_to_livreur():
            selected_livreur_index = livreur_listbox.curselection()
            selected_commande_index = commande_listbox.curselection()

            if not selected_livreur_index or not selected_commande_index:
                messagebox.showerror("Erreur", "Veuillez sélectionner un livreur et une commande.")
                return

            livreur = self.available_drivers_for_assignment[selected_livreur_index[0]]
            commande = self.depot.commandes_en_attente[selected_commande_index[0]]

            if livreur.vehicule:
                livreur.ajouter_commande(commande)
                self.depot.commandes_en_attente.remove(commande)
                messagebox.showinfo("Succès", f"Commande {commande.id} attribuée à {livreur.nom} avec succès !")
                self.update_status_display()
                assign_commande_window.destroy()
            else:
                messagebox.showerror("Erreur", "Impossible d'attribuer une commande à un livreur sans véhicule.")

        tk.Button(assign_commande_window, text="Attribuer la commande", command=assign_commande_to_livreur, bg="#FF5722", fg="white", font=button_font, relief="raised", bd=3, cursor="hand2").grid(row=2, column=0, columnspan=2, pady=10, padx=5)

    def open_perform_delivery_window(self):
        perform_delivery_window = tk.Toplevel(self.master)
        perform_delivery_window.title("Effectuer une livraison")
        perform_delivery_window.config(bg="#F0F8FF")
        perform_delivery_window.transient(self.master)
        perform_delivery_window.grab_set()

        label_font = ("Helvetica", 10)
        listbox_font = ("Helvetica", 9)
        button_font = ("Helvetica", 10, "bold")

        tk.Label(perform_delivery_window, text="Sélectionner le livreur pour effectuer la livraison:", bg="#F0F8FF", font=label_font).grid(row=0, column=0, padx=5, pady=5)
        livreur_listbox = tk.Listbox(perform_delivery_window, height=5, font=listbox_font, bg="#E0F7FA", fg="#006064")
        
        self.drivers_with_pending_orders = [l for l in self.depot.livreurs_disponibles if l.commandes_en_cours]
        for i, livreur in enumerate(self.drivers_with_pending_orders):
            livreur_listbox.insert(tk.END, livreur.nom)
        livreur_listbox.grid(row=1, column=0, padx=5, pady=5)

        def perform_delivery():
            selected_index = livreur_listbox.curselection()
            if not selected_index:
                messagebox.showerror("Erreur", "Veuillez sélectionner un livreur.")
                return

            livreur = self.drivers_with_pending_orders[selected_index[0]]
            
            if livreur.vehicule is None:
                messagebox.showerror("Erreur", f"{livreur.nom} n'a pas de véhicule pour effectuer la livraison.")
                return

            if not livreur.commandes_en_cours:
                messagebox.showinfo("Information", f"{livreur.nom} n'a pas de commandes actuelles à livrer.")
                return

            delivery_report = livreur.effectuer_livraison()
            messagebox.showinfo("Rapport de Livraison", delivery_report)
            self.update_status_display()
            perform_delivery_window.destroy()

        tk.Button(perform_delivery_window, text="Effectuer la livraison", command=perform_delivery, bg="#009688", fg="white", font=button_font, relief="raised", bd=3, cursor="hand2").grid(row=2, column=0, pady=10, padx=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = DeliveryApp(root)
    root.mainloop()