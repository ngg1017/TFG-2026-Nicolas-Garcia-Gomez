import reflex as rx
from typing import Optional
from datetime import datetime, timezone
from sqlmodel import Field

#Al heredar de rx.Model, Reflex crea automaticamente una columna 'id' (entero, clave primaria)
class Registro(rx.Model, table=True):
    __tablename__ = "registro"
    #Identificador unico (Obligatorio)
    num_historia: str
    
    #Fechas y Datos de Ingreso
    fecha_ingreso: Optional[str] = None
    fecha_alta: Optional[str] = None
    reingreso_48: Optional[str] = None
    especialidad_ingreso: Optional[str] = None
    ingreso_urgencia: Optional[str] = None
    fallecimiento: Optional[str] = None
    apache: Optional[float] = None
    
    #Respiratorio
    vmi: Optional[str] = None
    dias_vmi: Optional[float] = None
    barotrauma: Optional[str] = None
    grados_inclinacion: Optional[float] = None
    episodios_nav: Optional[str] = None
    registro_intubaciones: Optional[str] = None
    extubacion_programada: Optional[str] = None
    extubacion_maniobras: Optional[str] = None
    
    #Hemodinamica y Sepsis
    sepsis: Optional[str] = None
    shock_septico: Optional[str] = None
    pam_ingreso: Optional[float] = None
    pam_6h: Optional[float] = None
    pam_24h: Optional[float] = None
    diuresis_ingreso: Optional[float] = None
    diuresis_6h: Optional[float] = None
    diuresis_24h: Optional[float] = None
    lactato_ingreso: Optional[float] = None
    lactato_6h: Optional[float] = None
    lactato_24h: Optional[float] = None
    
    #Infeccioso
    tratamiento_adecuado: Optional[str] = None
    cobertura_empirica_completa: Optional[str] = None
    resistencia_antibioticos: Optional[str] = None
    numero_episodios_bacteriemia: Optional[float] = None
    numero_total_dias_cvc: Optional[float] = None
    
    #Sedacion y Neurologico
    rass: Optional[float] = None
    bis: Optional[float] = None
    rass_objetivo: Optional[float] = None
    bis_objetivo: Optional[float] = None
    ventana_sedacion: Optional[str] = None
    
    #Digestivo y Coagulacion
    fecha_inicio_ne: Optional[str] = None
    omeprazol: Optional[str] = None
    tratamiento_corticoides: Optional[str] = None
    antecedentes_hemorragia_gi: Optional[str] = None
    coagulopatia: Optional[str] = None
    insuficiencia_renal: Optional[str] = None
    insuficiencia_hepatica: Optional[str] = None
    
    #Cuidados y Seguridad
    upp: Optional[str] = None
    profilaxis_tvp: Optional[str] = None
    tvp: Optional[str] = None
    glucemia: Optional[float] = None
    tratamiento_insulina: Optional[str] = None
    traslado_intrahospitalario: Optional[str] = None
    listado_verificacion: Optional[str] = None
    eventos_adversos_traslado: Optional[str] = None
    actos_transfusionales: Optional[str] = None
    sangrado_activo: Optional[str] = None
    cantidad_transfusion_dia: Optional[float] = None

class Auditoria(rx.Model, table=True):
    usuario_final: str 
    accion: str   
    detalles: Optional[str] = None  
    
    #Genera la fecha y hora exacta automaticamente en el momento de guardarse
    fecha: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

class UsuarioDb(rx.Model, table=True):
    #unique=True impide duplicados
    email: str = Field(unique=True, index=True) 
    #Guardaremos el cifrado, nunca la clave real
    password_hash: str 
    rol: int