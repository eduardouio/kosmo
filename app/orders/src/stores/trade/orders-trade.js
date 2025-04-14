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
    },
});