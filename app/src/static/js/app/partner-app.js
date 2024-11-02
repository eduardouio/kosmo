const app = Vue.createApp({
    data() {
        return {
            url: urlPOST,
            csrf_token: csrf_token,
            all_supliers: all_supliers,
        }
    },
    methods: {
        changeItemStatus(item) {
            this.all_supliers = this.all_supliers.map((element) => {
                if (element.id === item.id) {
                    element.selected = !element.selected;
                }
                return element;
            });
            this.updateParentPartner(item);
        },
        updateParentPartner(partnerUpdated) {
            console.log('llamamos al updater del server');
            fetch(this.url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrf_token,
                },
                body: JSON.stringify(partnerUpdated),
            })
                .then((response) => response.json())
                .then((data) => {
                    console.log(data);
                });
        },
    },
    mounted() {
        console.log('App Vue Iniciada!');
    },
    computed: {},
});
app.config.compilerOptions.delimiters = ['[[', ']]'];
const vm = app.mount('#app');