import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import urllib.parse

# Token de Graphhopper (puedes reemplazarlo por el tuyo)
API_KEY = "2c1809a8-e160-4a8a-b1c4-7935406733ec"

class GraphhopperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Geolocalización y Rutas - API Ltda.")
        self.root.geometry("750x650")
        self.root.configure(bg="#0b0f19")  # Fondo oscuro estilo DEVNet

        # Estilos de Tkinter
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", background="#0b0f19", foreground="#00f3ff", font=("Consolas", 10))
        style.configure("Header.TLabel", background="#0b0f19", foreground="#ffffff", font=("Consolas", 14, "bold"))

        # --- TÍTULO Y CABECERA ---
        header_frame = tk.Frame(root, bg="#111827", bd=1, relief="solid")
        header_frame.pack(fill="x", padx=15, pady=10)

        lbl_title = tk.Label(
            header_frame, 
            text="🗺️ NAVEGADOR Y GEOLOCALIZACIÓN (GRAPHHOPPER)", 
            font=("Consolas", 13, "bold"), 
            bg="#111827", 
            fg="#00f3ff"
        )
        lbl_title.pack(pady=10)

        # --- FORMULARIO DE ENTRADA ---
        input_frame = tk.Frame(root, bg="#0b0f19")
        input_frame.pack(fill="x", padx=20, pady=5)

        # Origen
        tk.Label(input_frame, text="Ciudad de Origen:", bg="#0b0f19", fg="#a0aec0", font=("Consolas", 10, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        self.ent_origen = tk.Entry(input_frame, bg="#1a202c", fg="#ffffff", insertbackground="white", font=("Consolas", 11), width=25, relief="flat", bd=5)
        self.ent_origen.grid(row=0, column=1, padx=10, pady=5)
        self.ent_origen.insert(0, "Santiago")

        # Destino
        tk.Label(input_frame, text="Ciudad de Destino:", bg="#0b0f19", fg="#a0aec0", font=("Consolas", 10, "bold")).grid(row=1, column=0, sticky="w", pady=5)
        self.ent_destino = tk.Entry(input_frame, bg="#1a202c", fg="#ffffff", insertbackground="white", font=("Consolas", 11), width=25, relief="flat", bd=5)
        self.ent_destino.grid(row=1, column=1, padx=10, pady=5)
        self.ent_destino.insert(0, "Valparaiso")

        # Transporte
        tk.Label(input_frame, text="Medio de Transporte:", bg="#0b0f19", fg="#a0aec0", font=("Consolas", 10, "bold")).grid(row=2, column=0, sticky="w", pady=5)
        self.combo_vehiculo = ttk.Combobox(input_frame, values=["car (Auto)", "bike (Bicicleta)", "foot (A pie)"], state="readonly", width=23)
        self.combo_vehiculo.current(0)
        self.combo_vehiculo.grid(row=2, column=1, padx=10, pady=5)

        # Botón Calcular
        btn_calcular = tk.Button(
            input_frame, 
            text="🚀 CALCULAR RUTA", 
            command=self.calcular_ruta, 
            bg="#00f3ff", 
            fg="#0b0f19", 
            font=("Consolas", 10, "bold"), 
            activebackground="#00b8c4",
            cursor="hand2",
            bd=0,
            padx=15,
            pady=5
        )
        btn_calcular.grid(row=1, column=2, rowspan=2, padx=15)

        # --- TARJETAS DE RESULTADOS (DISTANCIA Y TIEMPO) ---
        res_frame = tk.Frame(root, bg="#0b0f19")
        res_frame.pack(fill="x", padx=20, pady=10)

        # Tarjeta Distancia
        card_dist = tk.Frame(res_frame, bg="#1a202c", bd=1, relief="solid")
        card_dist.pack(side="left", expand=True, fill="both", padx=5)
        tk.Label(card_dist, text="DISTANCIA TOTAL", bg="#1a202c", fg="#a0aec0", font=("Consolas", 9)).pack(pady=(5,0))
        self.lbl_distancia = tk.Label(card_dist, text="0.00 km", bg="#1a202c", fg="#00f3ff", font=("Consolas", 14, "bold"))
        self.lbl_distancia.pack(pady=(0,5))

        # Tarjeta Tiempo
        card_time = tk.Frame(res_frame, bg="#1a202c", bd=1, relief="solid")
        card_time.pack(side="right", expand=True, fill="both", padx=5)
        tk.Label(card_time, text="TIEMPO ESTIMADO", bg="#1a202c", fg="#a0aec0", font=("Consolas", 9)).pack(pady=(5,0))
        self.lbl_tiempo = tk.Label(card_time, text="0.00 min", bg="#1a202c", fg="#00f3ff", font=("Consolas", 14, "bold"))
        self.lbl_tiempo.pack(pady=(0,5))

        # --- ÁREA DE NARRATIVA PASO A PASO ---
        tk.Label(root, text="📋 Instrucciones de Navegación Paso a Paso (Español):", bg="#0b0f19", fg="#ffffff", font=("Consolas", 10, "bold")).pack(anchor="w", padx=20, pady=(10,2))

        self.txt_pasos = scrolledtext.ScrolledText(
            root, 
            bg="#111827", 
            fg="#e2e8f0", 
            insertbackground="white", 
            font=("Consolas", 9),
            height=15
        )
        self.txt_pasos.pack(fill="both", expand=True, padx=20, pady=(0,10))

        # Botón Salir
        btn_salir = tk.Button(
            root, 
            text="❌ SALIR / CERRAR PROGRAMA", 
            command=self.root.quit, 
            bg="#e53e3e", 
            fg="#ffffff", 
            font=("Consolas", 9, "bold"),
            bd=0,
            pady=5
        )
        btn_salir.pack(pady=(0,10))

    def calcular_ruta(self):
        origen = self.ent_origen.get().strip()
        destino = self.ent_destino.get().strip()
        vehiculo = self.combo_vehiculo.get().split()[0]

        if not origen or not destino:
            messagebox.showwarning("Atención", "Por favor ingrese ciudad de origen y destino.")
            return

        self.txt_pasos.delete("1.0", tk.END)
        self.txt_pasos.insert(tk.END, "Calculando ruta en tiempo real desde la API...\n\n")

        try:
            # 1. Geocodificación Origen
            url_orig = f"https://graphhopper.com/api/1/geocode?q={urllib.parse.quote(origen)}&locale=es&key={API_KEY}"
            res_orig = requests.get(url_orig).json()

            # 2. Geocodificación Destino
            url_dest = f"https://graphhopper.com/api/1/geocode?q={urllib.parse.quote(destino)}&locale=es&key={API_KEY}"
            res_dest = requests.get(url_dest).json()

            if not res_orig.get("hits") or not res_dest.get("hits"):
                messagebox.showerror("Error", "No se encontraron coordenadas para alguna de las ubicaciones.")
                return

            lat_orig = res_orig["hits"][0]["point"]["lat"]
            lng_orig = res_orig["hits"][0]["point"]["lng"]
            lat_dest = res_dest["hits"][0]["point"]["lat"]
            lng_dest = res_dest["hits"][0]["point"]["lng"]

            # 3. Consulta de Ruta
            route_url = (
                f"https://graphhopper.com/api/1/route?"
                f"point={lat_orig},{lng_orig}&point={lat_dest},{lng_dest}"
                f"&vehicle={vehiculo}&locale=es&key={API_KEY}"
            )

            res_route = requests.get(route_url)

            if res_route.status_code == 200:
                data = res_route.json()["paths"][0]
                distancia_km = data["distance"] / 1000
                tiempo_min = data["time"] / 60000

                # Formatear datos de salida a máximo 2 decimales (.2f)
                self.lbl_distancia.config(text=f"{distancia_km:.2f} km")
                self.lbl_tiempo.config(text=f"{tiempo_min:.2f} min")

                self.txt_pasos.delete("1.0", tk.END)
                self.txt_pasos.insert(tk.END, f"=== RUTA CALCULADA: {origen.title()} ➔ {destino.title()} ===\n\n")

                for idx, paso in enumerate(data["instructions"], 1):
                    texto = paso["text"]
                    dist = paso["distance"] / 1000
                    self.txt_pasos.insert(tk.END, f"{idx:02d}. {texto} ({dist:.2f} km)\n")

            else:
                messagebox.showerror("Error de API", f"Código HTTP {res_route.status_code} devuelto por Graphhopper.")

        except Exception as e:
            messagebox.showerror("Exception", f"Ocurrió un error al conectar: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = GraphhopperApp(root)
    root.mainloop()