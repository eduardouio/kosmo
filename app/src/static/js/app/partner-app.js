const app = Vue.createApp({
    data() {
        return {
            all_supliers: all_supliers
        }
    },
    methods: {},
    mounted() {},
    computed: {},
});
app.config.compilerOptions.delimiters = ['[[', ']]'];
const vm = app.mount('#app');