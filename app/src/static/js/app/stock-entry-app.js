const app = Vue.createApp({
    data(){
        return {
          product:products,
          partners:partners,
          urlPost:urlPost,
          csrftoken:csrfToken,
          show_form:true,
          disponibility:null,
          partner:null,
          stock: {
            id_partner:null,
            date: new Date().toISOString().split('T')[0],
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
        },
        processText($event){
            console.log($event.target.value);
        },
        sendData() {
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
                this.disponibility = JSON.parse(data['data']);
                console.dir(this.disponibility);
                this.showResults();
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        },        
        showResults(){
            this.show_form = false;
            
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