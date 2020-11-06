from io import BytesIO
from reportlab.lib.styles import ParagraphStyle, TA_CENTER
from reportlab.lib.units import inch, mm
from reportlab.lib import colors
from reportlab.platypus import (
    Table,
    SimpleDocTemplate,
    Spacer,
    TableStyle,
    Paragraph)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from .models import Proyecto, Fase, SolicitudCambioEstado, RoturaLineaBase


class ReporteProyecto(object):

    def __init__(self):
        self.buf = BytesIO()

    def run(self, proyectoid, fases, fecha_ini, fecha_fin):
        self.doc = SimpleDocTemplate(self.buf)
        self.story = []
        proyecto = Proyecto.objects.get(pk=proyectoid)
        self.titulo("Reporte Proyecto : " + proyecto.nombre)
        self.encabezado("Items del Proyecto en Estado 'Pendiente' y 'Desarrollo'")
        self.tabla_items_proyecto(proyecto)

        try:
            for faseid in fases:
                fase = Fase.objects.get(pk=faseid.id)
                self.encabezado("Items de la fase: " + fase.nombre)
                self.crearTabla(fase.items.all())
        except:
            self.encabezado("No ha seleccionado fases")

        self.solicitudes(fecha_ini, fecha_fin)
        self.solicitudes_LB(fecha_ini, fecha_fin)
        self.doc.build(self.story, onFirstPage=self.numeroPagina,
                       onLaterPages=self.numeroPagina)
        pdf = self.buf.getvalue()
        self.buf.close()
        return pdf

    def titulo(self, nombre):

        p = Paragraph(nombre, self.estiloPC())
        self.story.append(p)
        self.story.append(Spacer(1, 0.5 * inch))

    def encabezado(self, nombre):
        p = Paragraph(nombre, self.estiloPC())
        self.story.append(p)
        self.story.append(Spacer(1, 0.1 * inch))



    def crearTabla(self, items):
        data = [["Id", "Nombre", "Estado"]] \
               + [[x.id, x.nombre, x.estado]
                  for x in items]
        style = TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ])

        t = Table(data)
        t.setStyle(style)
        self.story.append(t)
        self.story.append(Spacer(1, 0.5 * inch))

    def tabla_items_proyecto(self, proyecto):
        items = []
        for f in proyecto.fases.all():
            for i in f.items.all():
                if i.estado == "en desarrollo" or i.estado == "pendiente de aprobacion":
                    items.append(i)

        data = [["Id", "Nombre", "Estado"]] \
               + [[x.id, x.nombre, x.estado]
                  for x in items]

        style = TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ])

        t = Table(data)
        t.setStyle(style)
        self.story.append(t)
        self.story.append(Spacer(1, 0.5 * inch))

    def solicitudes(self, fecha_ini, fecha_fin):
        solicitudes = SolicitudCambioEstado.objects.all()
        solicitud_rango = []
        for s in solicitudes:
            if s.justificacion >= fecha_ini and s.justificacion <= fecha_fin:
                solicitud_rango.append(s)

        data = [["SolicitudId", "Fecha",]] \
               + [[x.id, x.justificacion,]
                  for x in solicitud_rango]
        style = TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ])

        t = Table(data)
        t.setStyle(style)
        self.story.append(t)
        self.story.append(Spacer(1, 0.5 * inch))

    def solicitudes_LB(self, fecha_ini, fecha_fin):
        solicitudes = RoturaLineaBase.objects.all()
        solicitud_rango = []
        for s in solicitudes:
            if s.fecha >= fecha_ini and s.fecha <= fecha_fin:
                solicitud_rango.append(s)

        data = [["SolicitudIdRotura", "Fecha",]] \
               + [[x.id, x.fecha,]
                  for x in solicitud_rango]
        style = TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ])

        t = Table(data)
        t.setStyle(style)
        self.story.append(t)
        self.story.append(Spacer(1, 0.5 * inch))
    def estiloPC(self):
        return ParagraphStyle(name="centrado", alignment=TA_CENTER)

    def numeroPagina(self, canvas, doc):
        num = canvas.getPageNumber()
        text = "Pagina %s" % num
        canvas.drawRightString(200 * mm, 20 * mm, text)
