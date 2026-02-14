import tkinter as tk
from tkinter import ttk

def compare_data(*args):
    selected_name = separator_var.get()
    sep = SEPARATOR_MAP.get(selected_name, "|")

    val1 = entry_top.get().strip()
    val2 = entry_bottom.get().strip()
    
    parts1 = val1.split(sep) if val1 else []
    parts2 = val2.split(sep) if val2 else []
    
    # Odblokowanie pola i wyczyszczenie
    output_combined.config(state='normal')
    output_combined.delete('1.0', tk.END)
    
    max_len = max(len(parts1), len(parts2))
    
    found_diff = False
    for i in range(max_len):
        p1 = parts1[i].strip() if i < len(parts1) else "<brak>"
        p2 = parts2[i].strip() if i < len(parts2) else "<brak>"
        
        if p1 != p2:
            found_diff = True
            # Wstawianie numeru pola
            output_combined.insert(tk.END, f"Pole {i+1}: ", "bold")
            # Wstawianie wartości z 1. pola (Kolor czerwony)
            output_combined.insert(tk.END, f"{p1}", "red_text")
            # Separator wizualny
            output_combined.insert(tk.END, "  <--->  ")
            # Wstawianie wartości z 2. pola (Kolor niebieski)
            output_combined.insert(tk.END, f"{p2}\n", "blue_text")

    if not found_diff and (val1 or val2):
        output_combined.insert(tk.END, "Brak różnic", "gray_text")
        
    output_combined.config(state='disabled')

def clear_all():
    entry_top.delete(0, tk.END)
    entry_bottom.delete(0, tk.END)
    compare_data()

# --- KONFIGURACJA GUI ---

SEPARATOR_MAP = {
    "---  |  ---": "|",
    "---  ;  ---": ";",
    "---  ,  ---": ",",
    "--- SOH ---": chr(1),
    "--- TAB ---": "\t",
    "--- \\n ---": "\n"
}

root = tk.Tk()
root.title("Data Diff Tool v.1.2.1 - Porównywanie komunikatów")
root.geometry("900x600")

# Górny pasek ustawień
frame_settings = tk.Frame(root, padx=20, pady=15, bg="#ececec")

frame_settings.pack(side=tk.TOP, fill="x")
tk.Label(frame_settings, text="SEPARATOR:", font=('Arial', 9, 'bold'), bg="#ececec").pack(side=tk.LEFT)


separator_var = tk.StringVar(value="---  |  ---")
separator_choice = ttk.Combobox(frame_settings, textvariable=separator_var, values=list(SEPARATOR_MAP.keys()), width=20, state="readonly", justify="center")
separator_choice.pack(side=tk.LEFT, padx=10)
separator_choice.bind("<<ComboboxSelected>>", compare_data)

tk.Button(frame_settings, text="WYCZYŚĆ", command=clear_all, bg="#d32f2f", fg="white").pack(side=tk.RIGHT)

# 2. STOPKA (Deklarujemy ją TERAZ, aby zarezerwować dół okna)
footer_frame = tk.Frame(root, bg="#f0f0f0", bd=1, relief="ridge")
footer_frame.pack(side=tk.BOTTOM, fill="x")
tk.Label(footer_frame, text="Wersja 1.2.1 | © 2026 Krzysztof Kosowski", 
         font=('Arial', 8), bg="#f0f0f0", fg="#888").pack(side=tk.RIGHT, padx=10)

# Pola wejściowe
tk.Label(root, text="POLA WEJŚCIOWE", font=('Arial', 10, 'bold'), bg="#f5f5f5", fg="#333").pack(pady=(15, 0))

frame_input = tk.Frame(root, padx=20, pady=10)
frame_input.pack(side=tk.TOP, fill="x")

tk.Label(frame_input, text="PIERWSZY CIĄG DANYCH:", font=('Arial', 8), bg="#f5f5f5", fg="#333").pack(anchor="w")
entry_top = tk.Entry(frame_input, font=('Consolas', 11),foreground="#e74c3c")
entry_top.pack(fill="x", pady=5)
entry_top.bind("<KeyRelease>", compare_data)

tk.Label(frame_input, text="DRUGI CIĄG DANYCH:", font=('Arial', 8), bg="#f5f5f5", fg="#333").pack(anchor="w")
entry_bottom = tk.Entry(frame_input, font=('Consolas', 11),foreground="#3498db")
entry_bottom.pack(fill="x", pady=5)
entry_bottom.bind("<KeyRelease>", compare_data)

# Jedno wspólne pole wyjściowe
tk.Label(root, text="WYKRYTE RÓŻNICE", font=('Arial', 10, 'bold'), bg="#f5f5f5", fg="#333").pack(pady=(15, 0))
frame_output = tk.Frame(root, padx=20, pady=10)

# Tworzymy pasek przewijania wewnątrz ramki wyjściowej
scrollbar = tk.Scrollbar(frame_output)
scrollbar.pack(side=tk.RIGHT, fill="y") # Pasek po prawej, rozciągnięty w pionie
frame_output.pack(expand=True, fill="both")

output_combined = tk.Text(frame_output, font=('Consolas', 11), bg="white", state='disabled', padx=10, pady=10, yscrollcommand=scrollbar.set)
output_combined.pack(expand=True, fill="both")
scrollbar.config(command=output_combined.yview)

# --- KONFIGURACJA TAGÓW KOLORYSTYCZNYCH ---
output_combined.tag_configure("red_text", foreground="#e74c3c", font=('Consolas', 11, 'bold'))
output_combined.tag_configure("blue_text", foreground="#3498db", font=('Consolas', 11, 'bold'))
output_combined.tag_configure("bold", font=('Consolas', 11, 'bold'))
output_combined.tag_configure("gray_text", foreground="gray")


root.mainloop()