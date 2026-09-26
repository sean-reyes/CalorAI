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

# This loads the variables from your .env file into the system
load_dotenv()

# Now you can pull the key safely into your code
api_key = os.getenv("API_KEY")
menus = load_menus()

"""CONSTANTS"""
MAX_CALORIES = 2300  # preset for maximum calories
charts = None  # allows calorie calculator button to run
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
    """Style the program with a cleaner dashboard aesthetic."""
    style = ttk.Style(root)
    style.theme_use('clam')

    bg = '#eef3ee'
    panel = '#f7f7f3'
    white = '#ffffff'
    pale_green = '#dfeadf'
    deep_green = '#1f3b2e'
    soft_green = '#6b8f6f'
    soft_teal = '#dff3ef'
    orange = '#f4b183'
    red = '#e77a6d'
    purple = '#b39ddb'
    text = '#243127'
    muted = '#68796f'
    shadow = '#dfe6dc'

    root.configure(bg=bg)

    style.configure('TFrame', background=bg)
    style.configure('TLabel', background=bg, foreground=text, font=('Segoe UI', 11))
    style.configure('Header.TLabel', background=bg, foreground=deep_green,
                    font=('Segoe UI', 30, 'bold'))
    style.configure('Brand.TLabel', background=bg, foreground=deep_green,
                    font=('Segoe UI', 22, 'bold'))
    style.configure('Subtle.TLabel', background=bg, foreground=muted,
                    font=('Segoe UI', 10, 'bold'))
    style.configure('CardTitle.TLabel', background=panel, foreground=deep_green,
                    font=('Segoe UI', 10, 'bold'))
    style.configure('MetricValue.TLabel', background=panel, foreground=deep_green,
                    font=('Segoe UI', 28, 'bold'))
    style.configure('MetricSubtitle.TLabel', background=panel, foreground=muted,
                    font=('Segoe UI', 9))
    style.configure('Panel.TFrame', background=panel)
    style.configure('Sidebar.TFrame', background=white)
    style.configure('Action.TButton', font=('Segoe UI', 10, 'bold'),
                    padding=(12, 8), background='#2f4f43', foreground='white')
    style.configure('Secondary.TButton', font=('Segoe UI', 10, 'bold'),
                    padding=(12, 8), background='#edf2ee', foreground=deep_green)
    style.configure('Pill.TButton', font=('Segoe UI', 9, 'bold'),
                    padding=(10, 6), background='#e5efe6', foreground=deep_green)
    style.map('Action.TButton', background=[('active', '#244536')],
              foreground=[('active', 'white')])
    style.map('Secondary.TButton', background=[('active', '#dfeadf')],
              foreground=[('active', deep_green)])
    style.map('Pill.TButton', background=[('active', '#d7e7d8')],
              foreground=[('active', deep_green)])
    style.configure('TEntry', font=('Segoe UI', 11), fieldbackground=white)
    style.configure('TCombobox', font=('Segoe UI', 10), padding=6)
    style.map('TCombobox', fieldbackground=[('readonly', white)])

    style.configure('Breakfast.TCombobox', fieldbackground='#fff8e5', background='#f7d486',
                    foreground='#3b2d1f', font=('Segoe UI', 10, 'bold'), padding=10)
    style.configure('MorningTea.TCombobox', fieldbackground='#edf5ff', background='#b7d6f7',
                    foreground='#173b52', font=('Segoe UI', 10), padding=10)
    style.configure('Lunch.TCombobox', fieldbackground='#edf9ee', background='#b8d9a9',
                    foreground='#234d2d', font=('Segoe UI', 10), padding=10)
    style.configure('Dessert.TCombobox', fieldbackground='#f9edf9', background='#d9b4e8',
                    foreground='#4c2f6d', font=('Segoe UI', 10, 'bold'), padding=10)
    style.configure('Dinner.TCombobox', fieldbackground='#eef4f4', background='#c4d3d8',
                    foreground='#1d2d33', font=('Segoe UI', 10), padding=10)
    style.configure('MenuChoice.TCombobox', fieldbackground='#fff5ed', background='#ffd4b2',
                    foreground='#653b16', font=('Segoe UI', 10, 'bold'), padding=10)

    style.configure('DashboardCard.TFrame', background=panel)
    style.configure('MealPanel.TFrame', background=white)
    style.configure('SidebarButton.TButton', background='white', foreground=text,
                    font=('Segoe UI', 10), padding=(16, 10))
    style.map('SidebarButton.TButton', background=[('active', pale_green)])

    root.option_add('*TCombobox*Listbox*Font', ('Segoe UI', 10))
    root.option_add('*TCombobox*Listbox*Background', white)
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
        "calories_left": calories_left,
        "protein": totals["protein"],
        "fats": totals["fats"],
        "carbs": totals["carbs"],
        "protein_pct": protein_pct,
        "carbs_pct": carbs_pct,
        "fat_pct": fat_pct,
        "calories_pct": max(0, min(100, (totals["calories"] / MAX_CALORIES) * 100)) if MAX_CALORIES else 0,
    }


def refresh_dashboard():
    """Update the dashboard summary cards with live values."""
    if 'dashboard_labels' not in globals():
        return
    summary = build_dashboard_summary()
    dashboard_labels['calories_left'].config(text=f"{summary['calories_left']} kcal")
    dashboard_labels['protein'].config(text=f"{summary['protein']} g")
    dashboard_labels['fats'].config(text=f"{summary['fats']} g")
    dashboard_labels['carbs'].config(text=f"{summary['carbs']} g")

    for key in ['calories_left', 'protein', 'fats', 'carbs']:
        dashboard_labels[key].configure(foreground='#1f3b2e')
    if summary['calories_left'] < 0:
        dashboard_labels['calories_left'].configure(foreground='#b85c52')

    status_text = "On track" if summary['calories_left'] >= 0 else "Over target"
    results.config(text=f"{status_text} • Daily goal: {MAX_CALORIES} kcal")

    if 'dashboard_bars' in globals():
        dashboard_bars['calories_left'].configure(value=summary['calories_pct'])
        dashboard_bars['protein'].configure(value=min(100, summary['protein_pct']))
        dashboard_bars['fats'].configure(value=min(100, summary['fat_pct']))
        dashboard_bars['carbs'].configure(value=min(100, summary['carbs_pct']))


# Main Program
meat_types = [meat_type_func(each_menu) for each_menu in ALL_MENUS]

root = tk.Tk()
root.title("CalorAI")
root.configure(bg='#eef3ee')
root.minsize(1100, 700)
apply_theme(root)

main_frame = ttk.Frame(root, padding=18)
main_frame.pack(expand=True, fill='both')
main_frame.grid_columnconfigure(0, weight=0)
main_frame.grid_columnconfigure(1, weight=1)

sidebar = ttk.Frame(main_frame, style='Sidebar.TFrame', padding=(18, 20))
sidebar.grid(row=0, column=0, sticky='ns', padx=(0, 18))

content = ttk.Frame(main_frame, style='TFrame', padding=(8, 4))
content.grid(row=0, column=1, sticky='nsew')
content.grid_columnconfigure(0, weight=1)

brand_row = ttk.Frame(sidebar, style='Sidebar.TFrame')
brand_row.pack(fill='x', pady=(0, 24))

tk.Label(brand_row, text='C', bg='#f1c4d1', fg='#2b2b2b', font=('Segoe UI', 15, 'bold'), width=2, height=1, bd=0).pack(side='left', padx=(0, 10))
tk.Label(brand_row, text='CalorAI', bg='white', fg='#20342d', font=('Segoe UI', 18, 'bold')).pack(side='left')

nav_items = ["Overview", "AI Chat", "Meals", "History", "Profile"]
for item in nav_items:
    button_style = 'SidebarButton.TButton' if item == 'Overview' else 'TButton'
    btn = ttk.Button(sidebar, text=item, style=button_style if item != 'Overview' else 'SidebarButton.TButton', command=lambda x=item: None)
    btn.pack(fill='x', pady=4)

sidebar_bottom = ttk.Frame(sidebar, style='Sidebar.TFrame')
sidebar_bottom.pack(side='bottom', fill='x', pady=(28, 0))

tk.Label(sidebar_bottom, text='Backed connected', bg='white', fg='#3a4c44', font=('Segoe UI', 9)).pack(anchor='w', pady=(0, 4))
tk.Label(sidebar_bottom, text='Listening on localhost', bg='white', fg='#6b7f73', font=('Segoe UI', 8)).pack(anchor='w')

# Main content layout
header = ttk.Frame(content, style='TFrame')
header.grid(row=0, column=0, sticky='ew', pady=(0, 16))
header.grid_columnconfigure(0, weight=1)
header.grid_columnconfigure(1, weight=0)

ttk.Label(header, text='Good evening.', style='Header.TLabel').grid(row=0, column=0, sticky='w')

tk.Label(header, text='Sunday 2 August', bg='#eef3ee', fg='#5f7669', font=('Segoe UI', 10)).grid(row=0, column=1, sticky='e')

status_pill = ttk.Button(header, text='Daily target: 2,300 kcal', style='Pill.TButton')
status_pill.grid(row=1, column=0, sticky='w', pady=(10, 0))

cards = ttk.Frame(content, style='TFrame')
cards.grid(row=1, column=0, sticky='ew', pady=(0, 18))
for i in range(4):
    cards.grid_columnconfigure(i, weight=1)

metric_card_hold = []
for _ in range(4):
    card = ttk.Frame(cards, style='Panel.TFrame', padding=(18, 16))
    card.grid(row=0, column=len(metric_card_hold), padx=(0, 12), sticky='ew')
    metric_card_hold.append(card)

summary_labels = {}
dashboard_bars = {}
metric_names = [
    ('Calories left', 'calories_left', 'Daily target'),
    ('Protein', 'protein', 'Goal progress'),
    ('Fats', 'fats', 'Remaining balance'),
    ('Carbs', 'carbs', 'Energy intake'),
]
for idx, (name, key, subtitle) in enumerate(metric_names):
    card = metric_card_hold[idx]
    ttk.Label(card, text=name, style='CardTitle.TLabel').pack(anchor='w')
    value_label = ttk.Label(card, text='0 kcal', style='MetricValue.TLabel')
    value_label.pack(anchor='w', pady=(6, 0))
    ttk.Label(card, text=subtitle, style='MetricSubtitle.TLabel').pack(anchor='w', pady=(2, 0))
    summary_labels[key] = value_label

    progress = ttk.Progressbar(card, orient='horizontal', mode='determinate', length=180, maximum=100)
    progress.pack(fill='x', pady=(10, 0))
    dashboard_bars[key] = progress

# Keep meal planner and history stacked with a modern dashboard feel
main_dashboard = ttk.Frame(content, style='TFrame')
main_dashboard.grid(row=2, column=0, sticky='nsew')
main_dashboard.grid_columnconfigure(0, weight=1)
main_dashboard.grid_columnconfigure(1, weight=0)

# Left column: meal selection
left_frame = ttk.Frame(main_dashboard, style='Panel.TFrame', padding=18)
left_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 16))
left_frame.grid_columnconfigure(0, weight=1)

ttk.Label(left_frame, text='Today’s meals', style='CardTitle.TLabel').pack(anchor='w', pady=(0, 12))

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
button_frame.pack(fill='x', pady=(18, 0))

calculate_btn = ttk.Button(button_frame, text='Calculate Nutrition', command=lambda: calculation_and_graph(), style='Action.TButton')
calculate_btn.pack(fill='x', pady=3)

ttk.Button(button_frame, text='Create Custom Meal', command=lambda: toggle_create_custom_meal(), style='Secondary.TButton').pack(fill='x', pady=3)
ttk.Button(button_frame, text='Delete Custom Meal', command=lambda: toggle_delete_meal(), style='Secondary.TButton').pack(fill='x', pady=3)
ttk.Button(button_frame, text='Set Max Calories', command=lambda: toggle_max_cal(), style='Secondary.TButton').pack(fill='x', pady=3)
ttk.Button(button_frame, text='AI assistant', command=toggle_ai_assistant, style='Secondary.TButton').pack(fill='x', pady=3)

results = ttk.Label(left_frame, text='', style='TLabel', foreground='#4d5d52', justify='left')
results.pack(anchor='w', pady=(14, 0))

# Right column: previous-day summary and AI card
right_column = ttk.Frame(main_dashboard, style='TFrame')
right_column.grid(row=0, column=1, sticky='nsew')
right_column.grid_columnconfigure(0, weight=1)

right_frame = ttk.Frame(right_column, style='Panel.TFrame', padding=(18, 16))
right_frame.grid(row=0, column=0, sticky='nsew')

history_panel = ttk.Frame(right_column, style='Panel.TFrame', padding=(18, 16))
history_panel.grid(row=1, column=0, sticky='ew', pady=(16, 0))

ttk.Label(history_panel, text='Previous days', style='CardTitle.TLabel').pack(anchor='w')
for day, value in [('Mon', '1,840 kcal'), ('Tue', '1,920 kcal'), ('Wed', '1,760 kcal')]:
    ttk.Label(history_panel, text=f'{day}: {value}', background='#f7f7f3', foreground='#3a4d45', font=('Segoe UI', 10)).pack(anchor='w', pady=(10, 0))

ai_panel = ttk.Frame(right_column, style='Panel.TFrame', padding=(18, 16))
ai_panel.grid(row=2, column=0, sticky='ew', pady=(16, 0))
ttk.Label(ai_panel, text='AI coach', style='CardTitle.TLabel').pack(anchor='w')

tk.Label(ai_panel, text='You are on track to finish the day in a healthy range.', bg='#f7f7f3', fg='#31473d', font=('Segoe UI', 11), justify='left', wraplength=220).pack(anchor='w', pady=(12, 10))

ttk.Button(ai_panel, text='Open AI assistant', command=toggle_ai_assistant, style='Action.TButton').pack(fill='x')

# add a premium mini summary in the chart area
summary_chip = ttk.Label(right_frame, text='Calories in check', style='Subtle.TLabel', foreground='#3a4c44', background='#f7f7f3')
summary_chip.pack(anchor='w', pady=(0, 12))

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
