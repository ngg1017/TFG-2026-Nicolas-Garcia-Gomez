import reflex as rx
import json
import os
from Logica.State import State

class Usuarios(rx.State):
    #Login normal
    #Almacenan lo que el usuario escribe en la pantalla principal de login
    email: str = ""
    password: str = ""
    
    #Variables de sesion
    #Controlan si estas dentro de la app y el rol
    #"autenticado" es el muro que protege la app. "rol" dictara que botones puedes ver.
    autenticado: bool = False
    rol: int = 0
    mensaje_error: str = ""

    #Variables panel de gestion
    #El texto de entrada a la gestion
    clave_admin_confirmacion: str = ""
    email_admin_confirmacion: str = "" 
    #Si es True, la pantalla cambia al panel de control 
    viendo_gestion: bool = False 

    #Variables para Crear/Lerr/Borrar
    #"lista_usuarios_tabla": Reflex necesita una lista para dibujar una tabla, no puede dibujar un JSON directamente.
    lista_usuarios_tabla: list[list[str]] = []
    
    #Lo que el Admin escribe al crear un usuario nuevo
    nuevo_email: str = ""
    nueva_password: str = ""
    nuevo_rol: str = "1"

    #Variables para el cambio de contraseña
    email_antiguo: str = ""
    contraseña_nueva: str = ""
    contraseña_nueva2: str = ""
    viendo_recuperacion: bool = False

    def iniciar_sesion(self):
        #Desaparezcan mensajes de error antiguos
        self.mensaje_error = ""

        #Comprobacion: Evita que la app crashee si se borra el archivo JSON accidentalmente
        ruta_archivo = "usuarios.json"
        if not os.path.exists(ruta_archivo):
            self.mensaje_error = "Error: No se encuentra la base de usuarios."
            return

        #Lectura de BBDD local
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            base_usuarios = json.load(f)

        #strip() quita espacios invisibles al copiar/pegar y lower() evita problemas de mayusculas
        email_seguro = self.email.strip().lower()

        #Logica de validacion
        if email_seguro in base_usuarios:
            if base_usuarios[email_seguro]["password"] == self.password:
                #Registro de auditoria
                self.registrar_log("INICIAR_SESION", "El usuario inició sesión")

                #Levanta la barrera y carga los permisos de ese usuario especifico
                self.autenticado = True
                self.rol = base_usuarios[email_seguro]["rol"]
            else:
                self.mensaje_error = "Contraseña incorrecta."
        else:
            self.mensaje_error = "El usuario no existe."
            
    def cerrar_sesion(self):
        #Destruye la sesion actual, devolviendo todas las variables a su estado inicial. 
        #El redirect expulsa al usuario al Login.
        self.autenticado = False

        self.registrar_log("CERRAR_SESION", "El usuario cerró sesión")
        self.rol = 0
        self.email = ""
        self.password = ""

        #Devolvemos el metodo que borra los archivos
        return State.borrar_datos() 
    
    def cargar_usuarios_tabla(self):
        #Pasa los datos del JSON (un diccionario) a una lista 2D (filas y columnas)
        #Esto es obligatorio porque el componente rx.table de Reflex solo entiende listas iterables.
        ruta_archivo = "usuarios.json"
        if os.path.exists(ruta_archivo):
            with open(ruta_archivo, "r", encoding="utf-8") as f:
                base = json.load(f)
            #Comprension de listas en Python: [email, contraseña, rol convertido a texto]
            self.lista_usuarios_tabla = [[k, v["password"], str(v["rol"])] for k, v in base.items()]

    def abrir_gestion(self):
        #Triple barrera de seguridad para acceder al panel de creacion de usuarios
        email_seguro = self.email_admin_confirmacion.strip().lower()
        ruta_archivo = "usuarios.json"
        
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            base = json.load(f)
        
        #1. ¿Existes?
        if email_seguro in base:
            #2. ¿Tienes el maximo poder (Rol 3)? 
            if base[email_seguro]["rol"] == 3:
                #3. ¿Es su clave? 
                if base[email_seguro]["password"] == self.clave_admin_confirmacion: 
                    self.viendo_gestion = True
                    self.mensaje_error = ""
                    #Carga los datos para que la tabla no aparezca vacia
                    self.cargar_usuarios_tabla() 
                else:
                    self.mensaje_error = "Contraseña de administrador incorrecta."
            else:
                self.mensaje_error = "Este usuario no tiene permisos (Rol 3)."
        else:
            self.mensaje_error = "El usuario administrador no existe."

    def cerrar_gestion(self):
        #Cierra el panel de administracion sin cerrar la sesion principal
        self.viendo_gestion = False
        self.clave_admin_confirmacion = ""
        self.email_admin_confirmacion = ""

    def eliminar_usuario(self, email_a_borrar: str):
        #Un administrador no puede suicidarse digitalmente
        if email_a_borrar == self.email_admin_confirmacion.strip().lower():
            return rx.toast("No puedes eliminar tu propia cuenta") 
        
        ruta_archivo = "usuarios.json"
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            base = json.load(f)
        
        #Si pasa las reglas, se borra del diccionario y se sobreescribe el archivo
        if email_a_borrar in base:
            del base[email_a_borrar]
            with open(ruta_archivo, "w", encoding="utf-8") as f:
                json.dump(base, f, indent=4)
            #Fuerza a la tabla a repintarse sin ese usuario
            self.cargar_usuarios_tabla() 
            self.registrar_log("BORRAR_USUARIO", f"Se eliminó la cuenta: {email_a_borrar}", self.email_admin_confirmacion)
            return rx.toast(f"Usuario {email_a_borrar} eliminado")

    def añadir_usuario(self):
        email_seguro = self.nuevo_email.strip().lower()
        password_segura = self.nueva_password
        
        #Evita que se guarden datos corruptos o vacios
        if email_seguro == "": 
            return rx.toast("Debes introducir un email para el nuevo usuario")
        if password_segura == "":
            return rx.toast("La contraseña no puede estar vacía")
            
        ruta_archivo = "usuarios.json"
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            base = json.load(f)
        
        #Validacion de duplicados
        if email_seguro in base:
            return rx.toast("Este correo ya está registrado en el sistema")
            
        #Creacion del nuevo nodo en el JSON
        base[email_seguro] = {
            "password": password_segura,
            "rol": int(self.nuevo_rol)
        }
        with open(ruta_archivo, "w", encoding="utf-8") as f:
            json.dump(base, f, indent=4)

        #Actualiza la vista  
        self.cargar_usuarios_tabla() 
        
        #Limpia las cajas de texto tras añadir para que esten listas para el siguiente
        self.nuevo_email = ""
        self.nueva_password = ""
        
        self.registrar_log("NUEVO_USUARIO", f"Se creó cuenta para: {email_seguro} con Rol {self.nuevo_rol}", self.email_admin_confirmacion)
        return rx.toast(f"Usuario {email_seguro} añadido con éxito")

    def cambiar_contraseña(self):
        #Limpiamos el email de espacios accidentales y lo pasamos a minusculas
        email_seguro = self.email_antiguo.strip().lower()
        
        #Evita que el programa intente procesar datos corruptos, vacios o mal escritos.
        if email_seguro == "": 
            return rx.toast("Debes introducir tu correo electrónico")
            
        if self.contraseña_nueva == "":
            return rx.toast("La contraseña no puede estar vacía")
            
        if self.contraseña_nueva2 == "":
            return rx.toast("Debes repetir la contraseña")
            
        #Evita errores tipograficos al cambiar la clave
        if self.contraseña_nueva != self.contraseña_nueva2:
            return rx.toast("Las contraseñas deben coincidir")
            
        #Lectura de la base de datos
        ruta_archivo = "usuarios.json"
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            base = json.load(f)
        
        #Si el usuario introduce un correo que no esta registrado, se bloquea el proceso.
        if email_seguro not in base:
            return rx.toast("El usuario no existe en el sistema.")
        
        #Sobreescribimos el valor de la clave "password" de ese usuario especifico
        base[email_seguro]["password"] = self.contraseña_nueva

        #Abrimos el archivo en modo escritura ("w") y guardamos el diccionario actualizado
        with open(ruta_archivo, "w", encoding="utf-8") as f:
            json.dump(base, f, indent=4)
        
        # Vaciamos los campos de texto para que, si otro usuario intenta recuperar su clave después, no vea las contraseñas escritas anteriormente.
        self.email_antiguo = ""
        self.contraseña_nueva = ""
        self.contraseña_nueva2 = ""
        
        #Ejecutamos la funcion que cierra la ventana de recuperación y vuelve al Login
        self.cerrar_recuperacion()
        
        self.registrar_log("CAMBIO_CONTRASEÑA", "Se cambio la contraseña", self.email_antiguo)
        return rx.toast(f"Cambio de contraseña en Usuario {email_seguro} exitoso")
    
    #Sistema de auditoria
    def registrar_log(self, accion: str, detalles: str = "", usuario: str = ""):
        #Importamos la tabla para auditoria
        from Logica.Modelo import Auditoria 
        with rx.session() as session:
            log = Auditoria(
                usuario_final=self.email if usuario=="" else usuario,
                accion=accion,
                detalles=detalles
            )
            session.add(log)
            session.commit()

    #Funciones que controlan la apertura de la recuperacion
    def abrir_recuperacion(self):
        #Cierra el panel de recuperacion sin cerrar la sesion principal
        self.viendo_recuperacion = True
    
    def cerrar_recuperacion(self):
        #Cierra el panel de recuperacion sin cerrar la sesion principal
        self.viendo_recuperacion = False
    
    #Las dos primeras ademas tienen el trabajo extra de borrar el mensaje de error en rojo en cuanto el usuario vuelve a tocar el teclado.
    def actualizar_email(self, valor: str):
        self.email = valor
        self.mensaje_error = ""

    def actualizar_password(self, valor: str):
        self.password = valor
        self.mensaje_error = ""
    
    #El resto son simples asignadores directos definidos a mano para cumplir con los estandares de las versiones futuras de Reflex (>0.9.0)
    def set_nuevo_email(self, valor: str):
        self.nuevo_email = valor

    def set_nueva_password(self, valor: str):
        self.nueva_password = valor

    def set_nuevo_rol(self, valor: str):
        self.nuevo_rol = valor

    def set_email_admin_confirmacion(self, valor: str):
        self.email_admin_confirmacion = valor

    def set_clave_admin_confirmacion(self, valor: str):
        self.clave_admin_confirmacion = valor
    
    def set_email_antiguo(self, valor: str):
        self.email_antiguo = valor
    
    def set_contraseña_nueva(self, valor: str):
        self.contraseña_nueva = valor

    def set_contraseña_nueva2(self, valor: str):
        self.contraseña_nueva2 = valor