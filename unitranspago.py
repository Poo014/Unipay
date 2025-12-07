import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3
import os
import random

class UniTransPago:
    def __init__(self, root):
        self.root = root
        self.root.title("UniTransPago")
        
        # Configurar formato 9:16 (vertical)
        self.width = 360
        self.height = 640
        self.root.geometry(f"{self.width}x{self.height}")
        self.root.resizable(False, False)
        
        # Variables de estado
        self.usuario_actual = None
        self.dni_actual = None
        
        # Archivo de base de datos SQLite
        self.db_file = 'unitranspago.db'
        
        # Inicializar base de datos
        self.inicializar_db()
        
        # Mostrar pantalla de inicio
        self.mostrar_inicio()
    
    def get_connection(self):
        """Obtener conexión a SQLite"""
        try:
            conn = sqlite3.connect(self.db_file)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            messagebox.showerror("Error de Base de Datos", f"Error al conectar a la base de datos: {e}")
            return None
    
    def inicializar_db(self):
        """Crear base de datos y tablas si no existen"""
        conn = self.get_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        
        try:
            # Tabla usuarios
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id_usuario VARCHAR(20) PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL,
                    dni VARCHAR(20) UNIQUE NOT NULL,
                    id_tarjeta VARCHAR(20) UNIQUE NOT NULL,
                    fecha_registro DATETIME NOT NULL
                )
            """)
            
            # Tabla tarjetas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tarjetas (
                    id_tarjeta VARCHAR(20) PRIMARY KEY,
                    id_usuario VARCHAR(20) NOT NULL,
                    saldo DECIMAL(10, 2) DEFAULT 0.00,
                    activa BOOLEAN DEFAULT 1,
                    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
                )
            """)
            
            # Tabla transacciones
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transacciones (
                    id_transaccion INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_tarjeta VARCHAR(20) NOT NULL,
                    id_usuario VARCHAR(20),
                    tipo VARCHAR(20) NOT NULL,
                    monto DECIMAL(10, 2) NOT NULL,
                    fecha DATETIME NOT NULL,
                    FOREIGN KEY (id_tarjeta) REFERENCES tarjetas(id_tarjeta),
                    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
                )
            """)
            
            # Tabla viajes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS viajes (
                    id_viaje INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_tarjeta VARCHAR(20) NOT NULL,
                    ruta VARCHAR(50),
                    monto DECIMAL(10, 2),
                    fecha DATETIME NOT NULL,
                    FOREIGN KEY (id_tarjeta) REFERENCES tarjetas(id_tarjeta)
                )
            """)
            
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al inicializar base de datos: {e}")
            conn.close()
    
    def limpiar_ventana(self):
        """Limpiar todos los widgets de la ventana"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def mostrar_inicio(self):
        """Pantalla de inicio con opciones de registro e inicio de sesión"""
        self.limpiar_ventana()
        self.usuario_actual = None
        self.dni_actual = None
        
        # Título
        titulo = tk.Label(
            self.root,
            text="UniTransPago",
            font=("Arial", 24, "bold"),
            pady=40
        )
        titulo.pack()
        
        # Subtítulo
        subtitulo = tk.Label(
            self.root,
            text="Sistema de Transporte",
            font=("Arial", 14),
            pady=10
        )
        subtitulo.pack()
        
        # Botones
        frame_botones = tk.Frame(self.root, pady=50)
        frame_botones.pack()
        
        btn_registrarse = tk.Button(
            frame_botones,
            text="Registrarse",
            font=("Arial", 14),
            width=20,
            height=2,
            bg="#4CAF50",
            fg="white",
            command=self.registrarse_sistema
        )
        btn_registrarse.pack(pady=15)
        
        btn_iniciar_sesion = tk.Button(
            frame_botones,
            text="Iniciar Sesión",
            font=("Arial", 14),
            width=20,
            height=2,
            bg="#2196F3",
            fg="white",
            command=self.iniciar_sesion
        )
        btn_iniciar_sesion.pack(pady=15)
        
        # Indicador de estado
        frame_status = tk.Frame(self.root)
        frame_status.pack(pady=5)
        tk.Label(
            frame_status,
            text="✓ Base de datos SQLite",
            font=("Arial", 8),
            fg="green"
        ).pack()
    
    def registrarse_sistema(self):
        """Caso de uso: Registrarse en el sistema"""
        self.limpiar_ventana()
        
        tk.Label(
            self.root,
            text="Registrarse",
            font=("Arial", 20, "bold"),
            pady=20
        ).pack()
        
        frame_form = tk.Frame(self.root, pady=15)
        frame_form.pack()
        
        tk.Label(frame_form, text="Nombre completo:", font=("Arial", 11)).grid(row=0, column=0, sticky="w", pady=8)
        entry_nombre = tk.Entry(frame_form, font=("Arial", 11), width=22)
        entry_nombre.grid(row=0, column=1, pady=8)
        
        tk.Label(frame_form, text="DNI:", font=("Arial", 11)).grid(row=1, column=0, sticky="w", pady=8)
        entry_dni = tk.Entry(frame_form, font=("Arial", 11), width=22)
        entry_dni.grid(row=1, column=1, pady=8)
        
        def registrar():
            nombre = entry_nombre.get().strip()
            dni = entry_dni.get().strip()
            
            if not nombre or not dni:
                messagebox.showerror("Error", "Por favor complete todos los campos")
                return
            
            conn = self.get_connection()
            if not conn:
                return
            
            cursor = conn.cursor()
            
            # Verificar si el DNI ya está registrado
            cursor.execute("SELECT id_usuario FROM usuarios WHERE dni = ?", (dni,))
            if cursor.fetchone():
                cursor.close()
                conn.close()
                messagebox.showerror("Error", "El DNI ya está registrado")
                return
            
            # Generar ID de usuario y tarjeta únicos
            id_usuario = f"USR{random.randint(1000, 9999)}"
            cursor.execute("SELECT id_usuario FROM usuarios WHERE id_usuario = ?", (id_usuario,))
            while cursor.fetchone():
                id_usuario = f"USR{random.randint(1000, 9999)}"
                cursor.execute("SELECT id_usuario FROM usuarios WHERE id_usuario = ?", (id_usuario,))
            
            id_tarjeta = f"TAR{random.randint(100000, 999999)}"
            cursor.execute("SELECT id_tarjeta FROM tarjetas WHERE id_tarjeta = ?", (id_tarjeta,))
            while cursor.fetchone():
                id_tarjeta = f"TAR{random.randint(100000, 999999)}"
                cursor.execute("SELECT id_tarjeta FROM tarjetas WHERE id_tarjeta = ?", (id_tarjeta,))
            
            fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            try:
                # Registrar usuario
                cursor.execute("""
                    INSERT INTO usuarios (id_usuario, nombre, dni, id_tarjeta, fecha_registro)
                    VALUES (?, ?, ?, ?, ?)
                """, (id_usuario, nombre, dni, id_tarjeta, fecha_registro))
                
                # Crear tarjeta
                cursor.execute("""
                    INSERT INTO tarjetas (id_tarjeta, id_usuario, saldo, activa)
                    VALUES (?, ?, ?, ?)
                """, (id_tarjeta, id_usuario, 0.00, True))
                
                conn.commit()
                cursor.close()
                conn.close()
                
                messagebox.showinfo(
                    "Registro exitoso", 
                    f"Usuario {nombre} registrado correctamente.\n\n"
                    f"ID de Usuario: {id_usuario}\n"
                    f"ID de Tarjeta: {id_tarjeta}\n\n"
                    f"Puede iniciar sesión ahora."
                )
                self.mostrar_inicio()
            except sqlite3.Error as e:
                conn.rollback()
                cursor.close()
                conn.close()
                messagebox.showerror("Error", f"Error al registrar usuario: {e}")
        
        btn_registrar = tk.Button(
            frame_form,
            text="Registrarse",
            font=("Arial", 12),
            bg="#4CAF50",
            fg="white",
            width=15,
            command=registrar
        )
        btn_registrar.grid(row=2, column=0, columnspan=2, pady=20)
        
        btn_volver = tk.Button(
            self.root,
            text="Volver al inicio",
            font=("Arial", 10),
            command=self.mostrar_inicio
        )
        btn_volver.pack(pady=10)
    
    def iniciar_sesion(self):
        """Iniciar sesión con nombre y DNI"""
        self.limpiar_ventana()
        
        tk.Label(
            self.root,
            text="Iniciar Sesión",
            font=("Arial", 20, "bold"),
            pady=20
        ).pack()
        
        frame_form = tk.Frame(self.root, pady=15)
        frame_form.pack()
        
        tk.Label(frame_form, text="Nombre completo:", font=("Arial", 11)).grid(row=0, column=0, sticky="w", pady=8)
        entry_nombre = tk.Entry(frame_form, font=("Arial", 11), width=22)
        entry_nombre.grid(row=0, column=1, pady=8)
        
        tk.Label(frame_form, text="DNI:", font=("Arial", 11)).grid(row=1, column=0, sticky="w", pady=8)
        entry_dni = tk.Entry(frame_form, font=("Arial", 11), width=22)
        entry_dni.grid(row=1, column=1, pady=8)
        
        def login():
            nombre = entry_nombre.get().strip()
            dni = entry_dni.get().strip()
            
            if not nombre or not dni:
                messagebox.showerror("Error", "Por favor complete todos los campos")
                return
            
            conn = self.get_connection()
            if not conn:
                return
            
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id_usuario, nombre FROM usuarios 
                WHERE nombre = ? AND dni = ?
            """, (nombre, dni))
            
            resultado = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if not resultado:
                messagebox.showerror("Error", "Usuario no encontrado. Verifique nombre y DNI.")
                return
            
            # Iniciar sesión exitosa
            self.usuario_actual = resultado[0]
            self.dni_actual = dni
            messagebox.showinfo("Éxito", f"Bienvenido, {nombre}!")
            self.menu_usuario()
        
        btn_login = tk.Button(
            frame_form,
            text="Iniciar Sesión",
            font=("Arial", 12),
            bg="#2196F3",
            fg="white",
            width=15,
            command=login
        )
        btn_login.grid(row=2, column=0, columnspan=2, pady=20)
        
        btn_volver = tk.Button(
            self.root,
            text="Volver al inicio",
            font=("Arial", 10),
            command=self.mostrar_inicio
        )
        btn_volver.pack(pady=10)
    
    def menu_usuario(self):
        """Menú principal para usuarios autenticados"""
        if not self.usuario_actual:
            messagebox.showerror("Error", "Debe iniciar sesión primero")
            self.mostrar_inicio()
            return
        
        self.limpiar_ventana()
        
        # Información del usuario desde SQLite
        conn = self.get_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.nombre, u.id_tarjeta, t.saldo 
            FROM usuarios u
            JOIN tarjetas t ON u.id_tarjeta = t.id_tarjeta
            WHERE u.id_usuario = ?
        """, (self.usuario_actual,))
        
        resultado = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not resultado:
            messagebox.showerror("Error", "Usuario no encontrado")
            self.mostrar_inicio()
            return
        
        nombre = resultado[0]  # nombre está en índice 0
        id_tarjeta = resultado[1]  # id_tarjeta está en índice 1
        saldo = float(resultado[2])  # saldo está en índice 2
        
        tk.Label(
            self.root,
            text="Mi Cuenta",
            font=("Arial", 20, "bold"),
            pady=15
        ).pack()
        
        # Información del usuario
        frame_info = tk.Frame(self.root, pady=10)
        frame_info.pack()
        
        tk.Label(
            frame_info,
            text=f"Usuario: {nombre}",
            font=("Arial", 11),
            anchor="w"
        ).pack(pady=3)
        
        tk.Label(
            frame_info,
            text=f"Tarjeta: {id_tarjeta}",
            font=("Arial", 11),
            anchor="w"
        ).pack(pady=3)
        
        tk.Label(
            frame_info,
            text=f"Saldo: ${saldo:.2f}",
            font=("Arial", 13, "bold"),
            fg="green",
            anchor="w"
        ).pack(pady=5)
        
        # Separador
        tk.Label(self.root, text="─" * 40, font=("Arial", 8), fg="gray").pack(pady=10)
        
        # Botones de opciones
        frame_botones = tk.Frame(self.root, pady=15)
        frame_botones.pack()
        
        btn_recargar = tk.Button(
            frame_botones,
            text="Recargar tarjeta",
            font=("Arial", 12),
            width=25,
            height=2,
            bg="#4CAF50",
            fg="white",
            command=self.recargar_tarjeta
        )
        btn_recargar.pack(pady=8)
        
        btn_consultar = tk.Button(
            frame_botones,
            text="Consultar saldo",
            font=("Arial", 12),
            width=25,
            height=2,
            bg="#2196F3",
            fg="white",
            command=self.consultar_saldo
        )
        btn_consultar.pack(pady=8)
        
        btn_cerrar_sesion = tk.Button(
            frame_botones,
            text="Cerrar Sesión",
            font=("Arial", 10),
            width=20,
            bg="#f44336",
            fg="white",
            command=self.cerrar_sesion
        )
        btn_cerrar_sesion.pack(pady=20)
    
    def recargar_tarjeta(self):
        """Caso de uso: Recargar tarjeta"""
        if not self.usuario_actual:
            messagebox.showerror("Error", "Debe iniciar sesión primero")
            self.mostrar_inicio()
            return
        
        self.limpiar_ventana()
        
        # Obtener información de la tarjeta desde SQLite
        conn = self.get_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id_tarjeta FROM usuarios WHERE id_usuario = ?
        """, (self.usuario_actual,))
        resultado = cursor.fetchone()
        
        if not resultado:
            cursor.close()
            conn.close()
            messagebox.showerror("Error", "Usuario no encontrado")
            self.mostrar_inicio()
            return
        
        id_tarjeta = resultado[0]
        
        cursor.execute("""
            SELECT saldo FROM tarjetas WHERE id_tarjeta = ?
        """, (id_tarjeta,))
        resultado = cursor.fetchone()
        cursor.close()
        conn.close()
        
        saldo_actual = float(resultado[0]) if resultado else 0.0
        
        tk.Label(
            self.root,
            text="Recargar Tarjeta",
            font=("Arial", 18, "bold"),
            pady=15
        ).pack()
        
        # Mostrar información de la tarjeta
        frame_info = tk.Frame(self.root, pady=5)
        frame_info.pack()
        
        tk.Label(
            frame_info,
            text=f"Tarjeta: {id_tarjeta}",
            font=("Arial", 10)
        ).pack(pady=3)
        
        tk.Label(
            frame_info,
            text=f"Saldo actual: ${saldo_actual:.2f}",
            font=("Arial", 11, "bold"),
            fg="green"
        ).pack(pady=3)
        
        frame_form = tk.Frame(self.root, pady=15)
        frame_form.pack()
        
        tk.Label(frame_form, text="Monto a recargar:", font=("Arial", 11)).pack(pady=5)
        entry_monto = tk.Entry(frame_form, font=("Arial", 11), width=20)
        entry_monto.pack(pady=5)
        
        # Botones de monto rápido
        frame_rapido = tk.Frame(frame_form, pady=10)
        frame_rapido.pack()
        
        def recargar_rapido(monto):
            entry_monto.delete(0, tk.END)
            entry_monto.insert(0, str(monto))
        
        tk.Button(frame_rapido, text="$10.000", font=("Arial", 9), width=8, 
                 command=lambda: recargar_rapido(10000)).pack(side=tk.LEFT, padx=3)
        tk.Button(frame_rapido, text="$20.000", font=("Arial", 9), width=8,
                 command=lambda: recargar_rapido(20000)).pack(side=tk.LEFT, padx=3)
        tk.Button(frame_rapido, text="$50.000", font=("Arial", 9), width=8,
                 command=lambda: recargar_rapido(50000)).pack(side=tk.LEFT, padx=3)
        
        def recargar():
            try:
                monto = float(entry_monto.get())
            except ValueError:
                messagebox.showerror("Error", "Ingrese un monto válido")
                return
            
            if monto <= 0:
                messagebox.showerror("Error", "El monto debe ser mayor a 0")
                return
            
            # Recargar en SQLite
            conn = self.get_connection()
            if not conn:
                return
            
            cursor = conn.cursor()
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            try:
                # Actualizar saldo
                cursor.execute("""
                    UPDATE tarjetas SET saldo = saldo + ? 
                    WHERE id_tarjeta = ?
                """, (monto, id_tarjeta))
                
                # Registrar transacción
                cursor.execute("""
                    INSERT INTO transacciones (id_tarjeta, id_usuario, tipo, monto, fecha)
                    VALUES (?, ?, ?, ?, ?)
                """, (id_tarjeta, self.usuario_actual, "recarga", monto, fecha))
                
                conn.commit()
                
                # Obtener nuevo saldo
                cursor.execute("SELECT saldo FROM tarjetas WHERE id_tarjeta = ?", (id_tarjeta,))
                nuevo_saldo = float(cursor.fetchone()[0])
                
                cursor.close()
                conn.close()
                
                messagebox.showinfo(
                    "Éxito", 
                    f"Tarjeta recargada con ${monto:.2f}\n\n"
                    f"Nuevo saldo: ${nuevo_saldo:.2f}"
                )
                self.menu_usuario()
            except sqlite3.Error as e:
                conn.rollback()
                cursor.close()
                conn.close()
                messagebox.showerror("Error", f"Error al recargar tarjeta: {e}")
        
        btn_recargar = tk.Button(
            frame_form,
            text="Recargar",
            font=("Arial", 12),
            bg="#4CAF50",
            fg="white",
            width=15,
            command=recargar
        )
        btn_recargar.pack(pady=15)
        
        btn_volver = tk.Button(
            self.root,
            text="Volver al menú",
            font=("Arial", 10),
            command=self.menu_usuario
        )
        btn_volver.pack(pady=10)
    
    def consultar_saldo(self):
        """Caso de uso: Consultar saldo"""
        if not self.usuario_actual:
            messagebox.showerror("Error", "Debe iniciar sesión primero")
            self.mostrar_inicio()
            return
        
        self.limpiar_ventana()
        
        # Obtener información desde SQLite
        conn = self.get_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id_tarjeta, t.saldo, t.activa 
            FROM usuarios u
            JOIN tarjetas t ON u.id_tarjeta = t.id_tarjeta
            WHERE u.id_usuario = ?
        """, (self.usuario_actual,))
        
        resultado = cursor.fetchone()
        if not resultado:
            cursor.close()
            conn.close()
            messagebox.showerror("Error", "Usuario no encontrado")
            self.mostrar_inicio()
            return
        
        id_tarjeta = resultado[0]
        saldo = float(resultado[1])
        activa = bool(resultado[2])
        estado = "Activa" if activa else "Inactiva"
        
        tk.Label(
            self.root,
            text="Consultar Saldo",
            font=("Arial", 18, "bold"),
            pady=20
        ).pack()
        
        frame_info = tk.Frame(self.root, pady=20)
        frame_info.pack()
        
        tk.Label(
            frame_info,
            text="Información de la Tarjeta",
            font=("Arial", 14, "bold"),
            pady=10
        ).pack()
        
        tk.Label(
            frame_info,
            text=f"ID Tarjeta: {id_tarjeta}",
            font=("Arial", 11),
            pady=8
        ).pack()
        
        tk.Label(
            frame_info,
            text=f"Estado: {estado}",
            font=("Arial", 11),
            pady=5
        ).pack()
        
        tk.Label(
            frame_info,
            text=f"Saldo disponible:",
            font=("Arial", 11),
            pady=10
        ).pack()
        
        tk.Label(
            frame_info,
            text=f"${saldo:,.2f}",
            font=("Arial", 24, "bold"),
            fg="green",
            pady=10
        ).pack()
        
        # Últimas transacciones
        tk.Label(
            self.root,
            text="─" * 40,
            font=("Arial", 8),
            fg="gray"
        ).pack(pady=10)
        
        tk.Label(
            self.root,
            text="Últimas transacciones",
            font=("Arial", 12, "bold"),
            pady=5
        ).pack()
        
        # Obtener últimas 5 transacciones de este usuario desde SQLite
        cursor.execute("""
            SELECT tipo, monto, fecha 
            FROM transacciones 
            WHERE id_tarjeta = ? 
            ORDER BY fecha DESC 
            LIMIT 5
        """, (id_tarjeta,))
        
        transacciones_usuario = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if transacciones_usuario:
            frame_trans = tk.Frame(self.root, pady=5)
            frame_trans.pack()
            
            for trans in transacciones_usuario:
                tipo = trans[0]
                monto = float(trans[1])
                fecha = str(trans[2])
                color = "green" if tipo == "recarga" else "red"
                simbolo = "+" if tipo == "recarga" else "-"
                
                tk.Label(
                    frame_trans,
                    text=f"{tipo.capitalize()}: {simbolo}${monto:.2f} - {fecha[:16]}",
                    font=("Arial", 9),
                    fg=color
                ).pack(pady=2)
        else:
            tk.Label(
                self.root,
                text="No hay transacciones registradas",
                font=("Arial", 9),
                fg="gray"
            ).pack(pady=5)
        
        btn_volver = tk.Button(
            self.root,
            text="Volver al menú",
            font=("Arial", 10),
            command=self.menu_usuario
        )
        btn_volver.pack(pady=20)
    
    def cerrar_sesion(self):
        """Cerrar sesión y volver al inicio"""
        self.usuario_actual = None
        self.dni_actual = None
        self.mostrar_inicio()


def main():
    root = tk.Tk()
    app = UniTransPago(root)
    root.mainloop()


if __name__ == "__main__":
    main()
