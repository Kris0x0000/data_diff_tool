import tkinter as tk
from tkinter import ttk

################
# config start #
################

version = "v.1.4.1"
name = "Data Diff Tool"
font_size_main = 11
font_style_main = "Consolas"
font_size_button = 9 
font_style_button = "Consolas"
width=1200
height=600

SEPARATOR_MAP = {
    "---  |  ---": "|",
    "---  ;  ---": ";",
    "---  ,  ---": ",",
    "--- SOH ---": chr(1),
    "--- # ---": "#",
    "--- $ ---": "$"
}

##############
# config end #
##############

def compare_data(*args):
    selected_name = separator_var.get()
    sep = SEPARATOR_MAP.get(selected_name, "|")
    search_query = entry_search.get().lower().strip() # Pobranie frazy wyszukiwania

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
    visible_rows = 0
    
    for i in range(max_len):
        # Pobieramy surową wartość (jeśli istnieje)
        p1_raw = parts1[i] if i < len(parts1) else "<brak>"
        p2_raw = parts2[i] if i < len(parts2) else "<brak>"
        
        # Jeśli to nie jest brak danych, zamieniamy nową linię na spację i czyścimy nadmiarowe spacje
        # Robimy to TYLKO jeśli separatorem nie jest \n
        if sep != "\n":
            if p1_raw != "<brak>":
                p1 = p1_raw.replace("\n", " ").replace("\r", " ").strip()
            else: p1 = p1_raw
            
            if p2_raw != "<brak>":
                p2 = p2_raw.replace("\n", " ").replace("\r", " ").strip()
            else: p2 = p2_raw
        else:
            p1 = p1_raw.strip()
            p2 = p2_raw.strip()

        # Logika wyszukiwania (filtrowanie)
        if search_query and search_query not in p1.lower() and search_query not in p2.lower():
            continue

        field_no = i + 1
        visible_rows += 1
        row_tag = 'evenrow' if visible_rows % 2 == 0 else 'oddrow'
        
        # Porównanie i wstawienie do tabeli
        if p1 != p2:
            found_diff = True
            tree.insert('', tk.END, values=(field_no, p1, p2, "TAK"), tags=(row_tag, 'diff'))
        else:
            tree.insert('', tk.END, values=(field_no, p1, p2, "NIE"), tags=(row_tag,))

    # Jeśli brak różnic w przefiltrowanym widoku
    if not found_diff and visible_rows > 0 and (val1 or val2) and not search_query:
         # Dodajemy info o braku różnic tylko jeśli nie filtrujemy (żeby nie śmiecić przy wyszukiwaniu)
         pass

def clear_all():
    entry_top.delete(0, tk.END)
    entry_bottom.delete(0, tk.END)
    entry_search.delete(0, tk.END) # Czyścimy też wyszukiwarkę
    compare_data()
    
def clear_first():
    entry_top.delete(0, tk.END)
    compare_data()
    
def clear_second():
    entry_bottom.delete(0, tk.END)
    compare_data()
    
def center_window(window, width, height):
    # Pobieramy wymiary ekranu
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Obliczamy współrzędne X i Y dla środka
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    # Ustawiamy geometrię okna
    window.geometry(f'{width}x{height}+{x}+{y}')

    
def copy_row(event):
    # Pobierz ID zaznaczonego wiersza
    item_id = tree.identify_row(event.y)
    if not item_id:
        return    
    tree.selection_set(item_id) # Upewnij się, że wiersz jest zaznaczony
    values = tree.item(item_id, 'values')
    
    if values:
        # Tworzymy proste menu kontekstowe
        menu_font = (font_style_main, font_size_main)
        menu = tk.Menu(root, tearoff=0, font=menu_font)
        
        menu.add_command(label=f"Kopiuj wartość 1: {values[1][:20]}...", 
                         command=lambda: root.clipboard_append(values[1]))
        menu.add_command(label=f"Kopiuj wartość 2: {values[2][:20]}...", 
                         command=lambda: root.clipboard_append(values[2]))
        menu.add_separator()
        menu.add_command(label="Kopiuj obie wartości", 
                         command=lambda: root.clipboard_append(f"{values[1]} ; {values[2]}"))
        
        # Wyświetl menu w miejscu kliknięcia
        menu.post(event.x_root, event.y_root)
        
        # Czyścimy schowek przed nowym kopiowaniem (opcjonalnie, ale zalecane)
        root.clipboard_clear()
        

def treeview_sort_column(tv, col, reverse):
    l = [(tv.set(k, col), k) for k in tv.get_children('')]
    try:
        l.sort(key=lambda t: int(t[0]), reverse=reverse)
    except ValueError:
        l.sort(reverse=reverse)

    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)
        row_tag = 'evenrow' if index % 2 == 0 else 'oddrow'
        current_tags = list(tv.item(k, 'tags'))
        if 'evenrow' in current_tags: current_tags.remove('evenrow')
        if 'oddrow' in current_tags: current_tags.remove('oddrow')
        current_tags.append(row_tag)
        tv.item(k, tags=tuple(current_tags))

    tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse))

# --- KONFIGURACJA GUI ---


root = tk.Tk()
root.title(name + " " + version)
center_window(root, width, height)

# Górny pasek ustawień
frame_settings = tk.Frame(root, padx=20, pady=15, bg="#ececec")
frame_settings.pack(side=tk.TOP, fill="x")

# Separator
tk.Label(frame_settings, text="SEPARATOR:", font=(font_style_main, font_size_main), bg="#ececec").pack(side=tk.LEFT)
separator_var = tk.StringVar(value="---  |  ---")
separator_choice = ttk.Combobox(frame_settings, textvariable=separator_var, values=list(SEPARATOR_MAP.keys()), width=15, state="readonly", justify="center")
separator_choice.pack(side=tk.LEFT, padx=(5, 20))
separator_choice.bind("<<ComboboxSelected>>", compare_data)

# WYSZUKIWARKA (Nowość)
tk.Label(frame_settings, text="SZUKAJ WARTOŚCI:", font=(font_style_main, font_size_main), bg="#ececec").pack(side=tk.LEFT)
entry_search = tk.Entry(frame_settings, font=(font_style_main, font_size_main), width=30)
entry_search.pack(side=tk.LEFT, padx=5)
entry_search.bind("<KeyRelease>", compare_data) # Reaguje na pisanie

tk.Button(frame_settings, text="WYCZYŚĆ WSZYSTKO", command=clear_all, bg="#B22222", fg="white", font=(font_style_button, font_size_button), padx=1).pack(side=tk.RIGHT)

# Stopka
footer_frame = tk.Frame(root, bg="#f0f0f0", bd=1, relief="ridge")
footer_frame.pack(side=tk.BOTTOM, fill="x")
tk.Label(footer_frame, text=name+" "+version+" | Krzysztof Kosowski", font=('Consolas', 8), bg="#f0f0f0", fg="#888").pack(side=tk.RIGHT, padx=10)

# Pola wejściowe
frame_input = tk.Frame(root, padx=20, pady=10)
frame_input.pack(side=tk.TOP, fill="x")

frame_row1 = tk.Frame(frame_input) # Ramka pomocnicza dla 1. rzędu
frame_row1.pack(fill="x")

frame_row2 = tk.Frame(frame_input) # Ramka pomocnicza dla 2. rzędu
frame_row2.pack(fill="x")

tk.Label(frame_row1, text="DANE 1:", font=(font_style_main, font_size_main)).pack(anchor="w")
entry_top = tk.Entry(frame_row1, font=(font_style_main, font_size_main), fg="#e74c3c")
entry_top.pack(side=tk.LEFT, fill="x", expand=True, padx=(0, 10))
entry_top.bind("<KeyRelease>", compare_data)

tk.Button(frame_row1, text="WYCZYŚĆ 1", command=clear_first, font=(font_style_button, font_size_button), padx=10).pack(side=tk.RIGHT)

tk.Label(frame_row2, text="DANE 2:", font=(font_style_main, font_size_main)).pack(anchor="w")
entry_bottom = tk.Entry(frame_row2, font=(font_style_main, font_size_main), fg="#3498db")
entry_bottom.pack(side=tk.LEFT, fill="x", expand=True, padx=(0, 10))
entry_bottom.bind("<KeyRelease>", compare_data)

tk.Button(frame_row2, text="WYCZYŚĆ 2", command=clear_second, font=(font_style_button, font_size_button), padx=10).pack(side=tk.RIGHT)

# --- SEKCJA TREEVIEW (TABELA) ---
tk.Label(root, text="WYNIKI PORÓWNANIA I FILTROWANIA", font=(font_style_main, font_size_main), fg="#333").pack(pady=(10, 0))

frame_tree = tk.Frame(root, padx=20, pady=10)
frame_tree.pack(expand=True, fill="both")

columns = ('nr', 'val1', 'val2', 'diff_status')
style = ttk.Style()
style.configure("Treeview", background="#ffffff", foreground="black", rowheight=25, fieldbackground="#ffffff", font=(font_style_main, font_size_main, 'bold'))

# Konfiguracja czcionki dla nagłówków
style.configure("Treeview.Heading", font=(font_style_main, font_size_main))
style.map("Treeview", background=[('selected', '#347083')])

tree = ttk.Treeview(frame_tree, columns=columns, show='headings', selectmode='browse')

tree.heading('nr', text='Nr pola', command=lambda: treeview_sort_column(tree, 'nr', False))
tree.heading('val1', text='DANE 1', command=lambda: treeview_sort_column(tree, 'val1', False))
tree.heading('val2', text='DANE 2', command=lambda: treeview_sort_column(tree, 'val2', False))
tree.heading('diff_status', text='RÓŻNICA', command=lambda: treeview_sort_column(tree, 'diff_status', False))

tree.column('nr', width=80, anchor='center')
tree.column('val1', width=400, anchor='w')
tree.column('val2', width=400, anchor='w')
tree.column('diff_status', width=80, anchor='center')

tree_scrolly = ttk.Scrollbar(frame_tree, orient="vertical", command=tree.yview)
tree_scrollx = ttk.Scrollbar(frame_tree, orient="horizontal", command=tree.xview)
tree.configure(yscrollcommand=tree_scrolly.set, xscrollcommand=tree_scrollx.set)

tree_scrolly.pack(side=tk.RIGHT, fill="y")
tree_scrollx.pack(side=tk.BOTTOM, fill="x")

# Bind dla Windows/Linux (prawy przycisk myszy to Button-3)
tree.bind("<Button-3>", copy_row)
# Bind dla MacOS (często Button-2)
tree.bind("<Button-2>", copy_row)

tree.pack(expand=True, fill="both")

tree.tag_configure('oddrow', background='white', font=(font_style_main, font_size_main))
tree.tag_configure('evenrow', background='#f9f9f9', font=(font_style_main, font_size_main))
tree.tag_configure('diff', background='#ffcdd2', foreground='#b71c1c', font=(font_style_main, font_size_main, 'bold'))
tree.tag_configure('equal', foreground='gray', font=(font_style_main, font_size_main))

root.mainloop()