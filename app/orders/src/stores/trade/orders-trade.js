import { defineStore } from 'pinia';
import { appConfig } from '@/AppConfig';
import axios from 'axios';

export const useInvoiceStore = defineStore('invoiceStore', {
    state: () => ({
        invoices: [],
        selectedInvoice: null,
        selectedSupplier: null,
        showViews: {
            listInvoices: true,
            singleInvoice: false,
        },
        orderLines: [], // Estado para las líneas de pedido
    }),
    actions: {
        async loadInvoices() {
            if (this.invoices.length > 0) {
                return;
            }
            try {
                const response = await axios.get(appConfig.urlAllInvoices, { headers: appConfig.headers });
                this.invoices = response.data;
            } catch (error) {
                console.error('Error al cargar las facturas:', error);
                alert(`Hubo un error al cargar las facturas: ${error.message}`);
            }
        },

        normalizeLine(line) {
            if (line.box_items) return line;
            return {
                quantity: line.cajas || 1,
                box_model: line.tipo || 'HB',
                box_items: [],
            };
        },

        addBoxItem(lineIndex, newBoxItem) {
            const line = this.orderLines[lineIndex];
            if (!newBoxItem.product) return;
            line.box_items.push({ ...newBoxItem });
        },

        removeBoxItem(lineIndex, itemIndex) {
            const line = this.orderLines[lineIndex];
            line.box_items.splice(itemIndex, 1);
        },

        calculateTotalLine(lineIndex) {
            const line = this.orderLines[lineIndex];
            return line.box_items.reduce((acc, p) => acc + (p.qty_stem_flower || 0) * (p.stem_cost_price || 0), 0);
        },
    },
});