const app = Vue.createApp({
    data(){
        return {
          product:products,
          partners:partners,
          urlPost:urlPost,
          csrftoken:csrfToken,
          show_form:true,       
          show_message:false,
          message: '',
          disponibility:null,
          partner:null,
          stock: {
            replace: false,
            id_partner:null,
            id_stock_day: stockDaiID,
            stock_text: '',
          },
        }
    },
    methods:{
        selectPartner($event){
            this.partner = this.partners.find(
                partner => partner.name == $event.target.value
            );
            this.stock.id_partner = this.partner.id;
            if (this.partner.registered_stock){
                this.show_message = true;
                this.message = 'El socio ya tiene un stock registrado, lo puede reemplazar o anexar, por defecto se anexará';
            }
        },
        setReplace(){
            this.show_message = true;
            this.stock.replace = !this.stock.replace;
            if (this.stock.replace){
                this.message = 'Se reemplazará el stock anterior';
            }
            this.message = 'Se Anejará el stock al anterior';

        },
        sendData() {
            if (this.stock.id_partner  == null || this.stock.stock_text == '') {
                this.show_message = true;
                this.message = 'Debe seleccionar un socio e ingresar el texto del stock';
                return;
            }
            this.show_form = false;
            fetch(this.urlPost, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrftoken,
                },
                body: JSON.stringify(this.stock),
            })
            .then((response) => response.json())
            .then((data) => {
                this.disponibility = data;
                this.show_form = false;
                console.log('Success:', data);
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        },        
        formatCurrency(number){
            return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'USD' }).format(number);
        },
    },
    mounted(){
        console.log('Stock Entry App is mounted');
    },
    computed:{

    }
});
app.config.compilerOptions.delimiters = ['[[', ']]'];
const vm = app.mount('#app');