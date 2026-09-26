import tkinter as tk
from tkinter import ttk
import os
from calculator import CalcFunc
from meal import MealFunc
from ai_assistant import AIAssistant
from storage import (
    load_menus,
    load_selections as read_selections,
    save_menus,
    save_selections as write_selections,
)
from dotenv import load_dotenv

UI_FONT = 'Segoe UI Variable Text'

# This loads the variables from your .env file into the system
load_dotenv()

# Now you can pull the key safely into your code
api_key = os.getenv("API_KEY")
menus = load_menus()

"""CONSTANTS"""
MAX_CALORIES = 2300  # preset for maximum calories
charts = None  # allows calorie calculator button to run
calorie_animation_id = None
displayed_calories = 0.0
ALL_MENUS = [menus["breakfast_menu"], menus["morning_tea_menu"],
            menus["lunch_menu"], menus["dessert_menu"],
            menus["dinner_menu"],]

custom_meals = []  # empty list to add custom meals
menu_dict = {"Breakfast": "breakfast_menu", 
            "Morning Tea": "morning_tea_menu",
            "Lunch": "lunch_menu", "Dessert": "dessert_menu",
            "Dinner": "dinner_menu"}
menu_names = ["Breakfast", "Morning Tea", "Lunch",
            "Dessert","Dinner"]


class RoundedCard(tk.Canvas):
    """Canvas-backed card with a ttk content frame and rounded corners."""

    def __init__(self, master, style_name, padding, fill, min_height=0, radius=14):
        super().__init__(master, background='#252735', borderwidth=0,
                         highlightthickness=0, width=180, height=min_height)
        self._fill = fill
        self._radius = radius
        self._inset = 6
        self._min_width = 180
        self._min_height = min_height
        self._height_job = None
        self._shape_items = [
            self.create_rectangle(0, 0, 0, 0, fill=fill, outline=''),
            self.create_rectangle(0, 0, 0, 0, fill=fill, outline=''),
            self.create_oval(0, 0, 0, 0, fill=fill, outline=''),
            self.create_oval(0, 0, 0, 0, fill=fill, outline=''),
            self.create_oval(0, 0, 0, 0, fill=fill, outline=''),
            self.create_oval(0, 0, 0, 0, fill=fill, outline=''),
        ]
        self.content = ttk.Frame(self, style=style_name, padding=padding)
        self._content_window = self.create_window(
            self._inset, self._inset, anchor='nw', window=self.content
        )
        self.bind('<Configure>', self._resize_card)
        self.content.bind('<Configure>', self._schedule_height_update)

    def _resize_card(self, event):
        width = max(event.width, 1)
        height = max(event.height, 1)
        radius = min(self._radius, width / 2, height / 2)
        left, top = 0, 0
        right, bottom = width, height
        self.coords(self._shape_items[0], left + radius, top, right - radius, bottom)
        self.coords(self._shape_items[1], left, top + radius, right, bottom - radius)
        self.coords(self._shape_items[2], left, top, left + 2 * radius, top + 2 * radius)
        self.coords(self._shape_items[3], right - 2 * radius, top, right, top + 2 * radius)
        self.coords(self._shape_items[4], left, bottom - 2 * radius, left + 2 * radius, bottom)
        self.coords(self._shape_items[5], right - 2 * radius, bottom - 2 * radius, right, bottom)
        self.coords(self._content_window, self._inset, self._inset)
        self.itemconfigure(self._content_window, width=max(1, width - 2 * self._inset))

    def _schedule_height_update(self, _event=None):
        if self._height_job is None:
            self._height_job = self.after_idle(self._update_height)

    def _update_height(self):
        self._height_job = None
        if not self.winfo_exists():
            return
        width = max(self._min_width, self.content.winfo_reqwidth() + 2 * self._inset)
        height = max(self._min_height, self.content.winfo_reqheight() + 2 * self._inset)
        if (int(float(self.cget('width'))) != width
                or int(float(self.cget('height'))) != height):
            self.configure(width=width, height=height)

    def set_fill(self, fill):
        self._fill = fill
        for item in self._shape_items:
            self.itemconfigure(item, fill=fill)

def save_selections():
    """Persist data on program close."""
    selections = [var.get() for var in selected_meals]  # for each selection
    write_selections(selections)

def on_closing():
    """Detect program close, run data persistence."""
    save_selections()  # Runs JSON code
    root.destroy()  # Exit program 

def load_selections():
    """Load saved data from previous use of program."""
    selections = read_selections()
    for var, value in zip(selected_meals, selections):
        var.set(value)  # Set each dropdown box with value from before

def meat_type_func(menu):
    """Run logic of filters in each meal."""
    try:
        meat_type = set()  # Make set for each meat types present in meal selec
        for meal in menu.values():  # For each meal in spec menu
            meat_type.add(meal['meat'])  # Extract meat type of meal, add to set
        return ['None'] + sorted(meat_type - {'None'})  # Make default of dropdown "NONE"
    except Exception as e:
        print("meat_type_func error:", e)
        return ['None']


def apply_theme(root):
    """Apply the CalorAI charcoal and pastel-accent palette."""
    style = ttk.Style(root)
    style.theme_use('clam')

    bg = '#514d78'
    panel = '#252735'
    surface = '#303343'
    sidebar = '#2b2e3d'
    text = '#f3f2f8'
    muted = '#b0b2c1'
    ink = '#292a36'
    lime = '#a8e760'
    cyan = '#70d2e8'
    orange = '#ff9d67'
    lavender = '#bd9cf2'
    yellow = '#f5dd68'

    root.configure(bg=bg)

    style.configure('TFrame', background=panel)
    style.configure('TLabel', background=panel, foreground=text, font=(UI_FONT, 11))
    style.configure('Outer.TFrame', background=bg)
    style.configure('Header.TLabel', background=panel, foreground=text,
                    font=(UI_FONT, 28, 'bold'))
    style.configure('Brand.TLabel', background=sidebar, foreground=text,
                    font=(UI_FONT, 20, 'bold'))
    style.configure('Subtle.TLabel', background=panel, foreground=muted,
                    font=(UI_FONT, 10, 'bold'))
    style.configure('CardTitle.TLabel', background=surface, foreground=text,
                    font=(UI_FONT, 10, 'bold'))
    style.configure('MetricValue.TLabel', background=surface, foreground=text,
                    font=(UI_FONT, 26, 'bold'))
    style.configure('MetricSubtitle.TLabel', background=surface, foreground=muted,
                    font=(UI_FONT, 9))
    style.configure('Panel.TFrame', background=surface)
    style.configure('Sidebar.TFrame', background=sidebar)
    style.configure('TButton', font=(UI_FONT, 10), padding=(12, 8),
                    background=surface, foreground=text)
    style.map('TButton', background=[('active', '#414458')],
              foreground=[('active', text)])
    style.configure('Action.TButton', font=(UI_FONT, 10, 'bold'),
                    padding=(12, 8), background=lime, foreground=ink)
    style.configure('Secondary.TButton', font=(UI_FONT, 10, 'bold'),
                    padding=(12, 8), background=surface, foreground=text)
    style.configure('Pill.TButton', font=(UI_FONT, 9, 'bold'),
                    padding=(10, 6), background='#45465f', foreground=yellow)
    style.map('Action.TButton', background=[('active', '#b9f178')],
              foreground=[('active', ink)])
    style.map('Secondary.TButton', background=[('active', '#414458')],
              foreground=[('active', text)])
    style.map('Pill.TButton', background=[('active', '#555574')],
              foreground=[('active', yellow)])
    style.configure('TEntry', font=(UI_FONT, 11), fieldbackground=surface,
                    foreground=text, insertcolor=text)
    style.configure('TCombobox', font=(UI_FONT, 10), padding=6,
                    fieldbackground=surface, foreground=text, arrowcolor=text)
    style.map('TCombobox', fieldbackground=[('readonly', surface)],
              foreground=[('readonly', text)])

    style.configure('Breakfast.TCombobox', fieldbackground='#fff0a6', background=yellow,
                    foreground=ink, font=(UI_FONT, 10, 'bold'), padding=10)
    style.configure('MorningTea.TCombobox', fieldbackground='#d9f5fb', background=cyan,
                    foreground=ink, font=(UI_FONT, 10), padding=10)
    style.configure('Lunch.TCombobox', fieldbackground='#e4f8c9', background=lime,
                    foreground=ink, font=(UI_FONT, 10), padding=10)
    style.configure('Dessert.TCombobox', fieldbackground='#eee2ff', background=lavender,
                    foreground=ink, font=(UI_FONT, 10, 'bold'), padding=10)
    style.configure('Dinner.TCombobox', fieldbackground='#ffe1cc', background=orange,
                    foreground=ink, font=(UI_FONT, 10), padding=10)
    style.configure('MenuChoice.TCombobox', fieldbackground='#eee2ff', background=lavender,
                    foreground=ink, font=(UI_FONT, 10, 'bold'), padding=10)

    metric_accents = {
        'Calories': (yellow, '#fff0a6'),
        'Protein': (cyan, '#d9f5fb'),
        'Fats': (orange, '#ffe1cc'),
        'Carbs': (lavender, '#eee2ff'),
    }
    for name, accent_colors in metric_accents.items():
        accent, trough = accent_colors
        style.configure(f'{name}Card.TFrame', background=accent)
        for label_style, font in [
            ('Title', (UI_FONT, 10, 'bold')),
            ('Value', (UI_FONT, 26, 'bold')),
            ('Subtitle', (UI_FONT, 9)),
        ]:
            foreground = '#4a4b58' if label_style == 'Subtitle' else ink
            style.configure(f'{name}{label_style}.TLabel', background=accent,
                            foreground=foreground, font=font)
        style.configure(f'{name}.Horizontal.TProgressbar', background=ink,
                        troughcolor=trough, bordercolor=accent,
                        lightcolor=ink, darkcolor=ink)

    style.configure('Horizontal.TProgressbar', background=lavender,
                    troughcolor=surface, bordercolor=surface)
    style.configure('TScrollbar', background=surface, troughcolor=panel,
                    arrowcolor=text)
    style.configure('DashboardCard.TFrame', background=surface)
    style.configure('MealPanel.TFrame', background=surface)
    style.configure('SidebarButton.TButton', background=sidebar, foreground=text,
                    font=(UI_FONT, 10), padding=(16, 10))
    style.map('SidebarButton.TButton', background=[('active', '#414458')],
              foreground=[('active', lime)])

    root.option_add('*TCombobox*Listbox*Font', (UI_FONT, 10))
    root.option_add('*TCombobox*Listbox*Background', surface)
    root.option_add('*TCombobox*Listbox*Foreground', text)

def on_selection_change(*args):
    """Change saved data when user changes it even while program runs."""
    save_selections()
    try:
        refresh_dashboard()
    except NameError:
        pass

# Functions
def calculation_and_graph():
    """Run nutritional calculation and chars/graphs."""
    root.state('zoomed')  # Fullscreen the prgram
    for widget in right_frame.winfo_children():  # For each existing graph
        widget.destroy()  # Destroy exisitng graph
    global charts  # Access global charts
    # Run CalcFunc for graphing in calculator.py
    calculator = CalcFunc(charts, ALL_MENUS, selected_meals,
                          results, right_frame, root, MAX_CALORIES)
    charts = calculator.calculation_and_graph()  # Change charts value
    save_selections()  # Run data persistence

def hide_charts():
    """Destroy any existing chart."""
    global charts  # Access global charts variable
    if charts is not None:  # If theres an exisitng chart
        try:
            charts.get_tk_widget().destroy()  # Destroy exisitng chart
        except Exception:
            pass
        charts = None  # Indicate that theres no existing chart

def create_custom_meal():
    """Allow user to create a meal."""
    hide_charts()  # Destroy open charts if any
    # Create own frame for create custom meal section
    create_custom_meal.inputs_frame = ttk.Frame(right_frame)
    create_custom_meal.inputs_frame.pack(expand=True, fill='both', padx=80, pady=80)
    # Main heading of create custom meal section
    ttk.Label(create_custom_meal.inputs_frame, text="Add Custom Meal", style='Header.TLabel').grid(row=0, column=0, columnspan=2, pady=(0,12))
    # Labels for each input box later
    labels = ["Meal Name", "Calories", "Protein", "Fats", "Carbs"]
    global custom_meals  # Access global custom_meals vaiable
    custom_meals = [] 
    for i, new_meal in enumerate(labels):  # For each custom meal made (combine all key and value)
        # Announce new meal created
        ttk.Label(create_custom_meal.inputs_frame, text=f"{new_meal}:").grid(row=i+1, column=0, sticky='e', padx=5, pady=6)
        entry = ttk.Entry(create_custom_meal.inputs_frame)  # Style
        entry.grid(row=i+1, column=1, padx=5, pady=6)
        custom_meals.append(entry)  # Add new meal into custom meals list

    global menu_names  # Access menus
    global menu_choice_var  # Access menu choice
    menu_choice_var = tk.StringVar()
    menu_choice_var.set(menu_names[0])  # Make whatever menu they piked the default choice of menu dropdown

    # Alow user to select which menu to add custom meal to
    ttk.Label(create_custom_meal.inputs_frame, text="Add to menu:").grid(row=len(labels)+1, column=0, sticky='e', padx=5, pady=6)
    menu_dropdown = ttk.Combobox(create_custom_meal.inputs_frame, textvariable=menu_choice_var, values=menu_names, state="readonly")
    menu_dropdown.grid(row=len(labels)+1, column=1, padx=5, pady=6)
    # Create button for meal submission
    submit = ttk.Button(create_custom_meal.inputs_frame, text="Submit", command=process_inputs)
    submit.grid(row=len(labels)+2, column=0, columnspan=2, pady=(10,2))
    # Create button to close meal creation section
    close = ttk.Button(create_custom_meal.inputs_frame, text="Close", command=lambda: toggle_create_custom_meal(shown=True))
    close.grid(row=len(labels)+3, column=0, columnspan=2, pady=(2,10))

def process_inputs():
    """Process all inputs coming from meal creation section."""
    name = custom_meals[0].get().strip()  # Get first value of added meal (name)
    calories = custom_meals[1].get().strip()  # Get second value of added meal (cals)
    protein = custom_meals[2].get().strip()  # Get third value of added meal (prot)
    fats = custom_meals[3].get().strip()  # Get forth value of added meal (fat)
    carbs = custom_meals[4].get().strip()  # Get last value of added meal (carb)
    if not name:  # If no name is inputted (left blank)
        results.config(text="Please enter a name for the meal.")
        return
    try:  # If incorrect data type (not number)
        meal_info = {"calories": int(calories), "fats": int(fats),
                     "carbs": int(carbs), "protein": int(protein),
                     "meat": "None"}
    except ValueError:
        results.config(text="ONLY NUMBERS for nutritional values.")
        return

    global menu_dict  # Access global menu dictionary
    selected_menu_display = menu_choice_var.get()  # Get the data of users menu choice
    chosen_menu = menu_dict[selected_menu_display]  # Store data of chosen menu
    new_meal = f"{name.upper()} (CUSTOM)\n\n Calories: {meal_info['calories']} | Protein: {meal_info['protein']}g | Fats: {meal_info['fats']}g"
    menus[chosen_menu][new_meal] = meal_info  # Access new meal's nut information
    save_menus(menus)
    results.config(text=f"Customised meal '{name}' added to {selected_menu_display} menu.")

    global menu_map  # Access global meu map
    if chosen_menu in menu_map:  # If the chosen menu is in the map
        menu_map[chosen_menu].update_menu_options(menus[chosen_menu])  # Update menu dropdown

    for entry in custom_meals:  # For every input box
        entry.delete(0, tk.END)  # Reset all values

def toggle_create_custom_meal(shown=False):
    """Toggle meal creation section using button."""
    close_all_toggle_sections()  # Close all other sections
    if not shown:  # If user clicks button
        create_custom_meal()  # Run meal creation section

def delete_custom_meal():
    """Allow user to delete a custom meal."""
    hide_charts()  # Hide any open grahps
    # Create own frame for meal deletion section
    delete_custom_meal.frame = ttk.Frame(right_frame)
    delete_custom_meal.frame.pack(expand=True, fill='both', padx=80, pady=80)
    # Main heading for meal deletion section
    ttk.Label(delete_custom_meal.frame, text="Delete Custom Meal", style='Header.TLabel').grid(row=0, column=0, columnspan=2, pady=(0,12))
    global menu_names  # Access global menu names variable
    global menu_dict  # Access global menu dictionary
    delete_menu_var = tk.StringVar()  # Get user's menu choice
    delete_menu_var.set(menu_names[0])  # Set menu dropdown box to first option (Nothing)
    # Instructs user to select a menu
    ttk.Label(delete_custom_meal.frame, text="Select Menu:").grid(row=1, column=0, padx=5, pady=6, sticky='e')
    # Dropdown box for menus
    menu_dropdown = ttk.Combobox(delete_custom_meal.frame, textvariable=delete_menu_var, values=menu_names, state="readonly")
    menu_dropdown.grid(row=1, column=1, padx=5, pady=6)
    delete_meal_var = tk.StringVar()  # Get user's meal choice

    def update_dropdown(*args):
        """Update the menu dropdown box."""
        chosen_menu = menu_dict[delete_menu_var.get()]  # User's chosen menu from dropdown box
        # For each meal in selected menu, look for "(CUSTOM)" keyword
        custom_meal_names = [key for key in menus[chosen_menu] if "(CUSTOM)" in key]  
        meal_dropdown['values'] = custom_meal_names or [""]  # If there's a custom meal, show If not, show blank
        if custom_meal_names:  # If there is a custom meal in menu
            delete_meal_var.set(custom_meal_names[0])  # Make it the first option in dropdown
        else:
            delete_meal_var.set("")  # Show a blank option indicating no custom meals.

    # Instruct user to select a custom meal if multiple
    ttk.Label(delete_custom_meal.frame, text="Select Custom Meal:").grid(row=2, column=0, padx=5, pady=6, sticky='e')
    # For all custom meals in selected menu
    all_meal_creations = [key for key in menus[menu_dict[menu_names[0]]] if "(CUSTOM)" in key]
    # Show all custom meals in a dropdown box
    meal_dropdown = ttk.Combobox(delete_custom_meal.frame, textvariable=delete_meal_var, values=all_meal_creations or [""], state="readonly")
    meal_dropdown.grid(row=2, column=1, padx=5, pady=6)
    # When usr changes menu, update dropdwon box on custom meals present in new chosen menu.
    menu_dropdown.bind("<<ComboboxSelected>>", lambda e: update_dropdown())

    def delete():
        """Delete custom meal from menu."""
        chosen_menu = menu_dict[delete_menu_var.get()]  # Get user's chosen menu
        meal_key = delete_meal_var.get()
        if not meal_key or meal_key not in menus[chosen_menu]:  # If user clicks delete with no selection
            results.config(text="No custom meal selected to delete.")
            return
        del menus[chosen_menu][meal_key]  # Delete custom meal from menu
        save_menus(menus)
        results.config(text=f"Deleted custom meal '{meal_key}' from {delete_menu_var.get()}.")
        global menu_map  # Access global menu map
        if chosen_menu in menu_map:  # If menu is appropriate
            menu_map[chosen_menu].update_menu_options(menus[chosen_menu])  # Update menu dropdown
        update_dropdown()  # Update dropdown box for custom meals for deletion

    # Button to delete selected meal
    ttk.Button(delete_custom_meal.frame, text="Delete Selected Meal", command=delete).grid(row=3, column=0, columnspan=2, pady=10)
    # Button to close meal deletion section
    ttk.Button(delete_custom_meal.frame, text="Close", command=lambda: toggle_delete_meal(shown=True)).grid(row=4, column=0, columnspan=2, pady=2)

def toggle_delete_meal(shown=False):
    """Toggle meal deletion using button."""
    close_all_toggle_sections()  # Close other sections
    if not shown:  # If user clicks button
        delete_custom_meal()  # Run meal deletion section

def show_calorie_input():
    """Calculate max calories of user using physical attributes."""

    hide_charts()  # Close any open graphs
    # Create new frame for section
    show_calorie_input.frame = ttk.Frame(right_frame)
    show_calorie_input.frame.pack(expand=True, fill='both', padx=80, pady=80)
    # Main heading for section
    ttk.Label(show_calorie_input.frame, text="Set Max Calories", style='Header.TLabel').grid(row=0, column=0, columnspan=2, pady=(0,12))

    # Ask for user's sex
    ttk.Label(show_calorie_input.frame, text="Sex:").grid(row=1, column=0, padx=5, pady=6, sticky='e')
    sex_var = tk.StringVar(value="Male")  # Set dropdown value default to male
    # Dropdown box only male or female
    sex_dropdown = ttk.Combobox(show_calorie_input.frame, textvariable=sex_var, values=["Male", "Female"], state="readonly")
    sex_dropdown.grid(row=1, column=1, padx=5, pady=6)
    # Ask for user's height
    ttk.Label(show_calorie_input.frame, text="Height (CENTIMETRES):").grid(row=2, column=0, padx=5, pady=6, sticky='e')
    height_entry = ttk.Entry(show_calorie_input.frame)  # Input box for height
    height_entry.grid(row=2, column=1, padx=5, pady=6)
    # Ask for user's weight
    ttk.Label(show_calorie_input.frame, text="Weight (KILOGRAMS):").grid(row=3, column=0, padx=5, pady=6, sticky='e')
    weight_entry = ttk.Entry(show_calorie_input.frame)  # Input box for weight
    weight_entry.grid(row=3, column=1, padx=5, pady=6)

    def set_max_calories():
        try:
            sex = sex_var.get()  # Get user's sex
            height = int(height_entry.get())  # Get user's height
            weight = int(weight_entry.get())  # Get user's weight
            if sex == "Male":  # Calculations for male
                bmr = 10*weight + 6.25*height + 5
            else:  # Calculations for female
                bmr = 10*weight + 6.25*height - 161
            set_max_calories = int(bmr * 1.2)
            global MAX_CALORIES
            MAX_CALORIES = set_max_calories  # New max calories value
            results.config(text=f"Max Calories set to {MAX_CALORIES} kcal.")
            show_calorie_input.frame.destroy()  # Remove the max calorie calculating section
        except Exception as e:  # If user inputs wrong data type
            results.config(text="Please enter whole numbers.")
    # Button to set max calories
    ttk.Button(show_calorie_input.frame, text="Set Max Calories", command=set_max_calories).grid(row=4, column=0, columnspan=2, pady=10)
    # Button to close section
    ttk.Button(show_calorie_input.frame, text="Close", command=show_calorie_input.frame.destroy).grid(row=5, column=0, columnspan=2, pady=2)

def toggle_max_cal(shown=False):
    """Toggle calorie calculator using button."""
    close_all_toggle_sections()  # Close all other open sections
    if not shown:  # If button pressed and section not open
        show_calorie_input()  # Run calorie calculator

def get_ai_nutrition_context():
    """Build current calorie totals and the available meal choices."""
    totals = {"calories": 0, "protein": 0, "fats": 0, "carbs": 0}
    selected = []
    for menu_name, menu, selection in zip(menu_names, ALL_MENUS, selected_meals):
        meal_name = selection.get()
        if meal_name == "NO SELECTION/SKIP" or meal_name not in menu:
            continue
        details = menu[meal_name]
        selected.append({"menu": menu_name, "meal": meal_name.splitlines()[0]})
        for nutrient in totals:
            totals[nutrient] += details[nutrient]

    available_meals = []
    for menu_name, menu in zip(menu_names, ALL_MENUS):
        for meal_name, details in menu.items():
            if meal_name == "NO SELECTION/SKIP":
                continue
            available_meals.append({
                "menu": menu_name,
                "meal": meal_name.splitlines()[0],
                "calories": details["calories"],
                "protein_g": details["protein"],
                "fats_g": details["fats"],
                "carbs_g": details["carbs"],
            })

    return {
        "daily_calorie_limit": MAX_CALORIES,
        "calories_consumed_by_selected_meals": totals["calories"],
        "calories_remaining": MAX_CALORIES - totals["calories"],
        "selected_meals": selected,
        "available_meals": available_meals,
    }

def toggle_ai_assistant():
    """Open or close the meal-planning assistant."""
    close_all_toggle_sections()
    hide_charts()
    assistant.show()

def close_all_toggle_sections():
    """Close all other open sections."""
    if hasattr(create_custom_meal, "inputs_frame") and create_custom_meal.inputs_frame.winfo_exists():
        create_custom_meal.inputs_frame.destroy()
        del create_custom_meal.inputs_frame
    if hasattr(delete_custom_meal, "frame") and delete_custom_meal.frame.winfo_exists():
        delete_custom_meal.frame.destroy()
        del delete_custom_meal.frame
    if hasattr(show_calorie_input, "frame") and show_calorie_input.frame.winfo_exists():
        show_calorie_input.frame.destroy()
        del show_calorie_input.frame
    assistant.close()


def build_dashboard_summary():
    """Create the dashboard cards and summary values used on the home screen."""
    totals = {"calories": 0, "protein": 0, "fats": 0, "carbs": 0}
    for menu, selection_var in zip(ALL_MENUS, selected_meals):
        meal_name = selection_var.get()
        if meal_name == "NO SELECTION/SKIP" or meal_name not in menu:
            continue
        meal_info = menu[meal_name]
        for key in totals:
            totals[key] += meal_info[key]

    calories_left = MAX_CALORIES - totals["calories"]
    total_macro = totals["protein"] + totals["fats"] + totals["carbs"]
    protein_pct = (totals["protein"] / total_macro * 100) if total_macro else 0
    carbs_pct = (totals["carbs"] / total_macro * 100) if total_macro else 0
    fat_pct = (totals["fats"] / total_macro * 100) if total_macro else 0

    return {
        "calories": totals["calories"],
        "calories_left": calories_left,
        "protein": totals["protein"],
        "fats": totals["fats"],
        "carbs": totals["carbs"],
        "protein_pct": protein_pct,
        "carbs_pct": carbs_pct,
        "fat_pct": fat_pct,
        "calories_pct": max(0, min(100, (totals["calories"] / MAX_CALORIES) * 100)) if MAX_CALORIES else 0,
    }


def blend_hex_color(start_color, end_color, amount):
    """Interpolate between two RGB colors."""
    amount = max(0.0, min(1.0, amount))
    start_rgb = tuple(int(start_color[index:index + 2], 16) for index in (1, 3, 5))
    end_rgb = tuple(int(end_color[index:index + 2], 16) for index in (1, 3, 5))
    mixed_rgb = tuple(round(start + (end - start) * amount)
                      for start, end in zip(start_rgb, end_rgb))
    return '#{:02x}{:02x}{:02x}'.format(*mixed_rgb)


def update_calorie_warning(calories):
    """Tint the calorie tile from yellow to red as intake reaches its limit."""
    ratio = calories / MAX_CALORIES if MAX_CALORIES > 0 else 0
    yellow, orange, red = '#f5dd68', '#ff9d67', '#ef707d'
    light_yellow, light_orange, light_red = '#fff0a6', '#ffd4b5', '#f5b4bd'

    if ratio <= 0.6:
        card_color, track_color = yellow, light_yellow
    elif ratio <= 0.85:
        amount = (ratio - 0.6) / 0.25
        card_color = blend_hex_color(yellow, orange, amount)
        track_color = blend_hex_color(light_yellow, light_orange, amount)
    else:
        amount = min(1.0, (ratio - 0.85) / 0.15)
        card_color = blend_hex_color(orange, red, amount)
        track_color = blend_hex_color(light_orange, light_red, amount)

    style = ttk.Style(root)
    style.configure('CaloriesCard.TFrame', background=card_color)
    for label_style in ['Title', 'Value', 'Subtitle']:
        foreground = '#4a4b58' if label_style == 'Subtitle' else '#292a36'
        style.configure(f'Calories{label_style}.TLabel',
                        background=card_color, foreground=foreground)
    style.configure('Calories.Horizontal.TProgressbar', background=card_color,
                    troughcolor=track_color, bordercolor=card_color,
                    lightcolor=card_color, darkcolor=card_color)
    if 'metric_card_widgets' in globals():
        metric_card_widgets['calories'].set_fill(card_color)


def animate_calorie_total(target_calories):
    """Ease the calorie total and progress bar to their latest values."""
    global calorie_animation_id, displayed_calories

    if calorie_animation_id is not None:
        root.after_cancel(calorie_animation_id)
        calorie_animation_id = None

    start_calories = displayed_calories
    animation_steps = 20

    def update(step=0):
        global calorie_animation_id, displayed_calories
        progress = step / animation_steps
        eased_progress = 1 - (1 - progress) ** 3
        displayed_calories = start_calories + (target_calories - start_calories) * eased_progress
        dashboard_labels['calories'].configure(text=f"{round(displayed_calories):,} kcal")
        update_calorie_warning(displayed_calories)
        calorie_percent = (displayed_calories / MAX_CALORIES * 100) if MAX_CALORIES else 0
        dashboard_bars['calories'].configure(value=max(0, min(100, calorie_percent)))

        if step < animation_steps:
            calorie_animation_id = root.after(16, lambda: update(step + 1))
        else:
            displayed_calories = float(target_calories)
            dashboard_labels['calories'].configure(text=f"{target_calories:,} kcal")
            calorie_animation_id = None

    update()


def refresh_dashboard():
    """Update the dashboard summary cards with live values."""
    if 'dashboard_labels' not in globals():
        return
    summary = build_dashboard_summary()
    dashboard_labels['protein'].config(text=f"{summary['protein']} g")
    dashboard_labels['fats'].config(text=f"{summary['fats']} g")
    dashboard_labels['carbs'].config(text=f"{summary['carbs']} g")

    for key in ['calories', 'protein', 'fats', 'carbs']:
        dashboard_labels[key].configure(foreground='#292a36')

    remaining_text = (
        f"{summary['calories_left']:,} kcal remaining"
        if summary['calories_left'] >= 0
        else f"{abs(summary['calories_left']):,} kcal over target"
    )
    results.config(text=f"{remaining_text} • Daily goal: {MAX_CALORIES:,} kcal")
    status_pill.configure(text=f"Daily target: {MAX_CALORIES:,} kcal")

    if 'dashboard_bars' in globals():
        dashboard_bars['protein'].configure(value=min(100, summary['protein_pct']))
        dashboard_bars['fats'].configure(value=min(100, summary['fat_pct']))
        dashboard_bars['carbs'].configure(value=min(100, summary['carbs_pct']))
        animate_calorie_total(summary['calories'])


# Main Program 
meat_types = [meat_type_func(each_menu) for each_menu in ALL_MENUS]

root = tk.Tk()
root.title("CalorAI")
root.configure(bg='#514d78')
root.minsize(1100, 700)
apply_theme(root)

main_frame = ttk.Frame(root, padding=22, style='Outer.TFrame')
main_frame.pack(expand=True, fill='both')
main_frame.grid_columnconfigure(0, weight=0)
main_frame.grid_columnconfigure(1, weight=1)

sidebar = ttk.Frame(main_frame, style='Sidebar.TFrame', padding=(20, 22))
sidebar.grid(row=0, column=0, sticky='ns', padx=(0, 18))

content = ttk.Frame(main_frame, style='TFrame', padding=(12, 12))
content.grid(row=0, column=1, sticky='nsew')
content.grid_columnconfigure(0, weight=1)

brand_row = ttk.Frame(sidebar, style='Sidebar.TFrame')
brand_row.pack(fill='x', pady=(0, 28))

tk.Label(brand_row, text='C', bg='#bd9cf2', fg='#292a36', font=(UI_FONT, 15, 'bold'), width=2, height=1, bd=0).pack(side='left', padx=(0, 10))
tk.Label(brand_row, text='CalorAI', bg='#2b2e3d', fg='#f3f2f8', font=(UI_FONT, 18, 'bold')).pack(side='left')

nav_items = ["Overview", "AI Chat", "Meals", "History", "Profile"]
for item in nav_items:
    button_style = 'SidebarButton.TButton' if item == 'Overview' else 'TButton'
    btn = ttk.Button(sidebar, text=item, style=button_style if item != 'Overview' else 'SidebarButton.TButton', command=lambda x=item: None)
    btn.pack(fill='x', pady=6)

sidebar_bottom = ttk.Frame(sidebar, style='Sidebar.TFrame')
sidebar_bottom.pack(side='bottom', fill='x', pady=(28, 0))

tk.Label(sidebar_bottom, text='Backed connected', bg='#2b2e3d', fg='#f3f2f8', font=(UI_FONT, 9)).pack(anchor='w', pady=(0, 4))
tk.Label(sidebar_bottom, text='Listening on localhost', bg='#2b2e3d', fg='#b0b2c1', font=(UI_FONT, 8)).pack(anchor='w')

# Main content layout
header = ttk.Frame(content, style='TFrame')
header.grid(row=0, column=0, sticky='ew', pady=(16, 22))
header.grid_columnconfigure(0, weight=1)
header.grid_columnconfigure(1, weight=0)

ttk.Label(header, text='Welcome Back!', style='Header.TLabel').grid(row=0, column=0, sticky='w')

tk.Label(header, text='Sunday 2 August', bg='#252735', fg='#b0b2c1', font=(UI_FONT, 10)).grid(row=0, column=1, sticky='e')

status_pill = ttk.Button(header, text='Daily target: 2,300 kcal', style='Pill.TButton')
status_pill.grid(row=1, column=0, sticky='w', pady=(10, 0))

cards = ttk.Frame(content, style='TFrame')
cards.grid(row=1, column=0, sticky='ew', pady=(0, 22))
for i in range(4):
    cards.grid_columnconfigure(i, weight=1)

metric_card_hold = []
metric_card_widgets = {}
metric_card_fills = {
    'Calories': '#f5dd68',
    'Protein': '#70d2e8',
    'Fats': '#ff9d67',
    'Carbs': '#bd9cf2',
}
for card_style in ['Calories', 'Protein', 'Fats', 'Carbs']:
    card = RoundedCard(cards, style_name=f'{card_style}Card.TFrame',
                       padding=(20, 18), fill=metric_card_fills[card_style],
                       min_height=152)
    card.grid(row=0, column=len(metric_card_hold), padx=(0, 14), sticky='ew')
    metric_card_hold.append(card)

summary_labels = {}
dashboard_bars = {}
metric_names = [
    ('Calories consumed', 'calories', 'of daily target', 'Calories'),
    ('Protein', 'protein', 'Goal progress', 'Protein'),
    ('Fats', 'fats', 'Remaining balance', 'Fats'),
    ('Carbs', 'carbs', 'Energy intake', 'Carbs'),
]
for idx, (name, key, subtitle, card_style) in enumerate(metric_names):
    card_shell = metric_card_hold[idx]
    card = card_shell.content
    metric_card_widgets[key] = card_shell
    ttk.Label(card, text=name, style=f'{card_style}Title.TLabel').pack(anchor='w')
    value_label = ttk.Label(card, text='0 kcal', style=f'{card_style}Value.TLabel')
    value_label.pack(anchor='w', pady=(6, 0))
    ttk.Label(card, text=subtitle, style=f'{card_style}Subtitle.TLabel').pack(anchor='w', pady=(2, 0))
    summary_labels[key] = value_label

    progress = ttk.Progressbar(card, orient='horizontal', mode='determinate', length=180,
                               maximum=100, style=f'{card_style}.Horizontal.TProgressbar')
    progress.pack(fill='x', pady=(10, 0))
    dashboard_bars[key] = progress

# Keep meal planner and history stacked with a modern dashboard feel
main_dashboard = ttk.Frame(content, style='TFrame')
main_dashboard.grid(row=2, column=0, sticky='nsew')
main_dashboard.grid_columnconfigure(0, weight=1)
main_dashboard.grid_columnconfigure(1, weight=0)

# Left column: meal selection
left_card = RoundedCard(main_dashboard, style_name='Panel.TFrame',
                        padding=22, fill='#303343')
left_card.grid(row=0, column=0, sticky='nsew', padx=(0, 16))
left_frame = left_card.content
left_frame.grid_columnconfigure(0, weight=1)

ttk.Label(left_frame, text='Today’s meals', style='CardTitle.TLabel').pack(anchor='w', pady=(0, 16))

breakfast = MealFunc(left_frame, 'Breakfast:', menus['breakfast_menu'], meat_types[0], style='Breakfast.TCombobox', width=46)
morning_tea = MealFunc(left_frame, 'Morning Tea:', menus['morning_tea_menu'], meat_types[1], style='MorningTea.TCombobox', width=46)
lunch = MealFunc(left_frame, 'Lunch:', menus['lunch_menu'], meat_types[2], style='Lunch.TCombobox', width=46)
dessert = MealFunc(left_frame, 'Dessert:', menus['dessert_menu'], meat_types[3], style='Dessert.TCombobox', width=46)
dinner = MealFunc(left_frame, 'Dinner:', menus['dinner_menu'], meat_types[4], style='Dinner.TCombobox', width=46)

breakfast_preference, selected_breakfast = breakfast.selections()
morning_tea_preference, selected_morning_tea = morning_tea.selections()
lunch_preference, selected_lunch = lunch.selections()
dessert_preference, selected_dessert = dessert.selections()
dinner_preference, selected_dinner = dinner.selections()

selected_meals = [selected_breakfast, selected_morning_tea, selected_lunch,
                  selected_dessert, selected_dinner]

menu_map = {"breakfast_menu": breakfast, "morning_tea_menu": morning_tea,
            "lunch_menu": lunch, "dessert_menu": dessert,
            "dinner_menu": dinner}

for var in selected_meals:
    var.trace_add('write', on_selection_change)
load_selections()

button_frame = ttk.Frame(left_frame, style='TFrame')
button_frame.pack(fill='x', pady=(22, 0))

calculate_btn = ttk.Button(button_frame, text='Calculate Nutrition', command=lambda: calculation_and_graph(), style='Action.TButton')
calculate_btn.pack(fill='x', pady=4)

ttk.Button(button_frame, text='Create Custom Meal', command=lambda: toggle_create_custom_meal(), style='Secondary.TButton').pack(fill='x', pady=4)
ttk.Button(button_frame, text='Delete Custom Meal', command=lambda: toggle_delete_meal(), style='Secondary.TButton').pack(fill='x', pady=4)
ttk.Button(button_frame, text='Set Max Calories', command=lambda: toggle_max_cal(), style='Secondary.TButton').pack(fill='x', pady=4)
ttk.Button(button_frame, text='AI assistant', command=toggle_ai_assistant, style='Secondary.TButton').pack(fill='x', pady=4)

results = ttk.Label(left_frame, text='', style='TLabel', foreground='#f3f2f8', justify='left')
results.pack(anchor='w', pady=(18, 0))

# Right column: previous-day summary and AI card
right_column = ttk.Frame(main_dashboard, style='TFrame')
right_column.grid(row=0, column=1, sticky='nsew')
right_column.grid_columnconfigure(0, weight=1)

chart_card = RoundedCard(right_column, style_name='Panel.TFrame',
                         padding=(22, 20), fill='#303343', min_height=120)
chart_card.grid(row=0, column=0, sticky='nsew')
right_frame = chart_card.content

history_card = RoundedCard(right_column, style_name='Panel.TFrame',
                           padding=(22, 20), fill='#303343')
history_card.grid(row=1, column=0, sticky='ew', pady=(18, 0))
history_panel = history_card.content

ttk.Label(history_panel, text='Previous days', style='CardTitle.TLabel').pack(anchor='w')
for day, value in [('Mon', '1,840 kcal'), ('Tue', '1,920 kcal'), ('Wed', '1,760 kcal')]:
    ttk.Label(history_panel, text=f'{day}: {value}', background='#303343', foreground='#f3f2f8', font=(UI_FONT, 10)).pack(anchor='w', pady=(12, 0))

ai_card = RoundedCard(right_column, style_name='Panel.TFrame',
                       padding=(22, 20), fill='#303343')
ai_card.grid(row=2, column=0, sticky='ew', pady=(18, 0))
ai_panel = ai_card.content
ttk.Label(ai_panel, text='AI coach', style='CardTitle.TLabel').pack(anchor='w')

tk.Label(ai_panel, text='You are on track to finish the day in a healthy range.', bg='#303343', fg='#f3f2f8', font=(UI_FONT, 11), justify='left', wraplength=220).pack(anchor='w', pady=(14, 12))

ttk.Button(ai_panel, text='Open AI assistant', command=toggle_ai_assistant, style='Action.TButton').pack(fill='x')

# add a premium mini summary in the chart area
summary_chip = ttk.Label(right_frame, text='Calories in check', style='Subtle.TLabel', foreground='#b0b2c1', background='#303343')
summary_chip.pack(anchor='w', pady=(0, 16))

# keep dashboard labels accessible for updates
# the metric values are set from current selections at startup
assistant = AIAssistant(root, api_key, get_ai_nutrition_context)

dashboard_labels = summary_labels
refresh_dashboard()

root.update_idletasks()
window_width = root.winfo_reqwidth()
window_height = root.winfo_reqheight()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_x = (screen_width - window_width) // 2
window_y = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
#wait
