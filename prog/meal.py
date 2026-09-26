import tkinter as tk
from tkinter import ttk

class MealFunc:
    """Filter selection of meals."""

    def __init__(self, main_frame, meal_name, menu_values, meat_types, style="TCombobox", width=24):
        """Initialise (self initialise) attributes given."""
        self.meal_frame = ttk.Frame(main_frame)
        self.meal_frame.pack(fill='x', pady=6)

        self.label = ttk.Label(self.meal_frame, text=meal_name)  # Meal titles
        self.label.pack(anchor='w', pady=(0, 4))

        self.meat = tk.StringVar(value='None')  # None is the first option
        # Combobox for filters
        self.filter_dropdown = ttk.Combobox(
            self.meal_frame,
            textvariable=self.meat,
            values=meat_types,
            state="readonly",
            style=style,
            width=25
        )
        self.filter_dropdown.pack(side='left', padx=(0, 12))

        self.meal = tk.StringVar()
        self.meal_selection = ttk.Combobox(
            self.meal_frame,
            textvariable=self.meal,
            values=list(menu_values.keys()),
            state="readonly",
            style=style,
            width=width
        )
        self.meal_selection.pack(side='left', padx=(0, 12))

        def filter(*args):
            preferred_meat = self.meat.get()
            filtered = []
            for selected_meal, meal_details in menu_values.items():
                if (
                    preferred_meat == 'None'
                    or preferred_meat == meal_details['meat']
                    or selected_meal == 'NO SELECTION/SKIP'
                ):
                    filtered.append(selected_meal)
            self.meal_selection['values'] = filtered
            if filtered:
                self.meal.set(filtered[0])

        self.meat.trace_add('write', filter)
        filter()

    def selections(self):
        """Return values."""
        return self.meat, self.meal

    def update_menu_options(self, new_menu_dict):
        menu_names = list(new_menu_dict.keys())
        self.meal_selection['values'] = menu_names
        if menu_names:
            self.meal.set(menu_names[0])