import tkinter as tk
from tkinter import ttk
import re

###############################################################################
# KONFIGURACJA GLOBALNA I STAŁE
###############################################################################

version = "v.1.4.2"
name = "Data Diff Tool"
font_size_main = 11
font_style_main = "Consolas"
font_size_button = 9 
font_style_button = "Consolas"
width = 1280
height = 640

# Słownik mapujący czytelne etykiety separatorów na ich faktyczne znaki
SEPARATOR_MAP = {
    "---  |  ---": "|",
    "---  ;  ---": ";",
    "---  ,  ---": ",",
    "--- SOH ---": chr(1),
    "--- # ---": "#",
    "--- $ ---": "$"
}

###############################################################################
# KLASY POMOCNICZE (TOOLTIP / HOVER)
###############################################################################

class ToolTip:
    """
    Klasa odpowiedzialna za wyświetlanie dymku z podpowiedzią (tooltip)
    po najechaniu kursorem myszy na wskazany widget.
    """
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0
        
        # Przypisanie zdarzeń wejścia (<Enter>) i wyjścia (<Leave>) kursora myszy
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        """Tworzy i wyświetla małe okienko z tekstem podpowiedzi."""
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert") or (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        # Tworzenie okna typu Toplevel bez dekoracji systemowych (ramki, paska tytułu)
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(
            tw, 
            text=self.text, 
            justify=tk.LEFT,
            background="#ffffe0", # Klasyczny żółty kolor podpowiedzi
            foreground="black", 
            relief=tk.SOLID, 
            borderwidth=1,
            font=(font_style_main, 9)
        )
        label.pack(ipadx=3, ipady=1)

    def hide_tip(self, event=None):
        """Usuwa (niszczy) okienko z podpowiedzią, gdy kursor opuszcza widget."""
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


###############################################################################
# GŁÓWNA LOGIKA APLIKACJI (PORÓwnywanie i Filtrowanie)
###############################################################################

def compare_data(*args):
    """
    Główna funkcja parsująca, porównująca oraz filtrująca dane z pól wejściowych.
    Uruchamiana automatycznie przy każdej zmianie tekstu, wyboru separatora lub checkboxa.
    """
    selected_name = separator_var.get()
    sep = SEPARATOR_MAP.get(selected_name, "|")
    search_query = entry_search.get().lower().strip()
    is_kv_mode = key_value_mode_var.get()
    kv_sep = kv_separator_var.get()

    val1 = entry_top.get().strip()
    val2 = entry_bottom.get().strip()
     
    # Czyszczenie tabeli wyników przed ponownym przeliczeniem
    for item in tree.get_children():
        tree.delete(item)
     
    if not val1 and not val2:
        return

    # -------------------------------------------------------------------------
    # TRYB 1: KLUCZ = WARTOŚĆ (lub KLUCZ : WARTOŚĆ)
    # Paruje elementy po ich kluczach, niezależnie od kolejności w ciągu znaków.
    # -------------------------------------------------------------------------
    if is_kv_mode:
        def parse_to_dict(text, active_sep, kv_delimiter):
            """Pomocnicza funkcja parsująca tekst wejściowy na słownik {klucz: wartość}."""
            d = {}
            escaped_sep = re.escape(active_sep)
            # Dzielimy ciąg po głównym separatorze kolumn oraz dodatkowo po średnikach, przecinkach, tabach i nowych liniach
            pattern = f'{escaped_sep}|[,;\n\t]+'
            pairs = re.split(pattern, text)
            for p in pairs:
                p = p.strip()
                if kv_delimiter in p:
                    k, v = p.split(kv_delimiter, 1)
                    d[k.strip()] = v.strip()
            return d

        dict1 = parse_to_dict(val1, sep, kv_sep)
        dict2 = parse_to_dict(val2, sep, kv_sep)
        
        # Pobieramy posortowaną listę wszystkich unikalnych kluczy z obu słowników
        all_keys = sorted(list(set(dict1.keys()).union(set(dict2.keys()))))
        found_diff = False
        visible_rows = 0

        for i, key in enumerate(all_keys):
            p1_raw = dict1.get(key, "<brak>")
            p2_raw = dict2.get(key, "<brak>")
            
            # Czyszczenie znaków nowej linii w obrębie samej wartości
            p1 = p1_raw.replace("\n", " ").replace("\r", " ").strip() if p1_raw != "<brak>" else p1_raw
            p2 = p2_raw.replace("\n", " ").replace("\r", " ").strip() if p2_raw != "<brak>" else p2_raw

            display_p1 = f"{key}{kv_sep}{p1}" if p1 != "<brak>" else p1
            display_p2 = f"{key}{kv_sep}{p2}" if p2 != "<brak>" else p2

            # Filtrowanie wyników na podstawie wpisanej frazy w wyszukiwarce
            if search_query and search_query not in key.lower() and search_query not in display_p1.lower() and search_query not in display_p2.lower():
                continue

            field_no = key # W tym trybie klucz służy jako identyfikator w kolumnie "Nr pola"
            visible_rows += 1
            row_tag = 'evenrow' if visible_rows % 2 == 0 else 'oddrow'
             
            # Sprawdzenie, czy wartości pod tym samym kluczem się różnią
            if p1 != p2:
                found_diff = True
                tree.insert('', tk.END, values=(field_no, display_p1, display_p2, "TAK"), tags=(row_tag, 'diff'))
            else:
                tree.insert('', tk.END, values=(field_no, display_p1, display_p2, "NIE"), tags=(row_tag,))
        return

    # -------------------------------------------------------------------------
    # TRYB 2: STANDARDOWY (POZYCJONOWANY PO INDEKSACH)
    # Porównuje elementy element po elemencie według ich pozycji rozdzielonej separatorem.
    # -------------------------------------------------------------------------
    parts1 = val1.split(sep) if val1 else []
    parts2 = val2.split(sep) if val2 else []
     
    max_len = max(len(parts1), len(parts2))
    found_diff = False
    visible_rows = 0
     
    for i in range(max_len):
        p1_raw = parts1[i] if i < len(parts1) else "<brak>"
        p2_raw = parts2[i] if i < len(parts2) else "<brak>"
         
        if sep != "\n":
            p1 = p1_raw.replace("\n", " ").replace("\r", " ").strip() if p1_raw != "<brak>" else p1_raw
            p2 = p2_raw.replace("\n", " ").replace("\r", " ").strip() if p2_raw != "<brak>" else p2_raw
        else:
            p1 = p1_raw.strip()
            p2 = p2_raw.strip()

        # Filtrowanie wyników
        if search_query and search_query not in p1.lower() and search_query not in p2.lower():
            continue

        field_no = i + 1
        visible_rows += 1
        row_tag = 'evenrow' if visible_rows % 2 == 0 else 'oddrow'
         
        # Porównanie pozycji
        if p1 != p2:
            found_diff = True
            tree.insert('', tk.END, values=(field_no, p1, p2, "TAK"), tags=(row_tag, 'diff'))
        else:
            tree.insert('', tk.END, values=(field_no, p1, p2, "NIE"), tags=(row_tag,))


################.EXE / GUI - FUNKCJE POMOCNICZE ################################

def clear_all():
    """Czyści pola tekstowe wejściowe oraz wyszukiwarkę."""
    entry_top.delete(0, tk.END)
    entry_bottom.delete(0, tk.END)
    entry_search.delete(0, tk.END)
    compare_data()
     
def clear_first():
    """Czyści tylko pierwsze pole wejściowe (DANE 1)."""
    entry_top.delete(0, tk.END)
    compare_data()
     
def clear_second():
    """Czyści tylko drugie pole wejściowe (DANE 2)."""
    entry_bottom.delete(0, tk.END)
    compare_data()
     
def center_window(window, width, height):
    """Centruje główne okno aplikacji na środku ekranu użytkownika."""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')

def copy_row(event):
    """Tworzy i wyświetla menu kontekstowe (pod prawym przyciskiem myszy) do kopiowania zawartości wiersza."""
    item_id = tree.identify_row(event.y)
    if not item_id:
        return    
    tree.selection_set(item_id)
    values = tree.item(item_id, 'values')
     
    if values:
        menu_font = (font_style_main, font_size_main)
        menu = tk.Menu(root, tearoff=0, font=menu_font)
         
        menu.add_command(label=f"Kopiuj wartość 1: {values[1][:20]}...", 
                         command=lambda: root.clipboard_append(values[1]))
        menu.add_command(label=f"Kopiuj wartość 2: {values[2][:20]}...", 
                         command=lambda: root.clipboard_append(values[2]))
        menu.add_separator()
        menu.add_command(label="Kopiuj obie wartości", 
                         command=lambda: root.clipboard_append(f"{values[1]} ; {values[2]}"))
         
        menu.post(event.x_root, event.y_root)
        root.clipboard_clear()

def toggle_kv_state():
    """Włącza lub wyłącza combobox wyboru separatora klucz-wartość zależnie od stanu checkboxa."""
    if key_value_mode_var.get():
        kv_separator_choice.config(state="readonly")
        tree.heading('nr', text='Klucz')
    else:
        kv_separator_choice.config(state="disabled")
        tree.heading('nr', text='Nr pola')
    compare_data()

def treeview_sort_column(tv, col, reverse):
    """Obsługuje sortowanie danych w tabeli po kliknięciu w nagłówek kolumny."""
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


###############################################################################
# BUDOWA INTERFEMCU GRAFICZNEGO (GUI)
###############################################################################

root = tk.Tk()
root.title(name + " " + version)
center_window(root, width, height)

# Główna ramka na górny panel ustawień
frame_settings = tk.Frame(root, padx=20, pady=12, bg="#ececec")
frame_settings.pack(side=tk.TOP, fill="x")

# --- PIERWSZY WIERSZ USTAWIEŃ ---
frame_settings_row1 = tk.Frame(frame_settings, bg="#ececec")
frame_settings_row1.pack(side=tk.TOP, fill="x")

# Wybór separatora kolumn
tk.Label(frame_settings_row1, text="SEPARATOR:", font=(font_style_main, font_size_main), bg="#ececec").pack(side=tk.LEFT)
separator_var = tk.StringVar(value="---  |  ---")
separator_choice = ttk.Combobox(frame_settings_row1, textvariable=separator_var, values=list(SEPARATOR_MAP.keys()), width=14, state="readonly", justify="center")
separator_choice.pack(side=tk.LEFT, padx=(5, 20))
separator_choice.bind("<<ComboboxSelected>>", compare_data)
ToolTip(separator_choice, "Wybierz separator pól danych.")

# Pole wyszukiwania / filtrowania wyników w czasie rzeczywistym
tk.Label(frame_settings_row1, text="SZUKAJ:", font=(font_style_main, font_size_main), bg="#ececec").pack(side=tk.LEFT)
entry_search = tk.Entry(frame_settings_row1, font=(font_style_main, font_size_main), width=25)
entry_search.pack(side=tk.LEFT, padx=5)
entry_search.bind("<KeyRelease>", compare_data)
ToolTip(entry_search, "Szukaj tekstu w polach danych.")

# Przycisk czyszczący całe okno (po prawej stronie)
tk.Button(frame_settings_row1, text="WYCZYŚĆ WSZYSTKO", command=clear_all, bg="#B22222", fg="white", font=(font_style_button, font_size_button), padx=1).pack(side=tk.RIGHT)


# --- DRUGI WIERSZ USTAWIEŃ (POD SPODEM) ---
frame_settings_row2 = tk.Frame(frame_settings, bg="#ececec")
frame_settings_row2.pack(side=tk.TOP, fill="x", pady=(8, 0))

# Checkbox aktywujący tryb dopasowywania po kluczach
key_value_mode_var = tk.BooleanVar(value=False)
checkbox_kv = tk.Checkbutton(
    frame_settings_row2, 
    text="Tryb klucz", 
    variable=key_value_mode_var, 
    command=toggle_kv_state, 
    bg="#ececec", 
    font=(font_style_main, font_size_main)
)
checkbox_kv.pack(side=tk.LEFT)

# Wybór separatora w parze klucz-wartość ("=" lub ":")
kv_separator_var = tk.StringVar(value="=")
kv_separator_choice = ttk.Combobox(
    frame_settings_row2, 
    textvariable=kv_separator_var, 
    values=["=", ":"], 
    width=2, 
    state="disabled", # Startowo zablokowane, dopóki checkbox nie jest zaznaczony
    justify="center"
)
kv_separator_choice.pack(side=tk.LEFT, padx=2)
kv_separator_choice.bind("<<ComboboxSelected>>", compare_data)

lbl_kv_end = tk.Label(frame_settings_row2, text="wartość", font=(font_style_main, font_size_main), bg="#ececec")
lbl_kv_end.pack(side=tk.LEFT, padx=(0, 15))

# Przypisanie podpowiedzi (tooltipów) do elementów sterujących trybem klucz-wartość
ToolTip(checkbox_kv, "Paruj dane po kluczach niezależnie od ich kolejności w liniach.")
ToolTip(kv_separator_choice, "Wybierz znak rozdzielający klucz od wartości.")


# --- STOPKA APLIKACJI ---
footer_frame = tk.Frame(root, bg="#f0f0f0", bd=1, relief="ridge")
footer_frame.pack(side=tk.BOTTOM, fill="x")
tk.Label(footer_frame, text=name+" "+version+" | Krzysztof Kosowski", font=('Consolas', 8), bg="#f0f0f0", fg="#888").pack(side=tk.RIGHT, padx=10)


# --- POLA WPROWADZANIA DANYCH (DANE 1 / DANE 2) ---
frame_input = tk.Frame(root, padx=20, pady=10)
frame_input.pack(side=tk.TOP, fill="x")

frame_row1 = tk.Frame(frame_input)
frame_row1.pack(fill="x")

frame_row2 = tk.Frame(frame_input)
frame_row2.pack(fill="x")

# Pole tekstowe dla DANE 1
tk.Label(frame_row1, text="DANE 1:", font=(font_style_main, font_size_main)).pack(anchor="w")
entry_top = tk.Entry(frame_row1, font=(font_style_main, font_size_main), fg="#e74c3c")
entry_top.pack(side=tk.LEFT, fill="x", expand=True, padx=(0, 10))
entry_top.bind("<KeyRelease>", compare_data)
tk.Button(frame_row1, text="WYCZYŚĆ 1", command=clear_first, font=(font_style_button, font_size_button), padx=10).pack(side=tk.RIGHT)

# Pole tekstowe dla DANE 2
tk.Label(frame_row2, text="DANE 2:", font=(font_style_main, font_size_main)).pack(anchor="w")
entry_bottom = tk.Entry(frame_row2, font=(font_style_main, font_size_main), fg="#3498db")
entry_bottom.pack(side=tk.LEFT, fill="x", expand=True, padx=(0, 10))
entry_bottom.bind("<KeyRelease>", compare_data)
tk.Button(frame_row2, text="WYCZYŚĆ 2", command=clear_second, font=(font_style_button, font_size_button), padx=10).pack(side=tk.RIGHT)


# --- SEKCJA WYNIKÓW (TABELA TREEVIEW) ---
tk.Label(root, text="WYNIKI PORÓWNANIA I FILTROWANIA", font=(font_style_main, font_size_main), fg="#333").pack(pady=(10, 0))

frame_tree = tk.Frame(root, padx=20, pady=10)
frame_tree.pack(expand=True, fill="both")

columns = ('nr', 'val1', 'val2', 'diff_status')
style = ttk.Style()
style.configure("Treeview", background="#ffffff", foreground="black", rowheight=25, fieldbackground="#ffffff", font=(font_style_main, font_size_main, 'bold'))
style.configure("Treeview.Heading", font=(font_style_main, font_size_main))
style.map("Treeview", background=[('selected', '#347083')])

# Inicjalizacja komponentu tabeli
tree = ttk.Treeview(frame_tree, columns=columns, show='headings', selectmode='browse')

# Konfiguracja nagłówków kolumn wraz z funkcją sortującą
tree.heading('nr', text='Nr pola', command=lambda: treeview_sort_column(tree, 'nr', False))
tree.heading('val1', text='DANE 1', command=lambda: treeview_sort_column(tree, 'val1', False))
tree.heading('val2', text='DANE 2', command=lambda: treeview_sort_column(tree, 'val2', False))
tree.heading('diff_status', text='RÓŻNICA', command=lambda: treeview_sort_column(tree, 'diff_status', False))

# Szerokości i wyrównanie kolumn
tree.column('nr', width=130, anchor='center')
tree.column('val1', width=370, anchor='w')
tree.column('val2', width=370, anchor='w')
tree.column('diff_status', width=80, anchor='center')

# Paski przewijania (scrollbary) dla tabeli
tree_scrolly = ttk.Scrollbar(frame_tree, orient="vertical", command=tree.yview)
tree_scrollx = ttk.Scrollbar(frame_tree, orient="horizontal", command=tree.xview)
tree.configure(yscrollcommand=tree_scrolly.set, xscrollcommand=tree_scrollx.set)

tree_scrolly.pack(side=tk.RIGHT, fill="y")
tree_scrollx.pack(side=tk.BOTTOM, fill="x")

# Podpięcie menu kontekstowego pod prawy przycisk myszy (obsługa Windows/Linux oraz macOS)
tree.bind("<Button-3>", copy_row)
tree.bind("<Button-2>", copy_row)

tree.pack(expand=True, fill="both")

# Stylizowanie wierszy w tabeli (naprzemienne kolory tła oraz podświetlenie różnic)
tree.tag_configure('oddrow', background='white', font=(font_style_main, font_size_main))
tree.tag_configure('evenrow', background='#f9f9f9', font=(font_style_main, font_size_main))
tree.tag_configure('diff', background='#ffcdd2', foreground='#b71c1c', font=(font_style_main, font_size_main, 'bold'))
tree.tag_configure('equal', foreground='gray', font=(font_style_main, font_size_main))

# Uruchomienie głównej pętli zdarzeń okna graficznego
root.mainloop()