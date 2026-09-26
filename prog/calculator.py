import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.gridspec as gridspec
CHART_BG = '#252735'
CHART_TEXT = '#f3f2f8'

RDI_PERCENTS = {'carbs': 0.4, 'fats': 0.3, 'protein': 0.3}

class CalcFunc:
    """Calculate Nutrition."""

    def __init__(self, charts, all_menus, selected_meals,
                 results, frame, root, max_calories):
        self.charts = charts
        self.all_menus = all_menus
        self.selected_meals = selected_meals
        self.results = results
        self.frame = frame
        self.root = root
        self.max_calories = max_calories

    def calculation_and_graph(self):
        if all(meal_selected.get() == "NO SELECTION/SKIP"
               for meal_selected in self.selected_meals):
            self.results.config(
                text="No meals selected. \nPlease select at least one meal."
            )
            if self.charts is not None:
                self.charts.get_tk_widget().destroy()
                self.charts = None
            for widget in self.frame.winfo_children():
                widget.destroy()
            self.root.update_idletasks()
            self.root.geometry("")
            return self.charts

        try:
            nutrients = ['calories', 'protein', 'fats', 'carbs']
            nutrient_totals = {}
            for nutrient in nutrients:
                nutrient_value = 0
                for menu, selection_var in zip(self.all_menus, self.selected_meals):
                    nutrient_value += menu[selection_var.get()][nutrient]
                nutrient_totals[nutrient] = nutrient_value
            total_calories, total_protein, total_fats, total_carbs = (
                nutrient_totals[n] for n in nutrients)
            calories_remaining = self.max_calories - total_calories
            total_macros = total_fats + total_protein + total_carbs
            rdi = {nutrient_type: total_macros * value
                   for nutrient_type, value in RDI_PERCENTS.items()}

            self.results.config(
                text=(f"Total Nutritional Information:\n"
                      f"Calories: {total_calories} kcal, "
                      f"Protein: {total_protein} g, "
                      f"Fats: {total_fats} g"))
            with open("nutrition_report.txt", "w") as f:
                f.write(
                    f"MEALS SELECTED:\n\n"
                    f"\nBreakfast: {self.selected_meals[0].get()}\n\n"
                    f"\nMorning Tea: {self.selected_meals[1].get()}\n\n"
                    f"\nLunch: {self.selected_meals[2].get()}\n\n"
                    f"\nDinner: {self.selected_meals[3].get()}\n\n"
                    f"\nDessert: {self.selected_meals[4].get()}\n\n"
                    f"Total Nutritional Information:\n"
                    f" Calories: {total_calories} kcal\n"
                    f" Protein: {total_protein} g\n"
                    f" Fats: {total_fats} g\n"
                    f" Carbs: {total_carbs} g\n"
                )
                os.startfile("nutrition_report.txt")

        except Exception as e:
            print("Calculation error:", e)
            self.results.config(text=f"Calculation error: {e}\nPlease try again.")
            return None

        # ---CHARTS AND GRAPHS START HERE---
        try:
            if total_macros == 0:
                self.results.config(text="Total macros are zero. Cannot generate charts.")
                return None

            # Set up custom layout: 2 rows, 2 columns (top row: pies, bottom: bar spans both)
            fig = plt.figure(figsize=(7.5, 7.5), facecolor=CHART_BG)
            gs = gridspec.GridSpec(2, 2, height_ratios=[1, 1.2])

            # Pie charts (top row)
            ax_pie1 = fig.add_subplot(gs[0, 0])
            ax_pie2 = fig.add_subplot(gs[0, 1])
            # Bar graph (bottom row, spans both columns)
            ax_bar = fig.add_subplot(gs[1, :])

            # Match the dark dashboard surface and keep chart labels readable.
            for ax in [ax_pie1, ax_pie2, ax_bar]:
                ax.set_facecolor(CHART_BG)
                ax.tick_params(colors=CHART_TEXT)
                ax.title.set_color(CHART_TEXT)
                ax.xaxis.label.set_color(CHART_TEXT)
                ax.yaxis.label.set_color(CHART_TEXT)
                for spine in ax.spines.values():
                    spine.set_color('#55586b')

            # FIRST CHART (CALORIES CONSUMED/REMAINING)
            if total_calories <= self.max_calories:
                pie_one_labels = [f'Consumed: {total_calories} kcal',
                                  f'Left: {calories_remaining} kcal']
                pie_one_sizes = [total_calories, calories_remaining]
                pie_one_colours = ['#a8e760', '#bd9cf2']
            else:
                exceeded = total_calories - self.max_calories
                pie_one_labels = [f'Allowed: {self.max_calories} kcal',
                                  f'Exceeded: {exceeded} kcal']
                pie_one_sizes = [self.max_calories, exceeded]
                pie_one_colours = ['#a8e760', '#f18084']
            explode = (0.1, 0)
            ax_pie1.pie(
                pie_one_sizes, labels=pie_one_labels,
                colors=pie_one_colours, explode=explode,
                startangle=90, textprops={'color': '#292a36'},
                wedgeprops={'edgecolor': CHART_BG, 'linewidth': 1}
            )
            ax_pie1.set_title("Calories Consumed vs Calories Left", color=CHART_TEXT)
            ax_pie1.axis('equal')

            # SECOND CHART (TOTAL MACROS)
            pie_two_labels = [
                f'Protein: {total_protein}g ({total_protein / total_macros:.0%})',
                f'Fats: {total_fats}g ({total_fats / total_macros:.0%})',
                f'Carbs: \n{total_carbs}g\n ({total_carbs / total_macros:.0%})'
            ]
            pie_two_sizes = [total_protein, total_fats, total_carbs]
            explode = (0.05, 0.05, 0.05)
            pie_two_colours = ['#70d2e8', '#ff9d67', '#a8e760']
            ax_pie2.pie(
                pie_two_sizes, labels=pie_two_labels,
                colors=pie_two_colours, startangle=90,
                explode=explode, textprops={'color': '#292a36'},
                wedgeprops={'edgecolor': CHART_BG, 'linewidth': 1})
            ax_pie2.set_title("Total Macros", color=CHART_TEXT)
            ax_pie2.axis('equal')

            # THIRD CHART (CONSUMED/RDI COMPARISON)
            width = 0.2
            labels = ['Carbs', 'Fats', 'Protein']
            macronutrients = [total_carbs, total_fats, total_protein]
            rdi_macros = [rdi["carbs"], rdi["fats"], rdi["protein"]]
            x = np.arange(len(labels))
            ax_bar.bar(x - width / 2, macronutrients, width, label='Total Consumed', color='#a8e760')
            ax_bar.bar(x + width / 2, rdi_macros, width, label='Recommended Daily Intake', color='#bd9cf2')
            ax_bar.set_ylabel('Macros', color=CHART_TEXT)
            ax_bar.set_title('Macro Comparison', color=CHART_TEXT)
            ax_bar.set_xticks(x)
            ax_bar.set_xticklabels(labels)
            ax_bar.legend(['Total Consumed', 'Recommended Daily Intake'],
                          facecolor='#303343', edgecolor='#55586b',
                          labelcolor=CHART_TEXT)

            fig.tight_layout(rect=[0, 0, 1, 1])  # leave no extra margin

            # Remove any old charts
            if self.charts is not None:
                self.charts.get_tk_widget().destroy()
                self.charts = None
            self.charts = fig
            self.charts = FigureCanvasTkAgg(fig, master=self.frame)
            self.charts.draw()

            # Embed in Tkinter
            canvas_widget = self.charts.get_tk_widget()
            canvas_widget.config(bg=CHART_BG, highlightthickness=0)
            canvas_widget.grid(row=0, column=0, sticky="nsew")
            return self.charts

        except Exception as e:
            print("Graphing error:", e)
            self.results.config(text=f"Graphing error: {e}\nPlease try again.")
            return None