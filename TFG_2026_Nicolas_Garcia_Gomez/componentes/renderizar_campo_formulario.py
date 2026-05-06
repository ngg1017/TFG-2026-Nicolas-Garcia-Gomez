import reflex as rx
from Logica.BBDD import BBDD
from TFG_2026_Nicolas_Garcia_Gomez.estilos.colores import Color

def renderizar_campo_formulario(campo: str):
    return rx.vstack(
        rx.text(campo, size="2", weight="bold"),
        #¿Es booleano?
        rx.cond(
            BBDD.campos_display_booleano.contains(campo),
            rx.box(
                rx.select(
                    ["True", "False"], 
                    value=BBDD.nuevo_paciente_dict[campo].to(str).title(),
                    placeholder="Seleccione (Vacío por defecto)...", 
                    on_change=lambda v: BBDD.actualizar_campo_nuevo(campo, v), 
                    width="100%",
                    size="3",
                    variant="ghost",
                ),
                width="100%",
                background_color=Color.BOOLEANO_FONDO.value, 
                border=f"1px solid #3f3f46",
                border_radius="6px",
                padding="0"
            ),
            rx.cond(
                BBDD.campos_display_fecha.contains(campo),
                #¿Es Fecha Simple?
                rx.input(
                    value=BBDD.nuevo_paciente_dict[campo],
                    placeholder="Ej. DD/MM/YYYY", 
                    on_change=lambda v: BBDD.actualizar_campo_nuevo(campo, v), 
                    background_color="#EF444426",
                    width="100%",
                    size="3"
                ),
                
                #¿Es Fecha Multiple?
                rx.cond(
                    BBDD.campos_display_fecha_multiple.contains(campo),
                    rx.input(
                        value=BBDD.nuevo_paciente_dict[campo],
                        placeholder="Ej. 14/10/2026; 18/10/2026", 
                        on_change=lambda v: BBDD.actualizar_campo_nuevo(campo, v), 
                        width="100%",
                        background_color="#EF444426",
                        size="3"
                    ),
                    
                    #¿Es Numerico?
                    rx.cond(
                        BBDD.campos_display_numerico.contains(campo),
                        rx.input(
                            value=BBDD.nuevo_paciente_dict[campo],
                            placeholder="Introduzca un número...", 
                            on_change=lambda v: BBDD.actualizar_campo_nuevo(campo, v), 
                            width="100%",
                            background_color="#10B9811B",
                            size="3"
                        ),
                        
                        #Texto normal 
                        rx.input(
                            value=BBDD.nuevo_paciente_dict[campo],
                            placeholder="Introduzca texto...", 
                            on_change=lambda v: BBDD.actualizar_campo_nuevo(campo, v), 
                            width="100%",
                            background_color="#F59E0B1A",
                            size="3"
                        )
                    )
                )
            )
        ),
        align_items="start",
        width="100%",
        spacing="1",
        margin_bottom="15px",
    )