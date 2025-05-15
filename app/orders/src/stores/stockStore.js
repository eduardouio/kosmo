import { defineStore } from 'pinia';
import { appConfig } from '@/AppConfig';
import axios from 'axios';

export const useStockStore = defineStore('stockStore', {
    state: () => ({
        stock: [],
        stockText: 'Sin Seleccion',
        orders: [],
        stockDay: null,
        suppliers: [],
        selectedCustomer: null,
        colors: [],
        lengths: [],
        boxModels: [],
    }),
    actions: {
        async LoadOrders(baseStore) {
            try {
                const response = await axios.get(appConfig.urlOrdersByStock + '?type=purchase');
                this.orders = response.data;
                baseStore.stagesLoaded++;
            } catch (error) {
                console.error('Error al cargar las órdenes:', error);
                alert(`Hubo un error al cargar las órdenes: ${error.message}`);
            }
        },
        async getStock(baseStore) {
            try {
                const response = await axios.get(appConfig.urlDispo);
                const data = response.data;
                if (data.error) {
                    alert(data.error);
                    return;
                }
                this.stock = data.stock;
                this.orders = data.orders;
                this.stockDay = data.stockDay;
                this.extractSuppliers();
                this.extractColors();
                this.extractLengths();
                this.extractBoxModels();
                baseStore.stagesLoaded++;
                return true;
            } catch (error) {
                console.error('Error al obtener el stock:', error);
                return false;
            }
        },
        async addBoxItem(boxItem) {
            try {
                const response = await axios.post(appConfig.urlAddBoxItem, boxItem, {
                    headers: appConfig.headers
                });
                const data = response.data;
                boxItem.id = data.box_item.id;
                this.stock.forEach(item => {
                    if (item.stock_detail_id === boxItem.stock_detail_id) {
                        item.box_items.push(boxItem);
                    }
                });
                return data;
            } catch (error) {
                console.error('Error al agregar el item a la caja:', error);
                alert(`Hubo un error al agregar el item a la caja: ${error.message}`);
                return null;
            }
        },
        async updateStockDetail(boxes, boxDelete = false) {
            try {
                const response = await axios.post(appConfig.urlUpdateStockDetail, boxes, {
                    headers: appConfig.headers
                });
                const data = response.data;
                if (boxDelete) {
                    this.deleteBoxItem(boxes[0]);
                }
                return data;
            } catch (error) {
                console.error('Error al actualizar el stock:', error);
                alert(`Hubo un error al actualizar el stock: ${error.message}`);
                return null;
            }
        },
        deleteBoxItem(boxItem) {
            this.stock.forEach(item => {
                item.box_items = item.box_items.filter(subItem => subItem.id !== boxItem.id);
            });
        },
        extractColors() {
            let colors = this.stock.map(item => item.box_items).flat().map(item => item.product_colors)
                .flat().filter(
                    (value, index, self) => self.findIndex(t => (t === value)) === index
                );
            this.colors = colors.map(item => ({ name: item, is_selected: true }));
        },
        extractSuppliers() {
            let suppliers = this.stock.map(item => item.partner).filter(
                (value, index, self) => self.findIndex(t => (t.id === value.id)) === index
            );
            this.suppliers = suppliers.map(item => ({ ...item, is_selected: true }));
        },
        extractLengths() {
            let lengths = this.stock.map(item => item.box_items).flat().map(item => item.length)
                .filter(
                    (value, index, self) => self.findIndex(t => (t === value)) === index
                );
            this.lengths = lengths.map(item => ({ name: item, is_selected: true }));
            this.lengths.sort((a, b) => a.name - b.name);
        },
        extractBoxModels() {
            let models = this.stock
                .map(item => item.box_model)
                .filter((value, index, self) => self.indexOf(value) === index);
            this.boxModels = models.map(m => ({ name: m, is_selected: true }));
        },
        filterStock(querySearch) {
            if (!querySearch) {
                this.filterCategories(); // Aplica los filtros existentes
                return;
            }

            this.stock.forEach(item => {
                if (item.is_visible) { // Solo aplica el buscador a los registros visibles
                    item.is_visible = item.box_items.some(subItem =>
                        subItem.product_variety.toLowerCase().includes(querySearch.toLowerCase())
                    );
                }
            });
        },
        selectAll(option) {
            this.stock.forEach(item => {
                if (item.is_visible === true) {
                    item.is_selected = option;
                }
            });
            this.stockToText();
        },
        filterCategories() {
            const selectedSuppliers = this.suppliers.filter(item => item.is_selected).map(item => item.id);
            const selectedColors = this.colors.filter(item => item.is_selected).map(item => item.name);
            const selectedLengths = this.lengths.filter(item => item.is_selected).map(item => item.name);
            const selectedBoxModels = this.boxModels.filter(bm => bm.is_selected).map(bm => bm.name);

            if (selectedColors.length === 0 || selectedSuppliers.length === 0 || selectedLengths.length === 0) {
                this.stock.forEach(item => item.is_visible = false);
                return;
            }
            this.stock.forEach(item => {
                if (selectedSuppliers.includes(item.partner.id)) {
                    item.is_visible = item.box_items.some(subItem =>
                        subItem.product_colors.some(color => selectedColors.includes(color)) &&
                        selectedLengths.includes(subItem.length)
                    );
                } else {
                    item.is_visible = false;
                }
                if (!selectedBoxModels.includes(item.box_model)) {
                    item.is_visible = false;
                }
            });
        },
        async deleteSelected() {
            let toDelete = this.stock.filter(item => item.is_selected);
            this.stock = this.stock.filter(item => !item.is_selected);
            try {
                const response = await axios.post(appConfig.urlDeleteStockDetail, toDelete, {
                    headers: appConfig.headers
                });
                const data = response.data;
                console.dir(data);
            } catch (error) {
                console.error('Error al eliminar el stock seleccionado:', error);
                alert(`Hubo un error al eliminar el stock seleccionado: ${error.message}`);
            }
        },
        selectAllSuppliers(select = false) {
            this.suppliers = this.suppliers.map(item => ({ ...item, is_selected: select }));
            this.filterCategories();
        },
        selectAllColors(select = false) {
            this.colors = this.colors.map(item => ({ ...item, is_selected: select }));
            this.filterCategories();
        },
        selectAllLengths(select = false) {
            this.lengths = this.lengths.map(item => ({ ...item, is_selected: select }));
            this.filterCategories();
        },
        selectAllBoxModels(select = false) {
            this.boxModels = this.boxModels.map(bm => ({ ...bm, is_selected: select }));
            this.filterCategories();
        },
        getSelection() {
            return this.stock.filter(
                item => item.is_selected).map(i => ({ ...i, confirm_delete: false, is_selected: false })
            );
        },
        stockToText() {
            const now = new Date();
            this.stockText = 'Disponibilidad KosmoFlowers ' + now.toLocaleDateString() + '\n';
            let selected = this.stock.filter(item => item.is_selected);

            selected.forEach(item => {
                const checkRelation = (item) => {
                    if (!this.selectedCustomer) return true;
                    const parnters = this.selectedCustomer.related_partners.map(p => p.id);
                    return parnters.includes(item.partner.id);
                };

                if (checkRelation(item)) {
                    const totalStem = item.box_items.reduce((acc, subItem) => acc + subItem.qty_stem_flower, 0);
                    let line_text = `#${item.partner.id} ${item.quantity}${item.box_model} ${totalStem}`;

                    const groupedBoxItems = Object.values(
                        item.box_items.reduce((acc, subItem) => {
                            const key = `${subItem.product_variety}-${subItem.length}`;
                            if (!acc[key]) {
                                acc[key] = { ...subItem };
                            } else {
                                acc[key].qty_stem_flower += subItem.qty_stem_flower;
                            }
                            return acc;
                        }, {})
                    );

                    let costText = '';
                    let currentVariety = null;
                    groupedBoxItems.forEach(subItem => {
                        let cost = parseFloat(subItem.stem_cost_price) + parseFloat(subItem.margin);
                        cost = cost.toFixed(2);

                        if (subItem.product_variety !== currentVariety) {
                            line_text += ` ${subItem.product_variety}`;
                            currentVariety = subItem.product_variety;
                        }
                        
                        line_text += ` ${subItem.length}X${subItem.qty_stem_flower}`;
                        if (subItem.stem_cost_price){
                            costText += ` $${cost}`;
                        }
                    });

                    line_text += costText;
                    this.stockText += line_text + `\n`;
                }
            });
        },
        updateValues(newValue, column) {
            let box_items = [];
            this.stock.forEach(stockItem => {
                if (stockItem.is_selected) {
                    stockItem.box_items.forEach(currentItem => {
                        if(this.checkFilter(currentItem)) {
                            currentItem[column] = newValue;
                            box_items.push(currentItem);
                        }
                    });
                };
            });
            this.updateStockDetail(box_items);
        },
        checkFilter(currentItem) {
            let isVerified = false;
            const selectedLengths = this.lengths.filter(item => item.is_selected).map(item => item.name);
            const length = currentItem.length;
            
            if (selectedLengths.length > 0) {
                if (selectedLengths.includes(length)) {
                    isVerified = true;
                } else {
                    isVerified = false;
                }
            }
            return isVerified;
        },
        formatNumber(num) {
            if (num === null || num === undefined) return '0.00';
            const base_num = parseFloat(num);
            if (isNaN(base_num)) return '0.00';
            const parts = base_num.toString().split(".");
            const integerPart = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
            const decimalPart = parts.length > 1 ? "." + parts[1].slice(0, 2) : ".00";
            return integerPart + decimalPart;
        },
    },
});