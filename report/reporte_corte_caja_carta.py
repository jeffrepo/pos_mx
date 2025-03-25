from odoo import api, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
import pytz
import ast
import logging

class ReporteCorteCajaCarta(models.AbstractModel):
    _name = 'report.pos_mx.reporte_corte_caja_carta'

    nombre_reporte=''

    def sesiones(self, docs):
        listado_productos = []
        listado_totales = []
        cantidad = 0
        elementos = 0
        elementos1 = 0
        precio_unitario = 0
        descuento = 0
        descuento_lineas =0
        total_suma_descuento = 0
        total_suma_descuento_iva = 0
        total_columnas_descuento_iva = 0
        impuestos = 0
        linea_iva = 0
        porcentaje = 0
        total=0
        lineas = 0
        iva_venta = 0
        calculo_descuento_iva = 0
        calculo_precio_cantidad=0
        calculo_precio_cantidad_iva=0
        ventas_porciento_iva = 0
        ventas_porciento_sin_iva = 0
        total_columnas_ventas_sin_iva = 0
        total_columnas_ventas_iva = 0
        total_columnas_descuento_sin_iva = 0
        total_columna_descuento = 0
        total_columna_iva = 0
        total_columna_total = 0
        total_ventas_mostrador = 0
        suma_iva = 0
        importe = 0
        folios = []
        pedidos_no_facturados = []
        pedidos_facturados = []
        listado_referencia_facturas = []
        metodos_pago = {}
        productos = docs.order_ids.filtered(lambda order: order.invalido is False).lines
        pago_efectivo = 0
        contador_efectivo = 0
        ventas = docs.order_ids.filtered(lambda order: order.invalido is False)
        facturas = ventas.account_move
        numero_recibo = []
        importe_descuento = 0

        # DEV JEFFREPO

        dic_formas_pago = {'Tarjeta credito': 'TC', 'Efectivo': 'E', 'Tarjeta debito': 'TD', '​Transferencia': 'T', 'Tarjeta crédito': 'TC',}
        ventas_mostrador = {'folios': False, 'importe': 0.00, 'descuento': 0.00, 'total': 0}
        total_ventas_mostrador = 0.00
        ventas_sesion = {}
        totales_ventas_sesion = {'ventas_sin_iva': 0, 'descuento_sin_iva': 0, 'ventas_iva': 0, 'descuento_iva': 0, 'descuento': 0, 'iva': 0, 'total': 0}
        resumen_facturas_expedidas = {'serie': '', 'folios': '', 'venta_sin_iva': 0.00, 'venta_iva': 0.00, 'iva': 0.00, 'total': 0.00}
        resumen_factura_global = {'serie': '', 'folios': '', 'venta_sin_iva': 0.00, 'venta_iva': 0.00, 'iva': 0.00, 'total': 0.00}
        total_facturas_expedidas = 0.00
        detalle_facturas_expedidas = {}
        total_detalle_facturas_expedidas = 0.00
        diferencia = 0.00
        apertura_efectivo = docs.cash_register_balance_start
        total_retiro_efectivo = 0.00
        total_retiro_efectivo_sesion_previa = 0.00
        venta_efectivo = 0.00
        cierre_efectivo = docs.cash_register_balance_end_real
        retiro_corte_previo = {}

        #SOLO OBTENEMOS INFORMACION DE PEDIDOS FACTURADOS
        for venta in ventas:
            venta_nombre = venta.name



            if venta_nombre not in ventas_sesion:
                fp = False
                for linea_pago in venta.payment_ids:
                    if linea_pago.payment_method_id.name == 'Efectivo':
                        venta_efectivo += linea_pago.amount
                if len(venta.payment_ids) == 1:
                    metodo_pago = venta.payment_ids.payment_method_id.name
                    if metodo_pago not in dic_formas_pago:
                        dic_formas_pago[metodo_pago] = "T"
                    fp = dic_formas_pago[metodo_pago]
                else:
                    fp = 'M'
                # serie = venta_nombre.split("/", 1)[0]
                # folio = venta_nombre.split("/", 1)[1]
                ventas_sesion[venta_nombre] = {'venta': venta_nombre,'ventas_sin_iva': 0, 'descuento_sin_iva': 0, 'ventas_iva': 0, 'descuento_iva': 0, 'descuento': 0, 'iva': 0, 'total': 0, 'fp': fp, 'e':0}

            for linea in venta.lines:
                ventas_sin_iva = 0.00
                descuento_sin_iva = 0.00
                ventas_iva = 0.00
                descuento_iva = 0.00
                descuento = 0.00
                iva = 0.00
                total = 0.00
                descuento_sin_impuesto = False
                if linea.program_id:
                    ventas_sesion[venta_nombre]['descuento_sin_iva'] = 0.00
                    domain = linea.program_id.rule_products_domain
                    logging.warning(domain)
                    domain = ast.literal_eval(domain)
                    producto_ids = self.env['product.product'].search(domain)
                    if len(producto_ids[0].taxes_id) > 1:
                        descuento_sin_impuesto = True
                        descuento_sin_iva = linea.price_subtotal_incl * -1
                        descuento += descuento_sin_iva
                    else:
                        if producto_ids[0].taxes_id.name == 'IVA(0%) VENTAS':
                            descuento_sin_impuesto = True
                            descuento_sin_iva = linea.price_subtotal_incl * -1
                            descuento += descuento_sin_iva
                        else:
                            descuento_iva = linea.price_subtotal_incl * -1
                            descuento += descuento_iva
                else:
                    if linea.price_subtotal == linea.price_subtotal_incl:
                        ventas_sin_iva = linea.price_subtotal_incl
                        total = ventas_sin_iva - descuento_sin_iva
                        # ventas_sesion[venta_nombre]['ventas_sin_iva'] = ventas_sin_iva

                    else:
                        ventas_iva = linea.price_subtotal
                        iva = linea.price_subtotal_incl - ventas_iva
                        total = linea.price_subtotal_incl + descuento_iva
                        # ventas_sesion[venta_nombre]['ventas_iva'] = linea.price_subtotal_incl
                        # ventas_sesion[venta_nombre]['iva'] = iva


                total = total - descuento
                ventas_sesion[venta_nombre]['ventas_sin_iva'] += ventas_sin_iva
                ventas_sesion[venta_nombre]['descuento_sin_iva'] += descuento_sin_iva
                ventas_sesion[venta_nombre]['ventas_iva'] += ventas_iva
                ventas_sesion[venta_nombre]['descuento_iva'] += descuento_iva
                ventas_sesion[venta_nombre]['descuento'] += descuento
                ventas_sesion[venta_nombre]['iva'] += iva
                ventas_sesion[venta_nombre]['total'] += total

                ventas_mostrador['importe'] += ventas_sin_iva+ventas_iva+iva
                ventas_mostrador['descuento'] += descuento
                ventas_mostrador['total'] += total

                totales_ventas_sesion['ventas_sin_iva'] += ventas_sin_iva
                totales_ventas_sesion['descuento_sin_iva'] += descuento_sin_iva
                totales_ventas_sesion['ventas_iva'] += ventas_iva
                totales_ventas_sesion['descuento_iva'] += descuento_iva
                totales_ventas_sesion['descuento'] += descuento
                totales_ventas_sesion['iva'] += iva
                totales_ventas_sesion['total'] += total

                if venta.state == 'invoiced':
                    if venta_nombre not in detalle_facturas_expedidas:
                        detalle_facturas_expedidas[venta_nombre] = {'venta': venta_nombre,'ventas_sin_iva': 0, 'descuento_sin_iva': 0, 'ventas_iva': 0, 'descuento_iva': 0, 'descuento': 0, 'iva': 0, 'total': 0, 'fp': fp, 'e':0}
                # resumen de facturas expedidias

                    resumen_facturas_expedidas['venta_sin_iva'] += ventas_sin_iva
                    resumen_facturas_expedidas['venta_iva'] += ventas_iva
                    resumen_facturas_expedidas['iva'] += iva
                    resumen_facturas_expedidas['total'] += total

                    #Detalle facturas expedidas
                    detalle_facturas_expedidas[venta_nombre]['ventas_sin_iva'] += ventas_sin_iva
                    detalle_facturas_expedidas[venta_nombre]['ventas_iva'] += ventas_iva
                    detalle_facturas_expedidas[venta_nombre]['iva'] += iva
                    detalle_facturas_expedidas[venta_nombre]['total'] += total
                    total_detalle_facturas_expedidas += total


        for referencia in ventas:
            # folio = referencia.name.split("/", 1)[1]
            # serie = referencia.name.split("/", 1)[0]
            folios.append(referencia.name)
            folios.sort()
            total_suma_subtotal = 0
            calculo_precio_sin_iva = 0
            sumas_descuento = 0
            precio_original_iva = 0
            suma_descuento_iva = 0
            suma_descuento_sin_iva = 0

            if referencia.state != "invoiced":
                pedidos_no_facturados.append(referencia.id)
            else:
                pedidos_facturados.append(referencia.id)

            listado_productos.append({'venta': referencia.name,'ventas_sin_iva': 0, 'descuento_sin_iva': 0, 'ventas_iva': 0, 'descuento_iva': 0, 'descuento': 0, 'iva': 0, 'total': 0, 'fp': 0, 'e':0})

            iva_venta = referencia.amount_tax
            total = referencia.amount_total
            suma_iva = round(iva_venta, 2)
            for lineas in referencia.lines:
                linea_iva = lineas.tax_ids_after_fiscal_position
                cantidad = lineas.qty
                precio_unitario = lineas.price_unit
                descuento_lineas = lineas.discount
                porcentaje = descuento_lineas/100

                if linea_iva.id != False:
                    calculo_precio_cantidad_iva = (cantidad * precio_unitario) * porcentaje
                    suma_descuento_iva += calculo_precio_cantidad_iva
                    precio_original_iva += cantidad * precio_unitario

                if linea_iva.id == False:
                    calculo_precio_cantidad = (cantidad * precio_unitario)*porcentaje
                    suma_descuento_sin_iva += calculo_precio_cantidad
                    calculo_precio_sin_iva += cantidad * precio_unitario

            total_suma_descuento_iva = suma_descuento_iva
            total_suma_descuento = suma_descuento_sin_iva
            sumas_descuento = total_suma_descuento_iva + total_suma_descuento
            ventas_porciento_iva = precio_original_iva
            ventas_porciento_sin_iva = calculo_precio_sin_iva
            acceder = listado_productos[elementos]
            total_columnas_ventas_sin_iva += round(ventas_porciento_sin_iva, 2)
            total_columnas_ventas_iva += round(ventas_porciento_iva, 2)
            total_columnas_descuento_iva += round(total_suma_descuento_iva, 2)
            total_columna_descuento += round(sumas_descuento, 2)
            total_columna_iva += self.env.company.currency_id.round(suma_iva)
            total_columnas_descuento_sin_iva += round(total_suma_descuento, 2)
            total_columna_total += total
            if referencia.amount_total <= 0:
                numero_recibo.append(referencia.pos_reference)

            importe = round(total_columnas_ventas_sin_iva + total_columnas_ventas_iva + total_columna_iva, 2)
            total_ventas_mostrador = round(importe - total_columna_descuento, 2)

            importe1 = 0
            total_pagos = 0
            total_importe_pagos = 0

            for lineas_pagos in referencia.payment_ids:

                inicial = lineas_pagos.payment_method_id.name.split(' ', 0)[0]
                # inicial1 = inicial[0]
                inicial1 = lineas_pagos.payment_method_id.journal_id.code

                if lineas_pagos.payment_method_id.id not in metodos_pago:
                    metodos_pago[lineas_pagos.payment_method_id.id]={'tipo': lineas_pagos.payment_method_id.name, 'importe': 0, 'id': lineas_pagos.payment_method_id.id, 'conteo': 0}


                if lineas_pagos.payment_method_id.id == metodos_pago[lineas_pagos.payment_method_id.id]['id']:
                    importe1 = lineas_pagos.amount
                    metodos_pago[lineas_pagos.payment_method_id.id]['conteo'] += 1

                metodos_pago[lineas_pagos.payment_method_id.id]['importe'] += importe1


            for desc in acceder:
                acceder['ventas_sin_iva'] = ventas_porciento_sin_iva
                acceder['ventas_iva'] = ventas_porciento_iva
                acceder['total'] = total
                acceder['descuento_sin_iva'] = total_suma_descuento
                acceder['descuento_iva'] = total_suma_descuento_iva
                acceder['descuento'] = sumas_descuento
                acceder['iva'] = iva_venta
                acceder['fp'] = inicial1
            elementos +=1

        for  metod_pago in metodos_pago:
            total_pagos += metodos_pago[metod_pago]['importe']


        logging.warning(metodos_pago)

        # retiros = docs.retiros_ids

        listado_retiros = []
        retiros = self.env['pos_cash_limit.retiros_efectivo'].search([('sesion_id', '=', docs.id)], order='fecha_hora asc')
        logging.warning(retiros)
        distint = 0
        for retiro in retiros:
            distint += 1
            listado_retiros.append({'n_retiro': retiro.name, 'distintivo': retiro.motivo, 'fecha_hora': retiro.fecha_hora, 'cantidad': retiro.total, 'cajero': retiro.cajero })
            total_retiro_efectivo += retiro.total

        logging.warning(listado_retiros)
        total_retiros = 0
        for list_ret in listado_retiros:
            total_retiros += list_ret['cantidad']
            
        logging.warning('Los folios')
        logging.warning(folios)
        folios_concatenados = folios[0] + ' - ' + folios[-1]


        retiros_corte_previa = []
        retiros = self.env['pos_cash_limit.retiros_efectivo'].search([('sesion_id', '!=', docs.id),('entregado','=', False),('tienda_id','=',docs.config_id.id)], order='fecha_hora asc')
        logging.warning(retiros)
        distint = 0
        for retiro in retiros:
            distint += 1
            retiros_corte_previa.append({'n_retiro': retiro.name, 'distintivo': retiro.motivo, 'fecha_hora': retiro.fecha_hora, 'cantidad': retiro.total, 'cajero': retiro.cajero })
            total_retiro_efectivo_sesion_previa += retiro.total

        logging.warning(retiros_corte_previa)
        total_retiros_noentregados = 0
        for list_ret in retiros_corte_previa:
            total_retiros_noentregados += list_ret['cantidad']
        folios_concatenados = folios[0] + ' - ' + folios[-1]


        for referencia1 in facturas:
            listado_referencia_facturas.append(referencia1.ref)

        facturas_rectificativa = self.env['account.move'].search([('move_type' , '=', 'out_refund'), ('invoice_origin', 'in', listado_referencia_facturas)])
        listado_notas_credito = []
        nota_credito = 0
        total_descuento_credito = 0
        descuento_credito = 0
        total_nota_credito = 0
        total_desglose_venta = 0
        suma_impuesto = 0
        suma_precio_sin_descuento = 0
        suma_precios_descuento = 0
        total_importe_credito = 0
        importe_descuento = 0
        for fac_rec in facturas_rectificativa:
            listado_notas_credito.append({'folio_credito': fac_rec.invoice_origin, 'total': fac_rec.amount_total})
            nota_credito += fac_rec.amount_total

            calculo_descuento = 0
            for lineas_credito in fac_rec.invoice_line_ids:
                lineas_descuento = lineas_credito.discount
                suma_impuesto += (lineas_credito.price_total - lineas_credito.price_subtotal)
                if lineas_descuento != False:
                    precio_descuento = lineas_credito.quantity * lineas_credito.price_unit
                    calculo_descuento = precio_descuento * (lineas_credito.discount / 100)
                    logging.warning("calculo_descuento")
                    logging.warning(calculo_descuento)
                    suma_precios_descuento += precio_descuento

                else:
                    precio_sin_descuento = lineas_credito.quantity * lineas_credito.price_unit
                    suma_precio_sin_descuento += precio_sin_descuento

            descuento_credito += calculo_descuento
            importe_descuento = (suma_precios_descuento + suma_precio_sin_descuento) + suma_impuesto

        total_nota_credito = round(nota_credito, 2)
        total_importe_credito = importe_descuento
        total_descuento_credito = descuento_credito
        total_desglose_venta = round(total_ventas_mostrador - total_nota_credito, 2)

        facturas_globales = self.env['account.move'].search([('pos_order_ids', 'in', pedidos_no_facturados)])
        factura_expedida = self.env['account.move'].search([('pos_order_ids', 'in', pedidos_facturados)])
        logging.warning("factura_expedida")
        logging.warning(factura_expedida)

        listado_facturas_expedidas=[]
        total_factura_expedida = 0
        iva_factura_expedida = 0
        suma_ventas_sin_iva = 0
        suma_ventas_iva = 0
        suma_columna_ventas_expedidas=0
        suma_columna_ventas_iva_expedidas=0
        suma_iva_expedido = 0
        suma_columna_iva_expedidas = 0
        suma_total_expedido = 0
        suma_columna_total_expedido = 0
        for fex in factura_expedida:
            total_factura_expedida = fex.amount_total
            producto_iva1 = 0
            producto_sin_iva1 = 0
            # folio_expedido = fex.ref
            # serie_expedido = fex.ref
            for lineas in fex.invoice_line_ids:
                if lineas.tax_ids.id != False:
                    producto_iva1 += lineas.price_subtotal
                else:
                    producto_sin_iva1 += lineas.price_subtotal
            suma_ventas_sin_iva += producto_sin_iva1
            suma_ventas_iva += producto_iva1
            iva_factura_expedida = round(fex.amount_total - fex.amount_untaxed, 2)
            suma_iva_expedido += round(iva_factura_expedida, 2)
            suma_total_expedido += round(total_factura_expedida, 2)
            listado_facturas_expedidas.append({
                # 'serie_expedido': serie_expedido,
                # 'folio_expedido': folio_expedido,
                'pedido': fex.ref,
                'producto_iva1': producto_iva1,
                'producto_sin_iva1': producto_sin_iva1,
                'iva_factura_expedida': iva_factura_expedida,
                'total_factura_expedida': total_factura_expedida,
            })

        suma_columna_ventas_expedidas = suma_ventas_sin_iva
        suma_columna_ventas_iva_expedidas = suma_ventas_iva
        suma_columna_iva_expedidas = round(suma_iva_expedido, 2)
        suma_columna_total_expedido = round(suma_total_expedido, 2)

        listado_facturas_globales = []
        total_factura_global = 0
        producto_iva = 0
        producto_sin_iva = 0
        iva_factura_global = 0
        for fg in facturas_globales:
            total_factura_global = fg.amount_total
            for lineas in fg.invoice_line_ids:
                if lineas.tax_ids.id != False:
                    producto_iva += lineas.price_subtotal
                else:
                    producto_sin_iva += lineas.price_subtotal
            iva_factura_global = round(fg.amount_total - fg.amount_untaxed, 2)

        listado_facturas_globales.append({
        'producto_sin_iva': producto_sin_iva,
        'producto_iva': producto_iva,
        'iva_factura_global': iva_factura_global,
        'total': total_factura_global})

        suma_columna_total_facturas_totales = 0
        suma_columna_total_facturas_totales = suma_columna_total_expedido + total_factura_global

        listado_pedidos = self.env['pos.order'].search([('session_id','=', docs.id),('amount_total', '<', 0 )])

        logging.warning("listado_pedidos")
        logging.warning(listado_pedidos)

        listado_cancelados = []
        folios1= []
        serie1 = []

        for list_pedidos in listado_pedidos:
            if len(list_pedidos.refunded_order_ids) > 0:
                listado_cancelados.append({'venta': list_pedidos.name,'importe': list_pedidos.refunded_order_ids.amount_total})


        total_cancelado = 0
        for lst_cancelados in listado_cancelados:
            total_cancelado += lst_cancelados['importe']

        listado_totales.append({
         'total_columnas_ventas_sin_iva': total_columnas_ventas_sin_iva,
         'total_columnas_descuento_sin_iva': total_columnas_descuento_sin_iva,
         'total_columnas_ventas_iva': total_columnas_ventas_iva,
         'total_columnas_descuento_iva': total_columnas_descuento_iva,
         'total_columna_descuento': total_columna_descuento,
         'total_columna_iva': total_columna_iva,
         'total_columna_total':total_columna_total,
         'importe': importe,
         'total_ventas_mostrador': total_ventas_mostrador,
         'folios_concatenados': folios_concatenados,
         'total_nota_credito': total_nota_credito,
         'total_descuento_credito': total_descuento_credito,
         'total_importe_credito': total_importe_credito,
         'total_desglose_venta': total_desglose_venta,
         'suma_columna_ventas_expedidas': suma_columna_ventas_expedidas,
         'suma_columna_ventas_iva_expedidas': suma_columna_ventas_iva_expedidas,
         'suma_columna_iva_expedidas': suma_columna_iva_expedidas,
         'suma_columna_total_expedido': suma_columna_total_expedido,
         'suma_columna_total_facturas_totales': suma_columna_total_facturas_totales,
         'contador_efectivo': contador_efectivo,
         'total_pago': total_pagos,
         'total_retiros': total_retiros,
         'total_cancelado': total_cancelado
         })


        total_ventas_mostrador = ventas_mostrador['total']
        total_facturas_expedidas = resumen_facturas_expedidas['total'] + resumen_factura_global['total']

        diferencia = apertura_efectivo + total_retiro_efectivo - venta_efectivo - cierre_efectivo

        return {
        'listado_productos': listado_productos,
        'listado_totales': listado_totales,
        'listado_notas_credito': listado_notas_credito,
        'listado_facturas_expedidas': listado_facturas_expedidas,
        'listado_facturas_globales': listado_facturas_globales,
        'metodos_pago': metodos_pago,
        'listado_retiros': listado_retiros,
        'listado_cancelados': listado_cancelados,
        'ventas_mostrador': ventas_mostrador,
        'total_ventas_mostrador': total_ventas_mostrador,
        'ventas_sesion': ventas_sesion,
        'totales_ventas_sesion': totales_ventas_sesion,
        'folios_concatenados': folios_concatenados,
        'resumen_facturas_expedidas': resumen_facturas_expedidas,
        'resumen_factura_global': resumen_factura_global,
        'total_facturas_expedidas': total_facturas_expedidas,
        'detalle_facturas_expedidas': detalle_facturas_expedidas,
        'total_detalle_facturas_expedidas': total_detalle_facturas_expedidas,
        'diferencia': diferencia,
        'retiros_corte_previa': retiros_corte_previa,
        }


    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['pos.session'].browse(docids)
        timezone = pytz.timezone(self._context.get('tz') or self.env.user.tz or 'UTC')
        fecha_hoy = datetime.now().astimezone(timezone).strftime('%H')
        estado_sesion = False
        for sesion in docs:
            estado_sesion = sesion.state
        if int(fecha_hoy) >= 13 and estado_sesion != "closed":
            raise ValidationError("No tiene permitido generar corte de caja, favor de cerrar sesión")
        return {
            'doc_ids': docids,
            'doc_model': 'pos.session',
            'docs': docs,
            'sesiones': self.sesiones
        }
