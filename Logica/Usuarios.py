import reflex as rx
from Logica.State import State
import bcrypt
from Logica.Modelo import UsuarioDb

#Funciones de criptografia
def encriptar_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def verificar_password(password_plana: str, password_cifrada: str) -> bool:
    return bcrypt.checkpw(password_plana.encode("utf-8"), password_cifrada.encode("utf-8"))

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
        #strip() quita espacios invisibles al copiar/pegar y lower() evita problemas de mayusculas
        email_seguro = self.email.strip().lower()

        with rx.session() as session:
            #Crea un usuario inicial para poder entrar la primera vez
            if not session.exec(UsuarioDb.select()).first():
                print("Base de datos vacía detectada. Creando SuperAdmin temporal...")
                admin = UsuarioDb(
                    email="admin", 
                    password_hash=encriptar_password("admin"), 
                    rol=3
                )
                session.add(admin)
                session.commit()

            #Buscamos al usuario en la base de datos
            usuario_db = session.exec(
                UsuarioDb.select().where(UsuarioDb.email == email_seguro)
            ).first()

            #Logica de validacion
            if usuario_db:
                #Comparamos la clave escrita con el Hash guardado
                if verificar_password(self.password, usuario_db.password_hash):
                    #Registro de auditoria
                    self.registrar_log("INICIAR_SESION", "El usuario inició sesión", email_seguro)

                    #Levanta la barrera y carga los permisos de ese usuario especifico
                    self.autenticado = True
                    self.rol = usuario_db.rol
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
        self.reset()

        #Devolvemos el metodo que borra los archivos
        return State.borrar_datos() 
    
    def cargar_usuarios_tabla(self):
        #Pasa los datos de PostgreSQL a una lista 2D (filas y columnas)
        with rx.session() as session:
            todos = session.exec(UsuarioDb.select()).all()
            #Mostramos "*******" en la tabla en vez del hash real por estetica
            self.lista_usuarios_tabla = [[u.email, "*******", str(u.rol)] for u in todos]

    def abrir_gestion(self):
        #Triple barrera de seguridad para acceder al panel de creacion de usuarios
        email_seguro = self.email_admin_confirmacion.strip().lower()
        
        with rx.session() as session:
            #1. ¿Existes?
            admin_db = session.exec(
                UsuarioDb.select().where(UsuarioDb.email == email_seguro)
            ).first()
            
            if admin_db:
                #2. ¿Tienes el rol 3? 
                if admin_db.rol == 3:
                    #3. ¿Es su clave?
                    if verificar_password(self.clave_admin_confirmacion, admin_db.password_hash): 
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
        
        with rx.session() as session:
            #Buscamos al usuario y lo borramos
            usuario_db = session.exec(
                UsuarioDb.select().where(UsuarioDb.email == email_a_borrar)
            ).first()
            if usuario_db:
                session.delete(usuario_db)
                session.commit()
                
                #Fuerza a la tabla a repintarse sin ese usuario
                self.cargar_usuarios_tabla() 
                self.registrar_log("BORRAR_USUARIO", f"Se eliminó la cuenta: {email_a_borrar}", self.email_admin_confirmacion)
                return rx.toast(f"Usuario {email_a_borrar} eliminado")

    def añadir_usuario(self):
        email_seguro = self.nuevo_email.strip().lower()
        
        #Evita que se guarden datos corruptos o vacios
        if email_seguro == "": 
            return rx.toast("Debes introducir un email para el nuevo usuario")
        if self.nueva_password == "":
            return rx.toast("La contraseña no puede estar vacía")
            
        with rx.session() as session:
            #Validacion de duplicados
            existe = session.exec(
                UsuarioDb.select().where(UsuarioDb.email == email_seguro)
            ).first()
            if existe:
                return rx.toast("Este correo ya está registrado en el sistema")
                
            #Creacion del nuevo nodo en PostgreSQL
            nuevo_user = UsuarioDb(
                email=email_seguro,
                password_hash=encriptar_password(self.nueva_password),
                rol=int(self.nuevo_rol)
            )
            session.add(nuevo_user)
            session.commit()

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
            
        with rx.session() as session:
            #Si el usuario introduce un correo que no esta registrado, se bloquea el proceso.
            usuario_db = session.exec(
                UsuarioDb.select().where(UsuarioDb.email == email_seguro)
            ).first()
            if not usuario_db:
                return rx.toast("El usuario no existe en el sistema.")
            
            #Sobreescribimos la contraseña encriptada
            usuario_db.password_hash = encriptar_password(self.contraseña_nueva)
            session.add(usuario_db)
            session.commit()
        
        #Vaciamos los campos de texto
        self.email_antiguo = ""
        self.contraseña_nueva = ""
        self.contraseña_nueva2 = ""
        
        #Ejecutamos la funcion que cierra la ventana de recuperacion y vuelve al Login
        self.cerrar_recuperacion()
        
        self.registrar_log("CAMBIO_CONTRASEÑA", "Se cambio la contraseña", email_seguro)
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