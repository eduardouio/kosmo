const app = Vue.createApp({
    data(){
        return {
          product:products,
          partners:partners,
          urlPost:urlPost,
          csrftoken:csrfToken,
          show_form:true,
          disponibility:null,
          stock: {
            partner:null,
            date: new Date().toISOString().split('T')[0],
            stock_text: '',
          },
        }
    },
    methods:{
        selectPartner($event){
            this.stock.partner = this.partners.find(
                partner => partner.id == $event.target.value
            );
        },
        processText($event){
            console.log($event.target.value);
        },
        sendData(){
            this.show_form = false;
            fetch(this.urlPost, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrftoken,
                },
                body: JSON.stringify(this.stock),
            }).then(
                response => response.json()
            ).then(data => {
                console.log('Success:', data);
                this.disponibility = data;
            })

        },
        loadData(){
            this.show_form = false;
            if(!this.disponibility){
                this.show_form = true;
                console.log('No data to load');
                return;
            }
        }
    },
    mounted(){
        console.log('Stock Entry App is mounted');
    },
    computed:{

    }
});
app.config.compilerOptions.delimiters = ['[[', ']]'];
const vm = app.mount('#app');