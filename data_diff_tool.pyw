import tkinter as tk
from tkinter import ttk

def compare_data(*args):
    selected_name = separator_var.get()
    sep = SEPARATOR_MAP.get(selected_name, "|")

    val1 = entry_top.get().strip()
    val2 = entry_bottom.get().strip()
    
    # Czyszczenie tabeli przed nowym porównaniem
    for item in tree.get_children():
        tree.delete(item)
    
    if not val1 and not val2:
        return

    parts1 = val1.split(sep) if val1 else []
    parts2 = val2.split(sep) if val2 else []
    
    max_len = max(len(parts1), len(parts2))
    found_diff = False
    
    for i in range(max_len):
        p1 = parts1[i].strip() if i < len(parts1) else "<brak>"
        p2 = parts2[i].strip() if i < len(parts2) else "<brak>"
        
        field_no = i + 1
        
        # Określamy bazowy kolor (zebra)
        row_tag = 'evenrow' if i % 2 == 0 else 'oddrow'
        
        if p1 != p2:
            found_diff = True
            # Wstawiamy wiersz z tagiem 'diff' dla wyróżnienia kolorem
            #tree.insert('', tk.END, values=(field_no, p1, p2), tags=('diff',))
            tree.insert('', tk.END, values=(field_no, p1, p2), tags=(row_tag, 'diff'))
        else:
            # Wstawiamy wiersz bez specjalnego wyróżnienia
            #tree.insert('', tk.END, values=(field_no, p1, p2))
            tree.insert('', tk.END, values=(field_no, p1, p2), tags=(row_tag,))

    # Jeśli brak różnic, możemy dodać informację w pierwszym wierszu lub zmienić tytuł
    if not found_diff and (val1 or val2):
        tree.insert('', tk.END, values=("", "Brak różnic", "Brak różnic"), tags=('equal',))

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
root.title("Data Diff Tool v.1.2.2")
root.geometry("900x600")

# Górny pasek ustawień
frame_settings = tk.Frame(root, padx=20, pady=15, bg="#ececec")
frame_settings.pack(side=tk.TOP, fill="x")

tk.Label(frame_settings, text="SEPARATOR:", font=('Arial', 9, 'bold'), bg="#ececec").pack(side=tk.LEFT)

separator_var = tk.StringVar(value="---  |  ---")
separator_choice = ttk.Combobox(frame_settings, textvariable=separator_var, values=list(SEPARATOR_MAP.keys()), width=20, state="readonly", justify="center")
separator_choice.pack(side=tk.LEFT, padx=10)
separator_choice.bind("<<ComboboxSelected>>", compare_data)

tk.Button(frame_settings, text="WYCZYŚĆ", command=clear_all, bg="#d32f2f", fg="white", font=('Arial', 9, 'bold')).pack(side=tk.RIGHT)

# Stopka
footer_frame = tk.Frame(root, bg="#f0f0f0", bd=1, relief="ridge")
footer_frame.pack(side=tk.BOTTOM, fill="x")
tk.Label(footer_frame, text="Wersja 1.2.2 | Krzysztof Kosowski", font=('Arial', 8), bg="#f0f0f0", fg="#888").pack(side=tk.RIGHT, padx=10)

# Pola wejściowe
frame_input = tk.Frame(root, padx=20, pady=10)
frame_input.pack(side=tk.TOP, fill="x")

tk.Label(frame_input, text="PIERWSZY CIĄG DANYCH:", font=('Arial', 8, 'bold')).pack(anchor="w")
entry_top = tk.Entry(frame_input, font=('Consolas', 11), fg="#e74c3c")
entry_top.pack(fill="x", pady=5)
entry_top.bind("<KeyRelease>", compare_data)

tk.Label(frame_input, text="DRUGI CIĄG DANYCH:", font=('Arial', 8, 'bold')).pack(anchor="w")
entry_bottom = tk.Entry(frame_input, font=('Consolas', 11), fg="#3498db")
entry_bottom.pack(fill="x", pady=5)
entry_bottom.bind("<KeyRelease>", compare_data)

# --- SEKCJA TREEVIEW (TABELA) ---
tk.Label(root, text="PORÓWNANIE PÓL", font=('Arial', 10, 'bold'), bg="#f5f5f5", fg="#333").pack(pady=(10, 0))

frame_tree = tk.Frame(root, padx=20, pady=10)
frame_tree.pack(expand=True, fill="both")

# Definicja kolumn
columns = ('nr', 'val1', 'val2')


# 1. Tworzymy obiekt stylu
style = ttk.Style()

# 2. Wybieramy motyw, który lepiej obsługuje modyfikacje (np. 'clam')
#style.theme_use("clam")


# 3. Konfigurujemy wygląd Treeview
style.configure("Treeview",
                background="#ffffff",
                foreground="black",
                rowheight=25,
                fieldbackground="#ffffff",
)

# 4. Dodajemy mapowanie dla koloru obramowania (tworzy efekt linii)
style.map("Treeview", 
          background=[('selected', '#347083')])

tree = ttk.Treeview(frame_tree, columns=columns, show='headings', selectmode='browse')

# Definicja nagłówków
tree.heading('nr', text='Nr pola')
tree.heading('val1', text='PIERWSZY CIĄG DANYCH')
tree.heading('val2', text='DRUGI CIĄG DANYCH')

# Szerokość kolumn
tree.column('nr', width=80, anchor='center')
tree.column('val1', width=380, anchor='w')
tree.column('val2', width=380, anchor='w')

# Scrollbar dla Treeview
tree_scrolly = ttk.Scrollbar(frame_tree, orient="vertical", command=tree.yview)
tree_scrollx = ttk.Scrollbar(frame_tree, orient="horizontal", command=tree.xview)
tree.configure(yscrollcommand=tree_scrolly.set, xscrollcommand=tree_scrollx.set)

tree_scrolly.pack(side=tk.RIGHT, fill="y")
tree_scrollx.pack(side=tk.BOTTOM, fill="x")
tree.pack(expand=True, fill="both")

# --- KONFIGURACJA KOLORÓW DLA WIERSZY ---
tree.tag_configure('oddrow', background='white',font=('Arial', 11))
tree.tag_configure('evenrow', background='#f2f2f2',font=('Arial', 11)) # Delikatny szary

# Tag 'diff' konfigurujemy NA KOŃCU lub z wyraźnym tłem
# Używamy nieco mocniejszego koloru tekstu, by był czytelny na jasnoczerwonym tle
tree.tag_configure('diff', background='#ffcdd2', foreground='#b71c1c',font=('Arial', 11)) 

tree.tag_configure('equal', foreground='gray')

root.mainloop()