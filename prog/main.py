import tkinter as tk
from tkinter import ttk
import json
import os
import queue
import threading
import urllib.error
import urllib.request
from calculator import CalcFunc
from meal import MealFunc
# AI shit
import os
from dotenv import load_dotenv

# This loads the variables from your .env file into the system
load_dotenv()

# Now you can pull the key safely into your code
api_key = os.getenv("API_KEY")
with open('menus.json', 'r') as f:
    menus = json.load(f)

"""CONSTANTS"""
MAX_CALORIES = 2300  # preset for maximum calories
charts = None  # allows calorie calculator button to run
ALL_MENUS = [menus["breakfast_menu"], menus["morning_tea_menu"],
            menus["lunch_menu"], menus["dessert_menu"],
            menus["dinner_menu"],]

custom_meals = []  # empty list to add custom meals
ai_history = []
ai_request_pending = False
ai_active_request_id = 0
ai_response_queue = queue.Queue()
menu_dict = {"Breakfast": "breakfast_menu", 
            "Morning Tea": "morning_tea_menu",
            "Lunch": "lunch_menu", "Dessert": "dessert_menu",
            "Dinner": "dinner_menu"}
menu_names = ["Breakfast", "Morning Tea", "Lunch",
            "Dessert","Dinner"]

def save_selections():
    """Persist data on program close."""
    selections = [var.get() for var in selected_meals]  # for each selection
    with open('last_selections.json', 'w') as f:  # open external JSON file
        json.dump(selections, f)  # save selections in external JSON file

def on_closing():
    """Detect program close, run data persistence."""
    save_selections()  # Runs JSON code
    root.destroy()  # Exit program 

def load_selections():
    """Load saved data from previous use of program."""
    if os.path.exists('last_selections.json'):  # External JSON file exists?
        with open('last_selections.json', 'r') as f:  # Open external JSON file
            try:
                selections = json.load(f)  # Extract saved selections from file
                for var, value in zip(selected_meals, selections):
                    var.set(value)  # Set each dropdown box with value from before
            except Exception:
                pass

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
    """Style the program."""
    style = ttk.Style(root)  # style root frame
    style.theme_use('clam')  # prebuilded theme
    teal = '#E0F7FA'
    style.configure('TFrame', background=teal)  # Make entire program background teal
    style.configure('TLabel', background=teal, font=('Segoe UI', 14, 'italic'),
                    foreground='#2c3e50')  # Edt headings
    style.configure('Header.TLabel', background=teal, font=('Segoe UI', 30, 'bold'),
                    foreground='#2c3e50')  # Edit main heading
    style.configure('TButton', font=('Segoe UI', 12),
                    padding=10, background='#4DD0E1', foreground='#fff')  # Edit buttons
    style.map('TButton', background=[('active', '#0097A7')],
             foreground=[('active', '#fff')])  # Edit button on hover
    style.configure('TEntry', font=('Segoe UI', 15))  # Set default font colours and font
    style.configure('TCombobox', font=('Segoe UI', 12), padding=6)  # Edit dropdown box

    """CUSTOM COMBOBOX STYLES"""

    style.configure('Breakfast.TCombobox',
        fieldbackground='#FFF8E1', background='#FFD54F',
        foreground='#4527A0',font=('Segoe UI', 12, 'bold'),
        padding=12)

    style.configure('MorningTea.TCombobox',
        fieldbackground='#E3F2FD', background='#90CAF9',
        foreground='#01579B', font=('Segoe UI', 12),
        padding=12)
    
    style.configure('Lunch.TCombobox',
        fieldbackground='#F1F8E9', background='#AED581',
        foreground='#33691E', font=('Segoe UI', 12, 'italic'),
        padding=12)
    
    style.configure('Dessert.TCombobox',
        fieldbackground='#F3E5F5', background='#CE93D8',
        foreground='#6A1B9A', font=('Segoe UI', 12, 'bold'),
        padding=12)
    
    style.configure('Dinner.TCombobox',
        fieldbackground='#ECEFF1', background='#90A4AE',
        foreground='#263238', font=('Segoe UI', 12),
        padding=12)
    
    style.configure('MenuChoice.TCombobox',
        fieldbackground='#FFECB3', background='#FFD54F',
        foreground='#BF360C', font=('Segoe UI', 12, 'bold'),
        padding=12)

def on_selection_change(*args):
    """Change saved data when user changes it even while program runs."""
    save_selections()

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
    with open('menus.json', 'w') as f:  # Open external JSON file
        json.dump(menus, f, indent=4)  # Add to JSON file for data pers
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
        with open('menus.json', 'w') as f:  # Open external JSON file
            json.dump(menus, f, indent=4)  # Delete custom meal from JSON file
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
    """Calculate max calories of user using physical attrs."""

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

def append_ai_message(transcript, speaker, message):
    transcript.configure(state="normal")
    transcript.insert(tk.END, f"{speaker}:\n{message}\n\n")
    transcript.configure(state="disabled")
    transcript.see(tk.END)

def send_ai_message(prompt_entry, send_button, status_label, transcript, frame):
    """Send a meal-planning question to Gemini without blocking Tkinter."""
    global ai_request_pending, ai_active_request_id
    prompt = prompt_entry.get().strip()
    if not prompt:
        return
    if ai_request_pending:
        status_label.config(text="Please wait for the current reply.")
        return

    if not api_key:
        status_label.config(text="Set the API Key environment variable to use AI assistant.")
        return

    ai_active_request_id += 1
    request_id = ai_active_request_id
    context = get_ai_nutrition_context()
    system_instruction = (
        "You are a practical meal-planning assistant. Use the calorie limit, remaining calories, "
        "selected meals, and menu nutrition data below when making recommendations. Prefer foods "
        "from the available menu and do not claim a meal fits the remaining budget if its listed "
        "calories exceed it. If calories are already over the limit, say so plainly. Give concise, "
        "general food suggestions and do not present them as medical advice.\n\n"
        f"Current meal-planner data:\n{json.dumps(context, ensure_ascii=False)}"
    )
    user_entry = {
        "role": "user",
        "parts": [{"text": prompt}],
        "display": prompt,
    }
    ai_history.append(user_entry)
    contents = [
        {"role": item["role"], "parts": item["parts"]}
        for item in ai_history
    ]

    prompt_entry.delete(0, tk.END)
    append_ai_message(transcript, "You", prompt)
    send_button.configure(state="disabled")
    status_label.configure(text="Please wait...")
    ai_request_pending = True

    def request_recommendation():
        try:
            endpoint = (
                "https://generativelanguage.googleapis.com/v1beta/"
                "models/gemini-3.8-flash:generateContent"
            )
            body = {
                "systemInstruction": {"parts": [{"text": system_instruction}]},
                "contents": contents,
                "generationConfig": {"temperature": 0.4, "maxOutputTokens": 700},
            }
            request = urllib.request.Request(
                endpoint,
                data=json.dumps(body).encode("utf-8"),
                headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
                method="POST",
            )
            with urllib.request.urlopen(request, timeout=20) as response:
                result = json.loads(response.read().decode("utf-8"))
            parts = result.get("candidates", [{}])[0].get("content", {}).get("parts", [])
            answer = "\n".join(part.get("text", "") for part in parts).strip()
            if not answer:
                raise ValueError("Gemini returned no text. Try asking a different question.")
            ai_response_queue.put((request_id, answer, None, user_entry, frame))
        except urllib.error.HTTPError as error:
            try:
                error_body = json.loads(error.read().decode("utf-8"))
                message = error_body.get("error", {}).get("message", str(error))
            except Exception:
                message = str(error)
            ai_response_queue.put((request_id, None, f"Gemini API error: {message}", user_entry, frame))
        except Exception as error:
            ai_response_queue.put((request_id, None, f"Gemini request failed: {error}", user_entry, frame))

    def finish_request(answer, error, sent_entry, request_frame):
        global ai_request_pending
        if request_id != ai_active_request_id or not ai_request_pending:
            return
        ai_request_pending = False
        if error:
            if ai_history and ai_history[-1] is sent_entry:
                ai_history.pop()
        else:
            ai_history.append({
                "role": "model",
                "parts": [{"text": answer}],
                "display": answer,
            })

        current_frame = getattr(show_ai_assistant, "frame", None)
        if current_frame is not None and current_frame.winfo_exists():
            show_ai_assistant.send_button.configure(state="normal")
            if current_frame is request_frame:
                if error:
                    append_ai_message(show_ai_assistant.transcript, "Assistant", error)
                    show_ai_assistant.status_label.configure(text="Request failed.")
                else:
                    append_ai_message(show_ai_assistant.transcript, "Gemini", answer)
                    show_ai_assistant.status_label.configure(text="Ready")

    def poll_for_response():
        try:
            response = ai_response_queue.get_nowait()
        except queue.Empty:
            if ai_request_pending and request_id == ai_active_request_id:
                root.after(100, poll_for_response)
            return
        response_id, *response_data = response
        if response_id != request_id:
            if ai_request_pending and request_id == ai_active_request_id:
                root.after(100, poll_for_response)
            return
        finish_request(*response_data)

    def timeout_request():
        if ai_request_pending and request_id == ai_active_request_id:
            finish_request(
                None,
                "Gemini timed out after 30 seconds. Check your connection and API key, then retry.",
                user_entry,
                frame,
            )

    root.after(100, poll_for_response)
    root.after(30000, timeout_request)
    threading.Thread(target=request_recommendation, daemon=True).start()

def show_ai_assistant():
    """Display the Gemini meal-planning chat."""
    hide_charts()
    assistant_window = tk.Toplevel(root)
    assistant_window.title("AI assistant")
    assistant_window.geometry("720x640")
    assistant_window.minsize(560, 480)
    assistant_window.transient(root)
    assistant_window.protocol(
        "WM_DELETE_WINDOW",
        lambda: toggle_ai_assistant(shown=True),
    )
    frame = ttk.Frame(assistant_window, padding=24)
    show_ai_assistant.frame = assistant_window
    frame.pack(expand=True, fill="both")

    ttk.Label(frame, text="AI assistant", style="Header.TLabel").pack(anchor="w")
    ttk.Label(
        frame,
        text="Your selected meals and nutrition totals are sent to Gemini.",
        wraplength=560,
    ).pack(anchor="w", pady=(0, 10))

    conversation_frame = ttk.Frame(frame)
    conversation_frame.pack(fill="both", expand=True)
    scrollbar = ttk.Scrollbar(conversation_frame)
    scrollbar.pack(side="right", fill="y")
    transcript = tk.Text(
        conversation_frame,
        height=18,
        width=64,
        wrap="word",
        state="disabled",
        yscrollcommand=scrollbar.set,
    )
    transcript.pack(side="left", fill="both", expand=True)
    scrollbar.configure(command=transcript.yview)
    show_ai_assistant.transcript = transcript

    for item in ai_history:
        speaker = "You" if item["role"] == "user" else "Gemini"
        append_ai_message(transcript, speaker, item.get("display", item["parts"][0]["text"]))

    status_label = ttk.Label(frame, text="Ready")
    status_label.pack(anchor="w", pady=(8, 4))
    show_ai_assistant.status_label = status_label

    input_frame = ttk.Frame(frame)
    input_frame.pack(fill="x")
    prompt_entry = ttk.Entry(input_frame)
    prompt_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
    send_button = ttk.Button(
        input_frame,
        text="Send",
        command=lambda: send_ai_message(
            prompt_entry, send_button, status_label, transcript, assistant_window
        ),
    )
    send_button.pack(side="left")
    show_ai_assistant.send_button = send_button
    if ai_request_pending:
        send_button.configure(state="disabled")
        status_label.configure(text="Gemini is preparing a recommendation...")
    prompt_entry.bind(
        "<Return>",
        lambda event: (send_button.invoke(), "break")[1],
    )
    ttk.Button(
        frame,
        text="Close",
        command=lambda: toggle_ai_assistant(shown=True),
    ).pack(anchor="e", pady=(8, 0))

def toggle_ai_assistant(shown=False):
    """Open or close the meal-planning assistant."""
    close_all_toggle_sections()
    if not shown:
        show_ai_assistant()

def close_all_toggle_sections():
    """Close all other open sections."""
    # For meal creation section
    if hasattr(create_custom_meal, "inputs_frame") and create_custom_meal.inputs_frame.winfo_exists():
        create_custom_meal.inputs_frame.destroy()
        del create_custom_meal.inputs_frame
    # For meal deletion section
    if hasattr(delete_custom_meal, "frame") and delete_custom_meal.frame.winfo_exists():
        delete_custom_meal.frame.destroy()
        del delete_custom_meal.frame
    # For calorie calculator section
    if hasattr(show_calorie_input, "frame") and show_calorie_input.frame.winfo_exists():
        show_calorie_input.frame.destroy()
        del show_calorie_input.frame
    # For the AI assistant
    if hasattr(show_ai_assistant, "frame") and show_ai_assistant.frame.winfo_exists():
        show_ai_assistant.frame.destroy()
        del show_ai_assistant.frame


# Main Program
meat_types = [meat_type_func(each_menu) for each_menu in ALL_MENUS]  # Run meat_type_func func for all menus

root = tk.Tk()
apply_theme(root)  # Run apply_theme at program start

# Center the main section of program (dropdwon boxes)
main_frame = ttk.Frame(root)
main_frame.pack(expand=True, fill='both', padx=0, pady=6)

# Configuration of other frames
left_frame = ttk.Frame(main_frame)
right_frame = ttk.Frame(main_frame)

main_frame.grid_anchor('center')

left_frame.grid(row=0, column=0, sticky="ns", padx=(0,36), pady=36)
right_frame.grid(row=0, column=1, sticky="nsew", padx=(0,36), pady=36)

# Main heading
ttk.Label(left_frame, text="Select Your Meals", style='Header.TLabel').pack(pady=(0,10))

# Dropdown boxes for each meal. Runs MealFunc class from meal.py to store data.
breakfast = MealFunc(left_frame, "Breakfast:", menus["breakfast_menu"], meat_types[0], style="Breakfast.TCombobox", width=78)
morning_tea = MealFunc(left_frame, "Morning Tea:", menus["morning_tea_menu"], meat_types[1], style="MorningTea.TCombobox", width=78)
lunch = MealFunc(left_frame, "Lunch:", menus["lunch_menu"], meat_types[2], style="Lunch.TCombobox", width=78)
dessert = MealFunc(left_frame, "Dessert:", menus["dessert_menu"], meat_types[3], style="Dessert.TCombobox", width=78)
dinner = MealFunc(left_frame, "Dinner:", menus["dinner_menu"], meat_types[4], style="Dinner.TCombobox", width=78)

# Set variables for easy configurate later
breakfast_preference, selected_breakfast = breakfast.selections()
morning_tea_preference, selected_morning_tea = morning_tea.selections()
lunch_preference, selected_lunch = lunch.selections()
dessert_preference, selected_dessert = dessert.selections()
dinner_preference, selected_dinner = dinner.selections()

selected_meals = [selected_breakfast, selected_morning_tea, selected_lunch,
                  selected_dessert, selected_dinner]  # Store data for selected meals

menu_map = {"breakfast_menu": breakfast, "morning_tea_menu": morning_tea,
            "lunch_menu": lunch, "dessert_menu": dessert, 
            "dinner_menu": dinner}


for var in selected_meals:  # For each selected meal
    var.trace_add('write', on_selection_change)  # Overwrite saved meal
load_selections()  # Run to avoid eror

# Show results and informaton data
results = ttk.Label(left_frame, text="", style='TLabel', font=('Segoe UI', 11, 'italic'))
results.pack(pady=(10,0))

# Buttons
button_frame = ttk.Frame(left_frame)  # Create frame inside of left_frame
button_frame.pack(fill='x', pady=(20,20))
ttk.Button(button_frame, text="Calculate Nutrition", command=lambda:calculation_and_graph()).pack(fill='x', pady=3)
ttk.Button(button_frame, text="Create Custom Meal", command=lambda:toggle_create_custom_meal()).pack(fill='x', pady=3)
ttk.Button(button_frame, text="Delete Custom Meal", command=lambda:toggle_delete_meal()).pack(fill='x', pady=3)
ttk.Button(button_frame, text="Set Max Calories", command=lambda:toggle_max_cal()).pack(fill='x', pady=3)
ttk.Button(button_frame, text="AI assistant", command=toggle_ai_assistant).pack(fill='x', pady=3)

root.update_idletasks()
window_width = root.winfo_reqwidth()
window_height = root.winfo_reqheight()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_x = (screen_width - window_width) // 2
window_y = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")

root.protocol("WM_DELETE_WINDOW", on_closing)  # Detect program's close, run data save to JSON.
root.mainloop()