import { defineStore } from 'pinia';
import { appConfig } from '@/AppConfig';
import axios from 'axios';

export const useInvoiceStore = defineStore('invoiceStore', {
    state: () => ({
        invoices: [],
        selectedInvoice: null,
        isEditing: false
    }),
    actions: {
        async loadInvoices(baseStore) {
            if (this.invoices.length > 0) {
                baseStore.stagesLoaded++;
                return;
            }
            try {
                const response = await axios.get(appConfig.urlInvoices, {
                    headers: appConfig.headers
                });
                this.invoices = response.data;
                baseStore.stagesLoaded++;
            } catch (error) {
                console.error('Error al cargar las facturas:', error);
                alert(`Hubo un error al cargar las facturas: ${error.message}`);
            }
        },

        async saveInvoice(invoice) {
            try {
                const response = await axios.post(
                    this.isEditing ? appConfig.urlUpdateInvoice : appConfig.urlCreateInvoice,
                    invoice,
                    { headers: appConfig.headers }
                );
                if (!this.isEditing) {
                    this.invoices.unshift(response.data);
                }
                return response.data;
            } catch (error) {
                console.error('Error al guardar la factura:', error);
                alert(`Hubo un error al guardar la factura: ${error.message}`);
                return null;
            }
        },

        async getInvoiceById(id) {
            try {
                const response = await axios.get(
                    appConfig.urlInvoice.replace('{id}', id),
                    { headers: appConfig.headers }
                );
                this.selectedInvoice = response.data;
                return response.data;
            } catch (error) {
                console.error('Error al obtener la factura:', error);
                alert(`Hubo un error al obtener la factura: ${error.message}`);
                return null;
            }
        },

        initNewInvoice() {
            this.selectedInvoice = {
                partner: null,
                type_document: 'FAC_VENTA',
                num_invoice: '',
                date: new Date().toISOString().split('T')[0],
                due_date: null,
                delivery_date: null,
                awb: '',
                dae_export: '',
                hawb: '',
                cargo_agency: '',
                weight: 0,
                status: 'PENDIENTE',
                order_details: [],
                total_price: 0,
                total_margin: 0,
                qb_total: 0,
                hb_total: 0,
                fb_total: 0,
                total_pieces: 0,
                tot_stem_flower: 0
            };
            this.isEditing = false;
        },

        calculateTotals() {
            if (!this.selectedInvoice) return;

            let totalPrice = 0;
            let totalMargin = 0;
            let qbTotal = 0;
            let hbTotal = 0;
            let fbTotal = 0;
            let totalStems = 0;

            this.selectedInvoice.order_details.forEach(detail => {
                if (detail.box_model === 'QB') qbTotal += detail.quantity;
                if (detail.box_model === 'HB') hbTotal += detail.quantity;

                detail.box_items.forEach(item => {
                    const itemTotal = item.qty_stem_flower * item.stem_cost_price * detail.quantity;
                    const itemMargin = item.qty_stem_flower * item.profit_margin * detail.quantity;
                    totalPrice += itemTotal;
                    totalMargin += itemMargin;
                    totalStems += item.qty_stem_flower * detail.quantity;
                });
            });

            this.selectedInvoice.total_price = totalPrice;
            this.selectedInvoice.total_margin = totalMargin;
            this.selectedInvoice.tot_stem_flower = totalStems;
            this.selectedInvoice.qb_total = qbTotal;
            this.selectedInvoice.hb_total = hbTotal;
            this.selectedInvoice.fb_total = ((qbTotal / 2) + hbTotal) / 2;
        },

        addBoxToInvoice(box) {
            if (!this.selectedInvoice) return;
            this.selectedInvoice.order_details.push({...box});
            this.calculateTotals();
        },

        removeBoxFromInvoice(index) {
            if (!this.selectedInvoice) return;
            this.selectedInvoice.order_details.splice(index, 1);
            this.calculateTotals();
        },

        formatNumber(num) {
            if (num === null || num === undefined) return '0.00';
            const base_num = parseFloat(num);
            if (isNaN(base_num)) return '0.00';
            const parts = base_num.toString().split(".");
            const integerPart = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
            const decimalPart = parts.length > 1 ? "." + parts[1].slice(0, 2) : ".00";
            return integerPart + decimalPart;
        }
    }
});