#!/usr/bin/env python3
"""
generar_contrato_demo.py
Genera un contrato de proveedores ficticio en PDF con texto real (no imagen).
Incluye múltiples cláusulas de riesgo para probar el analizador.
"""
import sys
import textwrap
from pathlib import Path

import fitz  # PyMuPDF

# ── Contenido del contrato ─────────────────────────────────────────────────────
# Incluye intencionalmente: ajuste de precios, renovación automática,
# preaviso de cancelación, exclusividad, penalidades, confidencialidad,
# limitación de responsabilidad, cesión, indemnidad, jurisdicción.

CONTRATO = """\
CONTRATO DE PRESTACIÓN DE SERVICIOS TECNOLÓGICOS


Entre:

DATAFLOW SISTEMAS S.R.L., CUIT 30-71892456-9, con domicilio en Av. Corrientes 3456,
piso 4°, Ciudad Autónoma de Buenos Aires, representada por su Gerente General, Ing.
Alejandro Morales, DNI 24.567.890, en adelante denominada "EL PROVEEDOR";

y

DISTRIBUIDORA DEL NORTE S.A., CUIT 30-65124789-2, con domicilio en Av. Mitre 1200,
San Miguel de Tucumán, Provincia de Tucumán, representada por su Directora Comercial,
Cra. Valentina Ramos, DNI 28.901.234, en adelante denominada "EL CLIENTE";

las partes acuerdan celebrar el presente Contrato de Prestación de Servicios
Tecnológicos (en adelante "el Contrato"), sujeto a las siguientes cláusulas:


CLÁUSULA PRIMERA: OBJETO DEL CONTRATO

El Proveedor se obliga a prestar al Cliente servicios de desarrollo, implementación y
mantenimiento de la plataforma de gestión de inventario y logística denominada
"LOGFLOW Pro". Los servicios comprenden:
  a) Licencia de uso de la plataforma LOGFLOW Pro para hasta cincuenta (50) usuarios;
  b) Soporte técnico en días hábiles, de lunes a viernes en el horario de 9:00 a 18:00 hs;
  c) Actualizaciones de seguridad y mejoras funcionales incluidas en el precio;
  d) Capacitación inicial para hasta diez (10) usuarios designados por el Cliente.


CLÁUSULA SEGUNDA: PRECIO DE LOS SERVICIOS

El precio mensual por la prestación de los servicios acordados es de PESOS CIENTO
OCHENTA MIL ($180.000), más el Impuesto al Valor Agregado (IVA) correspondiente. El
pago deberá efectuarse dentro de los primeros cinco (5) días hábiles de cada mes
calendario, mediante transferencia bancaria a la cuenta indicada por el Proveedor.


CLÁUSULA TERCERA: AJUSTE DE PRECIOS

El precio establecido en la Cláusula Segunda será ajustado en forma automática cada
tres (3) meses, en base a la variación acumulada del Índice de Precios al Consumidor
(IPC) publicado por el Instituto Nacional de Estadística y Censos (INDEC)
correspondiente al trimestre anterior. El ajuste operará sin necesidad de notificación
previa ni acuerdo expreso entre las partes, siendo suficiente comunicación la remisión
de la factura con el nuevo importe actualizado. En ningún caso el ajuste podrá ser
negativo.


CLÁUSULA CUARTA: PLAZO DE VIGENCIA Y RENOVACIÓN

El presente Contrato tendrá una vigencia inicial de veinticuatro (24) meses contados
desde la fecha de su suscripción. Vencido dicho plazo, se renovará automáticamente por
períodos consecutivos de doce (12) meses cada uno, salvo que cualquiera de las partes
notifique fehacientemente a la otra, con una antelación no menor a noventa (90) días
corridos previos al vencimiento en curso, su voluntad de no prorrogar el Contrato.

La falta de notificación en tiempo y forma implicará la renovación automática del
Contrato en los mismos términos y condiciones vigentes al momento del vencimiento.


CLÁUSULA QUINTA: EXCLUSIVIDAD

5.1. Exclusividad del Cliente: Durante la vigencia del presente Contrato y por un
período de dieciocho (18) meses contados desde su terminación por cualquier causa, el
Cliente se compromete a no contratar, directa ni indirectamente, a ningún otro
proveedor de sistemas de gestión de inventario y logística que compita con la
plataforma LOGFLOW Pro, en el territorio de las provincias de Tucumán, Salta y Jujuy.

5.2. Exclusividad del Proveedor: El Proveedor no podrá comercializar la plataforma
LOGFLOW Pro ni prestar servicios similares a empresas distribuidoras mayoristas con
operaciones en las provincias indicadas que sean competencia directa del Cliente,
durante la vigencia del presente Contrato.


CLÁUSULA SEXTA: PENALIDADES POR INCUMPLIMIENTO Y RESCISIÓN

6.1. Incumplimiento del Proveedor: En caso de que el Proveedor no resuelva una
interrupción del servicio calificada como "crítica" dentro de las cuatro (4) horas
hábiles de notificada fehacientemente, el Cliente tendrá derecho a aplicar una
penalidad del tres por ciento (3%) sobre el precio mensual por cada hora adicional de
demora, hasta un máximo acumulable del veinte por ciento (20%) del precio mensual.

6.2. Rescisión anticipada por el Cliente sin causa: Si el Cliente rescindiera el
Contrato antes de su vencimiento sin causa imputable al Proveedor, deberá abonar en
concepto de indemnización una suma equivalente al precio de tres (3) meses de
servicio, calculada sobre el último precio vigente al momento de la rescisión.

6.3. Rescisión anticipada por el Proveedor sin causa: Si el Proveedor rescindiera el
Contrato antes de su vencimiento sin causa imputable al Cliente, deberá restituir el
equivalente al precio de dos (2) meses de servicio ya abonados, a título de
compensación por los daños ocasionados al Cliente.


CLÁUSULA SÉPTIMA: CONFIDENCIALIDAD

7.1. Ambas partes se obligan a mantener en estricta confidencialidad toda información
técnica, comercial, financiera y estratégica que reciban en virtud del presente
Contrato, sin que dicha obligación requiera estar expresamente marcada como
"confidencial" en cada documento.

7.2. La obligación de confidencialidad subsistirá durante la vigencia del Contrato y
por un período de cinco (5) años contados desde su vencimiento o resolución por
cualquier causa, con independencia del motivo de extinción.

7.3. Las partes solo podrán divulgar información confidencial cuando sea requerida
por orden judicial o autoridad competente, y en la medida estrictamente necesaria,
debiendo notificar previamente a la otra parte si las circunstancias lo permitieran.

7.4. El incumplimiento de esta cláusula habilitará a la parte afectada a iniciar las
acciones civiles y penales que correspondan, sin perjuicio de la facultad de exigir
el cese inmediato de la divulgación.


CLÁUSULA OCTAVA: LIMITACIÓN DE RESPONSABILIDAD

La responsabilidad total y acumulada del Proveedor frente al Cliente por cualquier
concepto derivado del presente Contrato —sea por incumplimiento, negligencia o
cualquier otra causa— no podrá exceder en ningún caso el equivalente al precio de
tres (3) meses de servicio efectivamente abonado por el Cliente en el período
inmediatamente anterior al evento generador del daño. Quedan excluidos expresamente
los daños indirectos, el lucro cesante, la pérdida de chance y todo daño consecuente,
aunque el Proveedor hubiese sido informado de la posibilidad de que tales daños
pudieran producirse.


CLÁUSULA NOVENA: CESIÓN DEL CONTRATO

Ninguna de las partes podrá ceder, transferir ni delegar total o parcialmente los
derechos y obligaciones emergentes del presente Contrato a terceros, sin el
consentimiento previo, expreso y por escrito de la otra parte.

No obstante, el Proveedor podrá subcontratar parcialmente la prestación de servicios
con empresas del mismo grupo económico, manteniendo responsabilidad directa y
solidaria frente al Cliente por la actuación de dichos subcontratistas.


CLÁUSULA DÉCIMA: INDEMNIDAD

El Proveedor mantendrá indemne e indemnizará al Cliente de todo daño, perjuicio,
costo, gasto o reclamo de cualquier naturaleza que pudiera surgir como consecuencia
directa del incumplimiento de sus obligaciones contractuales, de la negligencia de su
personal, o del uso de software de terceros en la plataforma LOGFLOW Pro que
infringiera derechos de propiedad intelectual de terceros. Esta indemnidad incluye los
honorarios razonables de abogados en que incurriera el Cliente para su defensa.


CLÁUSULA UNDÉCIMA: JURISDICCIÓN Y LEY APLICABLE

Para todos los efectos emergentes del presente Contrato, las partes acuerdan someterse
exclusivamente a la jurisdicción de los Tribunales Ordinarios en lo Comercial de la
Ciudad Autónoma de Buenos Aires, renunciando expresamente a cualquier otro fuero o
jurisdicción que pudiera corresponderles, incluso el fuero federal. El presente
Contrato se rige íntegramente por las leyes de la República Argentina.


CLÁUSULA DUODÉCIMA: DISPOSICIONES GENERALES

12.1. El presente Contrato constituye el acuerdo completo entre las partes y reemplaza
cualquier negociación, propuesta o acuerdo previo, ya sea verbal o escrito.

12.2. Cualquier modificación deberá instrumentarse por escrito y ser firmada por
representantes debidamente autorizados de ambas partes para tener validez.

12.3. Si alguna cláusula fuera declarada inválida o inaplicable, las restantes
disposiciones continuarán en plena vigencia sin alteración.

12.4. Las notificaciones entre las partes deberán realizarse por medio fehaciente
(carta documento, acta notarial o correo electrónico con acuse de recibo) al domicilio
o dirección de correo que cada parte designe formalmente.


En prueba de conformidad, las partes suscriben dos (2) ejemplares de idéntico tenor y
a un solo efecto, en la Ciudad Autónoma de Buenos Aires, a los 15 días del mes de
mayo de 2025.


_______________________________       _______________________________
DATAFLOW SISTEMAS S.R.L.              DISTRIBUIDORA DEL NORTE S.A.
Ing. Alejandro Morales                Cra. Valentina Ramos
Gerente General                       Directora Comercial
CUIT 30-71892456-9                    CUIT 30-65124789-2
"""


# ── Generador de PDF ───────────────────────────────────────────────────────────

PAGE_W   = 595   # A4 ancho en puntos
PAGE_H   = 842   # A4 alto en puntos
MARGIN_X = 65    # margen lateral
MARGIN_Y = 65    # margen superior/inferior
TEXT_W   = PAGE_W - 2 * MARGIN_X   # 465 pt

BODY_FONT   = "helv"
BODY_SIZE   = 10
BODY_LEAD   = 14.5   # interlineado cuerpo

TITLE_SIZE  = 13
TITLE_LEAD  = 20

HEAD_SIZE   = 10.5
HEAD_LEAD   = 16


def is_section_header(line: str) -> bool:
    """Detecta encabezados de cláusula."""
    stripped = line.strip()
    return (
        stripped.startswith("CLÁUSULA ")
        or stripped.startswith("CONTRATO DE ")
    )


def is_document_title(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("CONTRATO DE ")


def render_contract(text: str, out_path: Path) -> int:
    """Renderiza el contrato como PDF multipágina. Devuelve el nro de páginas."""
    doc   = fitz.open()
    page  = doc.new_page(width=PAGE_W, height=PAGE_H)
    y     = MARGIN_Y
    pages = 1

    def new_page():
        nonlocal page, y, pages
        page  = doc.new_page(width=PAGE_W, height=PAGE_H)
        y     = MARGIN_Y
        pages += 1

    def write(line_text: str, size: float, lead: float,
              color: tuple = (0, 0, 0), x_offset: int = 0) -> None:
        nonlocal y
        if y + lead > PAGE_H - MARGIN_Y:
            new_page()
        page.insert_text(
            (MARGIN_X + x_offset, y),
            line_text,
            fontsize=size,
            fontname=BODY_FONT,
            color=color,
        )
        y += lead

    # Calcular ancho en caracteres aproximado para el wrapping
    # A 10pt Helvetica, ~0.55 pt/char → chars = TEXT_W / (size * 0.55)
    def char_width(size: float) -> int:
        return int(TEXT_W / (size * 0.558))

    for raw_line in text.split("\n"):
        stripped = raw_line.strip()

        # Línea vacía
        if not stripped:
            y += BODY_LEAD * 0.55
            if y > PAGE_H - MARGIN_Y - BODY_LEAD:
                new_page()
            continue

        # Título del documento (primera línea)
        if is_document_title(stripped):
            y += 4
            write(stripped, TITLE_SIZE, TITLE_LEAD, color=(0.05, 0.15, 0.35))
            y += 4
            continue

        # Encabezado de cláusula
        if is_section_header(stripped):
            y += 6
            write(stripped, HEAD_SIZE, HEAD_LEAD, color=(0.05, 0.15, 0.35))
            y += 2
            continue

        # Texto con sangría (ítems con letra o número)
        x_off = 0
        wrap_w = char_width(BODY_SIZE)
        if stripped.startswith(("a)", "b)", "c)", "d)", "e)")):
            x_off  = 12
            wrap_w = char_width(BODY_SIZE) - 2
        elif len(stripped) > 3 and stripped[0].isdigit() and stripped[1:3] in (".1", ".2", ".3", ".4"):
            x_off  = 0
            wrap_w = char_width(BODY_SIZE)

        # Wrap del texto
        wrapped = textwrap.wrap(stripped, width=wrap_w)
        if not wrapped:
            wrapped = [stripped]

        for wline in wrapped:
            write(wline, BODY_SIZE, BODY_LEAD, x_offset=x_off)

    doc.save(str(out_path))
    doc.close()
    return pages


def main():
    out_dir  = Path(__file__).parent
    out_path = out_dir / "contrato_proveedor_demo.pdf"

    print("Generando contrato demo...")
    pages = render_contract(CONTRATO, out_path)

    size_kb = out_path.stat().st_size / 1024
    print(f"✓  Guardado: {out_path}")
    print(f"   {pages} página(s)  ·  {size_kb:.1f} KB")
    print()
    print("Cláusulas de riesgo incluidas:")
    clausulas_riesgo = [
        ("TERCERA",   "Ajuste de precios (automático por IPC, sin notificación)"),
        ("CUARTA",    "Renovación automática + preaviso de 90 días para cancelar"),
        ("QUINTA",    "Exclusividad bidireccional (cliente y proveedor)"),
        ("SEXTA",     "Penalidades por incumplimiento y rescisión anticipada"),
        ("SÉPTIMA",   "Confidencialidad con vigencia de 5 años post-contrato"),
        ("OCTAVA",    "Limitación de responsabilidad (tope de 3 meses)"),
        ("NOVENA",    "Cesión del contrato"),
        ("DÉCIMA",    "Indemnidad"),
        ("UNDÉCIMA",  "Jurisdicción exclusiva CABA"),
    ]
    for num, desc in clausulas_riesgo:
        print(f"  · Cláusula {num}: {desc}")
    print()
    print(f"Para analizar:")
    print(f"  python src/main.py ejemplos/contrato_proveedor_demo.pdf")


if __name__ == "__main__":
    main()
