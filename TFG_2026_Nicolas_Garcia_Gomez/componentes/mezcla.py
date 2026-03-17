import reflex as rx
from Logica.Programa import Programa

def mezcla() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Seleccione Indicadores"),
            rx.form.root(
                rx.flex(
                    rx.select(
                        ["apple", "grape", "pear"],
                        default_value="apple",
                        name="indicador",
                        required=True,
                    ),
                    rx.button("Submit", flex="1", type="submit"),
                    width="100%",
                    spacing="3",
                ),
                on_submit=Programa.seleccion_ind,
                reset_on_submit=True,
            ),
            rx.divider(),
            rx.hstack(
                rx.heading("Results:"),
                rx.badge(Programa.lista_selecc.to_string()),
            ),
            align_items="left",
            width="100%",
        ),
        width="50%",
    )

    

 
