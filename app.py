import json
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk


# The recipes are the app's small starter database. You can add more later.
RECIPES = [
    {
        "name": "Masala Omelette",
        "category": "Breakfast",
        "time": 12,
        "ingredients": ["egg", "onion", "tomato", "salt"],
        "steps": "1. Chop the onion and tomato.\n2. Beat the eggs with salt.\n3. Mix in the vegetables and cook in a lightly oiled pan until set.",
    },
    {
        "name": "Tomato Rice",
        "category": "Lunch",
        "time": 25,
        "ingredients": ["rice", "tomato", "onion", "salt"],
        "steps": "1. Cook the rice.\n2. Sauté chopped onion and tomato until soft.\n3. Stir in the rice and salt, then warm through.",
    },
    {
        "name": "Banana Pancakes",
        "category": "Breakfast",
        "time": 15,
        "ingredients": ["banana", "egg", "flour"],
        "steps": "1. Mash the banana.\n2. Mix with egg and flour.\n3. Cook small pancakes in a lightly oiled pan, turning once.",
    },
    {
        "name": "Aloo Sandwich",
        "category": "Snack",
        "time": 20,
        "ingredients": ["bread", "potato", "onion", "salt"],
        "steps": "1. Boil and mash the potato.\n2. Mix with chopped onion and salt.\n3. Spread between bread slices and toast until golden.",
    },
    {
        "name": "Simple Dal",
        "category": "Dinner",
        "time": 35,
        "ingredients": ["lentils", "onion", "tomato", "salt"],
        "steps": "1. Rinse and boil the lentils until soft.\n2. Cook chopped onion and tomato in a pan.\n3. Stir into the lentils, add salt, and simmer for a few minutes.",
    },
    {
        "name": "Garlic Noodles",
        "category": "Dinner",
        "time": 20,
        "ingredients": ["noodles", "garlic", "onion", "salt"],
        "steps": "1. Cook the noodles according to their packet.\n2. Sauté chopped garlic and onion.\n3. Add noodles and salt, then toss together.",
    },
    {
        "name": "Yogurt Banana Bowl",
        "category": "Snack",
        "time": 5,
        "ingredients": ["yogurt", "banana", "honey"],
        "steps": "1. Put the yogurt in a bowl.\n2. Slice the banana over it.\n3. Drizzle with honey.",
    },
    {
        "name": "Potato Egg Hash",
        "category": "Breakfast",
        "time": 25,
        "ingredients": ["potato", "egg", "onion", "salt"],
        "steps": "1. Dice and cook the potato in a pan until tender.\n2. Add chopped onion and cook until soft.\n3. Add an egg and salt, then cook until the egg is set.",
    },
]

BACKGROUND = "#fff0f6"
CARD = "#fffafd"
GREEN = "#e85d9e"
TEXT = "#54263f"
MUTED = "#9b6b83"


class WhatCanICookApp:
    def __init__(self, root):
        self.root = root
        self.root.title("What Can I Cook?")
        self.root.geometry("980x700")
        self.root.minsize(760, 560)
        self.root.configure(bg=BACKGROUND)
        self.pantry_file = Path(__file__).with_name("pantry.json")
        self.pantry = self.load_pantry()
        self.search_text = tk.StringVar()
        self.category = tk.StringVar(value="All meals")

        self.configure_styles()
        self.build_screen()
        self.refresh_pantry()
        self.show_recipes()

    def configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=BACKGROUND)
        style.configure("Card.TFrame", background=CARD)
        style.configure("TLabel", background=BACKGROUND, foreground=TEXT, font=("Arial", 11))
        style.configure("Title.TLabel", font=("Arial", 25, "bold"), foreground=GREEN)
        style.configure("Subtitle.TLabel", font=("Arial", 11), foreground=MUTED)
        style.configure("CardTitle.TLabel", background=CARD, font=("Arial", 14, "bold"), foreground=TEXT)
        style.configure("CardText.TLabel", background=CARD, foreground=MUTED, font=("Arial", 10))
        style.configure("Green.TButton", background=GREEN, foreground="white", padding=(12, 8), font=("Arial", 10, "bold"))
        style.map("Green.TButton", background=[("active", "#cc4284")])
        style.configure("TButton", padding=(10, 7), font=("Arial", 10))

    def build_screen(self):
        header = ttk.Frame(self.root, padding=(28, 22, 28, 12))
        header.pack(fill="x")
        ttk.Label(header, text="What Can I Cook?", style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, text="Find something tasty with the ingredients you already have.", style="Subtitle.TLabel").pack(anchor="w", pady=(4, 0))

        main = ttk.Frame(self.root, padding=(28, 10, 28, 24))
        main.pack(fill="both", expand=True)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        pantry_panel = ttk.Frame(main, style="Card.TFrame", padding=18)
        pantry_panel.grid(row=0, column=0, sticky="nsw", padx=(0, 18))
        pantry_panel.configure(width=260)
        pantry_panel.grid_propagate(False)
        ttk.Label(pantry_panel, text="My pantry", style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(pantry_panel, text="Add ingredients one at a time.", style="CardText.TLabel").pack(anchor="w", pady=(4, 12))

        add_row = ttk.Frame(pantry_panel, style="Card.TFrame")
        add_row.pack(fill="x")
        self.ingredient_entry = ttk.Entry(add_row)
        self.ingredient_entry.pack(side="left", fill="x", expand=True)
        self.ingredient_entry.bind("<Return>", lambda _event: self.add_ingredient())
        ttk.Button(add_row, text="Add", style="Green.TButton", command=self.add_ingredient).pack(side="left", padx=(7, 0))

        self.pantry_list = tk.Listbox(pantry_panel, height=14, font=("Arial", 11), borderwidth=0,
                                      highlightthickness=0, bg="#fff5fa", fg=TEXT,
                                      selectbackground="#f7c5dc", activestyle="none")
        self.pantry_list.pack(fill="both", expand=True, pady=(14, 8))
        ttk.Button(pantry_panel, text="Remove selected", command=self.remove_ingredient).pack(anchor="w")
        ttk.Label(pantry_panel, text="Your pantry saves automatically.", style="CardText.TLabel").pack(anchor="w", pady=(12, 0))

        results_panel = ttk.Frame(main)
        results_panel.grid(row=0, column=1, sticky="nsew")
        results_panel.columnconfigure(0, weight=1)
        results_panel.rowconfigure(2, weight=1)
        ttk.Label(results_panel, text="Recipe ideas", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")

        controls = ttk.Frame(results_panel)
        controls.grid(row=1, column=0, sticky="ew", pady=(12, 12))
        controls.columnconfigure(0, weight=1)
        search = ttk.Entry(controls, textvariable=self.search_text)
        search.grid(row=0, column=0, sticky="ew", padx=(0, 8), ipady=5)
        search.insert(0, "")
        search.bind("<KeyRelease>", lambda _event: self.show_recipes())
        category_menu = ttk.Combobox(controls, textvariable=self.category,
                                     values=["All meals", "Breakfast", "Lunch", "Dinner", "Snack"],
                                     state="readonly", width=13)
        category_menu.grid(row=0, column=1, sticky="e")
        category_menu.bind("<<ComboboxSelected>>", lambda _event: self.show_recipes())

        self.recipe_canvas = tk.Canvas(results_panel, bg=BACKGROUND, highlightthickness=0)
        scrollbar = ttk.Scrollbar(results_panel, orient="vertical", command=self.recipe_canvas.yview)
        self.recipe_canvas.configure(yscrollcommand=scrollbar.set)
        self.recipe_canvas.grid(row=2, column=0, sticky="nsew")
        scrollbar.grid(row=2, column=1, sticky="ns")
        self.recipe_list_frame = ttk.Frame(self.recipe_canvas)
        self.canvas_window = self.recipe_canvas.create_window((0, 0), window=self.recipe_list_frame, anchor="nw")
        self.recipe_list_frame.bind("<Configure>", lambda _event: self.recipe_canvas.configure(scrollregion=self.recipe_canvas.bbox("all")))
        self.recipe_canvas.bind("<Configure>", lambda event: self.recipe_canvas.itemconfigure(self.canvas_window, width=event.width))

    def load_pantry(self):
        try:
            data = json.loads(self.pantry_file.read_text(encoding="utf-8"))
            return sorted({item.strip().lower() for item in data if item.strip()})
        except (FileNotFoundError, json.JSONDecodeError, TypeError):
            return []

    def save_pantry(self):
        self.pantry_file.write_text(json.dumps(self.pantry, indent=2), encoding="utf-8")

    def refresh_pantry(self):
        self.pantry_list.delete(0, tk.END)
        for ingredient in self.pantry:
            self.pantry_list.insert(tk.END, ingredient.title())

    def add_ingredient(self):
        ingredient = self.ingredient_entry.get().strip().lower()
        if not ingredient:
            return
        if ingredient not in self.pantry:
            self.pantry.append(ingredient)
            self.pantry.sort()
            self.save_pantry()
            self.refresh_pantry()
            self.show_recipes()
        self.ingredient_entry.delete(0, tk.END)

    def remove_ingredient(self):
        selected = self.pantry_list.curselection()
        if not selected:
            messagebox.showinfo("Select an ingredient", "Choose an ingredient in your pantry first.")
            return
        del self.pantry[selected[0]]
        self.save_pantry()
        self.refresh_pantry()
        self.show_recipes()

    def show_recipes(self):
        for widget in self.recipe_list_frame.winfo_children():
            widget.destroy()

        query = self.search_text.get().strip().lower()
        chosen_category = self.category.get()
        matches = []
        for recipe in RECIPES:
            if chosen_category != "All meals" and recipe["category"] != chosen_category:
                continue
            if query and query not in recipe["name"].lower() and query not in recipe["category"].lower():
                continue
            missing = [item for item in recipe["ingredients"] if item not in self.pantry]
            matches.append((recipe, missing))

        if not self.pantry:
            ttk.Label(self.recipe_list_frame, text="Add a few ingredients to your pantry to see how well each recipe matches.",
                      style="Subtitle.TLabel", wraplength=550).pack(anchor="w", pady=12)
        elif not matches:
            ttk.Label(self.recipe_list_frame, text="No recipes match those filters. Try another search.",
                      style="Subtitle.TLabel").pack(anchor="w", pady=12)

        matches.sort(key=lambda pair: (len(pair[1]), pair[0]["time"], pair[0]["name"]))
        for recipe, missing in matches:
            self.make_recipe_card(recipe, missing)

    def make_recipe_card(self, recipe, missing):
        card = ttk.Frame(self.recipe_list_frame, style="Card.TFrame", padding=16)
        card.pack(fill="x", pady=(0, 12))
        ttk.Label(card, text=recipe["name"], style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(card, text=f"{recipe['category']}  •  {recipe['time']} min", style="CardText.TLabel").pack(anchor="w", pady=(4, 8))

        if not self.pantry:
            status = "Add pantry ingredients to see your match."
            color = MUTED
        elif not missing:
            status = "You have everything for this recipe!"
            color = GREEN
        else:
            status = "Still need: " + ", ".join(missing)
            color = "#c0477d"
        tk.Label(card, text=status, bg=CARD, fg=color, font=("Arial", 10), wraplength=500, justify="left").pack(anchor="w")
        ttk.Button(card, text="View recipe", command=lambda: self.show_details(recipe, missing)).pack(anchor="e", pady=(8, 0))

    def show_details(self, recipe, missing):
        window = tk.Toplevel(self.root)
        window.title(recipe["name"])
        window.geometry("440x430")
        window.configure(bg=BACKGROUND)
        body = ttk.Frame(window, padding=24)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text=recipe["name"], style="Title.TLabel", wraplength=390).pack(anchor="w")
        ttk.Label(body, text=f"{recipe['category']}  •  {recipe['time']} minutes", style="Subtitle.TLabel").pack(anchor="w", pady=(4, 18))
        ttk.Label(body, text="Ingredients", style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(body, text=", ".join(recipe["ingredients"]).title(), wraplength=390, justify="left").pack(anchor="w", pady=(6, 14))
        if self.pantry and missing:
            ttk.Label(body, text="You still need: " + ", ".join(missing), foreground="#c0477d", wraplength=390).pack(anchor="w", pady=(0, 12))
        ttk.Label(body, text="Steps", style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(body, text=recipe["steps"], wraplength=390, justify="left").pack(anchor="w", pady=(6, 0))


if __name__ == "__main__":
    window = tk.Tk()
    app = WhatCanICookApp(window)
    window.mainloop()
